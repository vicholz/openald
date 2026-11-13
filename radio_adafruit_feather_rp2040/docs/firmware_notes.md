# OpenALD Feather RP2040 v1.0 — firmware notes

**Firmware now exists:** `firmware/openald_feather/` (Arduino, arduino-pico core; build with `firmware/build.sh`, prebuilt `firmware/openald_feather_v1.0.uf2`). It compiles with arduino-pico 6.3.2 + Adafruit NeoPixel 1.15.5 for "Adafruit Feather RP2040"; it has **not** been run on hardware. These notes cover what firmware has to know about this hardware; the sketch follows them. Nothing has been tested on hardware.

Why Arduino rather than CircuitPython: the same toolchain style as the single board (MiniCore/Arduino), a 1 ms timer-interrupt wheel poll that is not disturbed by the main loop, flash persistence of frequency/volume, and a single .uf2 to flash.

## Toolchains
* **Arduino**: Earle Philhower's *Raspberry Pi Pico/RP2040* core. Select the board "Adafruit Feather RP2040". `Wire` is the STEMMA QT port on SDA = GP2 and SCL = GP3.
* **CircuitPython**: the "Adafruit Feather RP2040" build. Use `i2c = board.STEMMA_I2C()`, `board.D24`, `board.D25`, `board.D4` and `board.A0`.
* To get into the bootloader, double-tap RESET through the pin-hole in the top, or use the 1200-baud touch from the Arduino IDE. The right-angle BOOT button (rev D+) is not reachable with the case closed.

## RDA5807M (FM module on the STEMMA QT port)
* I2C addresses: **0x10** for sequential access (writes start at register 0x02 and reads at 0x0A) and **0x11** for random register access. Both appear on a scan.
* The module runs from the Feather's 3.3 V rail, which EN switches. Every power-on is a cold start, so firmware must re-initialise the chip: soft reset, enable, band and spacing, volume, then tune.
* **Pull-ups**: we don't know whether your module has SDA/SCL pull-ups. If an I2C scan finds nothing, add 4.7 k from SDA and from SCL to 3V3 on the module.
* The headphone cable is the antenna, as is normal for RDA5807 modules.
* Volume is the 4-bit register value, 0–15.

## Thumbwheel (Mitsumi SIQ-02FVS3)

Paper-verified against the Mitsumi SIQ series datasheet ([LCSC copy of the official PDF](https://datasheet.lcsc.com/datasheet/pdf/7bff72617d5a3503f5ed21ab02a77dea.pdf?productCode=C2925423)). Nothing here has been tested on hardware.

* **Wiring:** A = D24 (GP24), B = D25 (GP25), push = D4 (GP6), common C = GND, wired straight from the wheel's tabs to the Feather (no controls board; see `pin_map.md`). These are ordinary Feather RP2040 GPIOs (not QSPI, and not the STEMMA QT I2C pins GP2/GP3). They all support pin interrupts and PIO. Enable `INPUT_PULLUP` in `setup()` before you read them: at reset the RP2040 defaults these pads to pull-down. There is no RC filter and no ESD diode, so debounce in firmware (the datasheet does not specify bounce time).
* **Electrical:** the RP2040 internal pull-ups are 50–80 kΩ (RP2040 datasheet, GPIO pad characteristics), so a closed contact draws about 41–66 µA at 3.3 V, under the 0.5 mA / 5 V DC rating. The datasheet does not specify a minimum wetting current. Do not also configure D24/D25 as UART1 or I2C0; `Wire` / `board.STEMMA_I2C()` already uses GP2/GP3.
* **Decode:** 15 detents, one quadrature cycle (four valid Gray-code transitions) per detent, A leading B for clockwise. Count **one step per detent** (accumulate ±4), not one step per edge. A 1 ms state-table poll debounces; PIO quadrature is also fine.
* Suggested behaviour, the same as the single-board radio: turn changes the volume, push and turn tunes, a long press runs seek.

Example (Earle Philhower Arduino-Pico, board "Adafruit Feather RP2040"). arduino-pico pin numbers are GPIO numbers, so use 24 / 25 / **6** (silk D4 is GP6, not GPIO 4; an earlier version of this example wrongly used 4). The full sketch runs this from a 1 ms `add_repeating_timer_ms` callback. Call `encoder_setup()` from `setup()`, and `encoder_poll()` every 1 ms.

```cpp
// D24=ENCA (GP24), D25=ENCB (GP25), D4=ENCSW (GP6). Common = GND.
const uint8_t PIN_A = 24, PIN_B = 25, PIN_SW = 6;   // arduino-pico pin numbers are GPIO numbers: D4 = GP6
static const int8_t ENC_TAB[16] = {
  0,-1,+1,0, +1,0,0,-1, -1,0,0,+1, 0,+1,-1,0
};
static uint8_t enc_prev;
static int8_t  enc_accum;
static int8_t  enc_step;        // +1 / -1 once per detent; consume in the main loop
static uint8_t sw_hist, sw_down;
static uint16_t sw_ms;

void encoder_setup() {
  pinMode(PIN_A, INPUT_PULLUP);
  pinMode(PIN_B, INPUT_PULLUP);
  pinMode(PIN_SW, INPUT_PULLUP);
  enc_prev = (digitalRead(PIN_A) ? 2 : 0) | (digitalRead(PIN_B) ? 1 : 0);
}

void encoder_poll() {            // call every 1 ms
  uint8_t now = (digitalRead(PIN_A) ? 2 : 0) | (digitalRead(PIN_B) ? 1 : 0);
  enc_accum += ENC_TAB[(enc_prev << 2) | now];
  enc_prev = now;
  if (enc_accum >= 4)  { enc_step += 1; enc_accum = 0; }
  if (enc_accum <= -4) { enc_step -= 1; enc_accum = 0; }

  sw_hist = (sw_hist << 1) | (digitalRead(PIN_SW) ? 1 : 0);
  if (!sw_down && (sw_hist & 0x1F) == 0x00) { sw_down = 1; sw_ms = 0; }      // 5 ms low
  if (sw_down) {
    if (sw_ms < 60000) sw_ms++;
    if ((sw_hist & 0x1F) == 0x1F) {         // released
      // sw_ms < 500: short press; sw_ms >= 500: already treated as long press
      sw_down = 0;
    } else if (sw_ms == 500) {
      // long press: start seek
    }
  }
}
```

## Battery voltage (the Feather has no battery monitor)
* A0 (GP26) reads VBAT/2 through an inline 220 k / 220 k divider with 100 nF from A0 to GND (hand-wired in heat-shrink; see `pin_map.md`). Without the divider there is no battery reading.
* `vbat = adc_raw / 4095 * 3.3 * 2`. With Arduino `analogReadResolution(12)`, average 8–16 samples.
* The source impedance is 110 k. The 100 nF capacitor holds the node during sampling, so read no faster than about every 10 ms.
* Divider drain is about 9.5 µA, always on, including when switched OFF.
* Rough charge levels at rest: 4.15 V or more is full, about 3.7 V is half, 3.4 V or less is low. Shut down cleanly below about 3.3 V. A protected cell cuts off near 2.5–2.8 V anyway.

## Power switch / EN behaviour
* OFF (SS-12F16 knob toward the USB end) means EN is held low: the 3.3 V regulator is off, along with the RP2040, the FM module and the NeoPixel.
* **Off-state drain**: the Feather's EN pull-up (10 k to the battery/USB rail) conducts about 0.4 mA while EN is grounded. That is roughly 9–10 % of a 3500 mAh cell per month.
  Optional mod: replace that pull-up with 100 k to cut the drain to about 40 µA. Total off drain is then about 50 µA including the divider.
* Charging works with the switch in either position. The MCP73831 is powered from VBUS and charges at **200 mA**, so a 3500 mAh cell takes about **18–20 h** from empty. That is slow, and it is a property of the Feather.
* STAT (the optional fine-wire tap) can also go to a spare GPIO through a 100 k resistor if firmware should know the charge state. That is not done here.

## LEDs firmware can use
* Red D13 (GP13) and the NeoPixel (GP16) show through the top windows near the USB end. These are hidden while docked.
* The firmware lights the NeoPixel only for the battery level: 5 s at power-on and 3 s after a short press; it is cleared (off) at all other times and D13 stays off. The NeoPixel (WS2812B-3535, LED1) has VDD tied to +3V3 in Adafruit's board file, with **no power-enable pin** (GPIO 20 is MISO here), so it can't be powered down; a dark WS2812B draws ~1 mA typ. while the switch is ON (not measured).
* The optional 3 mm CHG/FULL LEDs in the top half are hardware-only (driven by VBUS and STAT) and visible while docked.
