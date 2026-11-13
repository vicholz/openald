// OpenALD Feather RP2040 v1.0 - firmware (Arduino, Earle Philhower "Raspberry Pi Pico/RP2040" core,
// board "Adafruit Feather RP2040"). Needs the "Adafruit NeoPixel" library.
//
// NOT TESTED ON HARDWARE. Written against the datasheets and the wiring in ../../docs/wiring_diagram.png.
//
// Pin map (must match docs/wiring_diagram.* and docs/pin_map.md; numbers are RP2040 GPIOs = arduino-pico pin numbers):
//   GP24 (silk D24) wheel A      INPUT_PULLUP, common C = GND
//   GP25 (silk D25) wheel B      INPUT_PULLUP
//   GP6  (silk D4)  wheel S/push INPUT_PULLUP, LOW = pressed
//   GP26 (silk A0)  VBAT/2 from the 220k/220k divider (100 nF to GND)
//   GP2 / GP3       STEMMA QT SDA / SCL -> RDA5807M (Wire = i2c1 on this board)
//   GP16            on-board NeoPixel (battery level / status)
//   GP13            on-board red LED (unused, kept off)
//   EN              SS-12F16 middle lug (hardware power switch; firmware never sees it)
//   STAT tap, VBUS  optional charge LEDs, hardware only (firmware cannot read them)
//
// Wheel behaviour (mirrors the single-board radio as far as the Feather hardware allows):
//   turn                      volume (0 = mute .. 15)
//   short press (<500 ms)     battery level on the NeoPixel for 3 s
//   hold >= 500 ms, no turn   seek up to the next station
//   push and turn             tune +/- TUNE_STEP_10K per detent (no battery check, no seek)
// Differences from the single board: the level is shown as a NeoPixel colour instead of a 3-LED bar, and there is no
// battery check with the power switch OFF (EN holds the Feather's 3.3 V regulator off, so nothing can run).
// The NeoPixel and D13 sit by the USB end and are hidden while docked.

#include <Wire.h>
#include <EEPROM.h>
#include <Adafruit_NeoPixel.h>
#include "pico/time.h"
#include "hardware/gpio.h"
#include "rda5807m.h"

// ---------------- pins ----------------
const uint8_t PIN_ENC_A = 24, PIN_ENC_B = 25, PIN_ENC_SW = 6;   // D24, D25, D4 (D4 is GP6 on this board, not GPIO 4)
const uint8_t PIN_VBAT = 26;                                      // A0
const uint8_t PIN_PIXEL = 16, PIN_RED_LED = 13;

// ---------------- settings (edit) ----------------
const bool     DEEMPH_50US = false;          // false = 75 us (Americas, Korea); true = 50 us (Europe, Asia, Australia)
const uint16_t TUNE_STEP_10K = 20;           // 200 kHz per detent (US odd-tenth channels); 10 = 100 kHz
const uint16_t DEFAULT_FREQ_10K = 9910;      // 99.1 MHz on first boot
const uint8_t  DEFAULT_VOLUME = 6;
const float    VBAT_CAL = 1.000f;            // multiply the reading by this after checking against a meter
const bool     SHOW_BATTERY_AT_POWER_ON = true;  // the Feather can't check the battery with the switch OFF, so flash it at power-on
const uint8_t  PIXEL_BRIGHTNESS = 24;        // 0..255; the NeoPixel is very bright at full power
const uint32_t SAVE_DELAY_MS = 5000;         // write frequency/volume to flash this long after the last change
const float    V_MUTE = 3.25f, V_RESUME = 3.45f;  // low-battery cut-off (radio powered down) and resume threshold

// ---------------- wheel (1 ms timer poll; state table from the single-board spec) ----------------
static const int8_t ENC_TAB[16] = {0, -1, +1, 0, +1, 0, 0, -1, -1, 0, 0, +1, 0, +1, -1, 0};
static volatile int8_t  enc_step;            // +1 / -1 per detent (consumed by loop)
static volatile bool    sw_down;             // debounced "held"
static volatile bool    battery_req, seek_req;
static uint8_t  enc_prev, sw_hist, sw_turned;
static int8_t   enc_accum;
static uint16_t sw_ms;
static repeating_timer_t wheel_timer;

static bool wheel_poll(repeating_timer_t *) {
  uint8_t now = (gpio_get(PIN_ENC_A) ? 2 : 0) | (gpio_get(PIN_ENC_B) ? 1 : 0);
  enc_accum += ENC_TAB[(enc_prev << 2) | now];
  enc_prev = now;
  int8_t step = 0;
  if (enc_accum >= 4)  { step = +1; enc_accum = 0; }
  if (enc_accum <= -4) { step = -1; enc_accum = 0; }
  if (step) enc_step += step;

  sw_hist = (sw_hist << 1) | (gpio_get(PIN_ENC_SW) ? 1 : 0);      // 1 = released (pull-up), 0 = pressed
  if (!sw_down && (sw_hist & 0x1F) == 0x00) { sw_down = true; sw_ms = 0; sw_turned = 0; }   // 5 ms pressed
  if (sw_down) {
    if (step) sw_turned = 1;                                       // push-and-turn = tune
    if (sw_ms < 60000) sw_ms++;
    if ((sw_hist & 0x1F) == 0x1F) {                                // 5 ms released
      if (sw_ms < 500 && !sw_turned) battery_req = true;
      sw_down = false;
    } else if (sw_ms == 500 && !sw_turned) {
      seek_req = true;
    }
  }
  return true;
}

// ---------------- battery ----------------
// VBAT = ADC / 4095 * 3.3 V * 2 (220k / 220k). Source impedance 110k, so the 100 nF cap does the sampling: read at most every ~10 ms.
float read_vbat() {
  uint32_t sum = 0;
  for (int i = 0; i < 16; i++) sum += analogRead(PIN_VBAT);
  return (sum / 16.0f) / 4095.0f * 3.3f * 2.0f * VBAT_CAL;
}
// Bands as on the single board: 3 = >=3.90, 2 = 3.60-3.90, 1 = 3.40-3.60, 0 = 3.30-3.40 (slow blink), -1 = <3.30 (fast blink).
// 50 mV hysteresis: a band only changes when the voltage leaves it by more than 50 mV.
int battery_band(float v) {
  static int band = 99;
  const float edge[4] = {3.30f, 3.40f, 3.60f, 3.90f};
  int raw = -1;
  for (int i = 0; i < 4; i++) if (v >= edge[i]) raw = i;
  if (band == 99 || raw > band + 1 || raw < band - 1) band = raw;
  else if (raw == band + 1 && v >= edge[raw] + 0.05f) band = raw;
  else if (raw == band - 1 && v < edge[band] - 0.05f) band = raw;
  return band;
}

// ---------------- state ----------------
Adafruit_NeoPixel pixel(1, PIN_PIXEL, NEO_GRB + NEO_KHZ800);
rda::Radio radio;
bool radio_ok = false, low_batt_off = false;
uint16_t freq10k = DEFAULT_FREQ_10K;
uint8_t volume = DEFAULT_VOLUME;
uint32_t show_until = 0, dirty_at = 0, last_vcheck = 0, last_lowflash = 0, seek_started = 0;
bool dirty = false;
float vbat = 4.0f;

struct Saved { uint32_t magic; uint16_t freq10k; uint8_t volume; uint8_t check; };
const uint32_t MAGIC = 0x0A1D1000;   // "OpenALD v1.0"

void load_settings() {
  Saved s; EEPROM.get(0, s);
  if (s.magic == MAGIC && s.check == (uint8_t)(s.freq10k ^ (s.freq10k >> 8) ^ s.volume ^ 0x5A) &&
      s.freq10k >= rda::BAND_LO_10K && s.freq10k <= rda::BAND_HI_10K && s.volume <= 15) {
    freq10k = s.freq10k; volume = s.volume;
  }
}
void save_settings() {
  Saved s{MAGIC, freq10k, volume, (uint8_t)(freq10k ^ (freq10k >> 8) ^ volume ^ 0x5A)};
  EEPROM.put(0, s); EEPROM.commit();                 // one 4 KB flash sector erase per save; saves are debounced
  dirty = false;
}
void mark_dirty() { dirty = true; dirty_at = millis(); }

void pixel_set(uint8_t r, uint8_t g, uint8_t b) {
  static uint32_t last = 0xFFFFFFFF;
  uint32_t c = pixel.Color(r, g, b);
  if (c == last) return;                             // only push changes to the pixel
  last = c; pixel.setPixelColor(0, c); pixel.show();
}

// Battery display: green / yellow / orange solid, red slow (1 Hz) or fast (4 Hz) blink.
void show_battery(uint32_t now) {
  int band = battery_band(vbat);
  switch (band) {
    case 3:  pixel_set(0, 255, 0); break;
    case 2:  pixel_set(200, 160, 0); break;
    case 1:  pixel_set(255, 60, 0); break;
    case 0:  pixel_set(((now / 500) & 1) ? 255 : 0, 0, 0); break;
    default: pixel_set(((now / 125) & 1) ? 255 : 0, 0, 0); break;
  }
}

void start_battery_display() {
  vbat = read_vbat();                    // measure with the pixel off (as on the single board)
  show_until = millis() + 3000;
  Serial.printf("battery %.2f V (band %d)\n", vbat, battery_band(vbat));
}

void radio_start() {
  static bool wire_up = false;
  if (!wire_up) { Wire.setSDA(2); Wire.setSCL(3); Wire.begin(); wire_up = true; }   // STEMMA QT = i2c1
  Wire.setClock(100000);
  delay(50);                                         // module power-up after EN switched the 3.3 V rail on
  radio_ok = radio.begin(DEEMPH_50US);
  if (radio_ok) { radio.setVolume(volume); radio.tune(freq10k); }
  Serial.printf("RDA5807M %s, %u.%u MHz, volume %u\n", radio_ok ? "found" : "NOT FOUND at 0x11 (check wiring / pull-ups)",
                freq10k / 100, (freq10k / 10) % 10, volume);
}

void setup() {
  pinMode(PIN_RED_LED, OUTPUT); digitalWrite(PIN_RED_LED, LOW);
  pinMode(PIN_ENC_A, INPUT_PULLUP);                  // RP2040 pads default to pull-down: enable the pull-ups first
  pinMode(PIN_ENC_B, INPUT_PULLUP);
  pinMode(PIN_ENC_SW, INPUT_PULLUP);
  analogReadResolution(12);
  Serial.begin(115200);                              // USB CDC (only does anything with a computer attached)
  pixel.begin(); pixel.setBrightness(PIXEL_BRIGHTNESS); pixel_set(0, 0, 0);
  EEPROM.begin(256);
  load_settings();
  enc_prev = (gpio_get(PIN_ENC_A) ? 2 : 0) | (gpio_get(PIN_ENC_B) ? 1 : 0);
  sw_hist = 0xFF;
  add_repeating_timer_ms(-1, wheel_poll, nullptr, &wheel_timer);

  vbat = read_vbat();
  if (vbat < V_MUTE && vbat > 1.0f) low_batt_off = true;   // < 1 V = divider not fitted: run anyway
  if (!low_batt_off) radio_start();
  if (SHOW_BATTERY_AT_POWER_ON) start_battery_display();
}

void loop() {
  uint32_t now = millis();

  // --- wheel events ---
  noInterrupts();
  int8_t steps = enc_step; enc_step = 0;
  bool held = sw_down, breq = battery_req, sreq = seek_req;
  battery_req = seek_req = false;
  interrupts();

  if (breq) start_battery_display();
  if (radio_ok && !low_batt_off) {
    if (steps && held) {                             // push and turn: tune
      if (radio.seeking()) { radio.stopSeek(); freq10k = radio.frequency(); }
      int32_t f = (int32_t)freq10k + steps * (int32_t)TUNE_STEP_10K;
      if (f > rda::BAND_HI_10K) f = rda::BAND_LO_10K;         // wrap like a dial
      if (f < rda::BAND_LO_10K) f = rda::BAND_HI_10K;
      freq10k = f; radio.tune(freq10k); mark_dirty();
      Serial.printf("tune %u.%u MHz\n", freq10k / 100, (freq10k / 10) % 10);
    } else if (steps) {                              // turn: volume
      int v = constrain((int)volume + steps, 0, 15);
      if (v != volume) { volume = v; radio.setVolume(volume); mark_dirty(); }
      Serial.printf("volume %u\n", volume);
    }
    if (sreq) { radio.startSeek(true); seek_started = now; Serial.println("seek"); }
    if (radio.seeking()) {
      static uint32_t last_poll = 0;
      if (now - last_poll >= 20) {
        last_poll = now;
        if (radio.seekDone() || now - seek_started > 8000) {
          radio.stopSeek(); freq10k = radio.frequency(); mark_dirty();
          Serial.printf("seek -> %u.%u MHz (RSSI %u)\n", freq10k / 100, (freq10k / 10) % 10, radio.rssi());
        }
      }
    }
  }

  // --- battery watch (every 2 s, not while the pixel shows something) ---
  if (now - last_vcheck >= 2000 && now >= show_until) {
    last_vcheck = now;
    float v = read_vbat();
    if (v > 1.0f) {                                  // divider fitted
      vbat = v;
      if (!low_batt_off && v < V_MUTE) {
        low_batt_off = true;
        if (radio_ok) radio.powerDown();
        Serial.printf("battery %.2f V < %.2f V: radio off\n", v, V_MUTE);
      } else if (low_batt_off && v > V_RESUME) {     // e.g. charging with the switch on
        low_batt_off = false;
        radio_start();
      }
    }
  }

  // --- pixel ---
  if (now < show_until) {
    show_battery(now);
  } else if (radio.seeking()) {
    pixel_set(0, 0, ((now / 150) & 1) ? 120 : 0);    // blue blink while seeking
  } else if (!radio_ok && !low_batt_off) {
    pixel_set(((now / 1000) & 1) ? 120 : 0, 0, ((now / 1000) & 1) ? 120 : 0);   // magenta 0.5 Hz: radio not found
  } else if (vbat < 3.30f && vbat > 1.0f) {          // very low: 50 ms red flash every 10 s even without a press
    if (now - last_lowflash >= 10000) last_lowflash = now;
    pixel_set(now - last_lowflash < 50 ? 255 : 0, 0, 0);
  } else {
    pixel_set(0, 0, 0);
  }

  // --- persist ---
  if (dirty && now - dirty_at >= SAVE_DELAY_MS && !radio.seeking()) save_settings();

  delay(2);
}
