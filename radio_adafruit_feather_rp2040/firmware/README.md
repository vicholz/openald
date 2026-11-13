# OpenALD Feather RP2040 v1.0 — firmware

> **Compiles, never run on hardware.** Written from the datasheets and `../docs/wiring_diagram.png`. Expect to debug it on the first build.

* `openald_feather/openald_feather.ino` — main sketch; `openald_feather/rda5807m.h` — small RDA5807M register driver (no radio library needed).
* Toolchain: Arduino with Earle Philhower's **arduino-pico** core (board **Adafruit Feather RP2040**, FQBN `rp2040:rp2040:adafruit_feather`) and the **Adafruit NeoPixel** library. Compile-checked with arduino-cli 1.6.0, arduino-pico 6.3.2, Adafruit NeoPixel 1.15.5.
* `./build.sh` installs the core + library if needed and compiles; `./build.sh /dev/ttyACM0` also uploads.
* `openald_feather_v1.0.uf2` — prebuilt image. To flash: switch the radio ON, double-tap RESET through the pin-hole in the top (or hold BOOT while plugging in USB, case open), then copy the .uf2 to the **RPI-RP2** drive.

## Pins (match `../docs/wiring_diagram.png` and `../docs/pin_map.md`)
| Function | Feather silk | GPIO used in the sketch |
|---|---|---|
| Wheel A / B | D24 / D25 | 24 / 25 (pull-ups) |
| Wheel push S (low = pressed) | D4 | **6** |
| Battery VBAT/2 (220k/220k + 100 nF) | A0 | 26 |
| RDA5807M I2C | STEMMA QT | SDA 2 / SCL 3 (`Wire`, i2c1) |
| Battery / status display | NeoPixel (on board) | 16 |

## Behaviour
| Action | Result |
|---|---|
| Turn | volume 0 (mute) … 15 |
| Short press (< 0.5 s, no turn) | battery level on the NeoPixel for 3 s |
| Hold ≥ 0.5 s (no turn) | seek up (blue blink while seeking; turning while held cancels it and tunes) |
| Push and turn | tune ± 200 kHz per detent (`TUNE_STEP_10K`), wraps 87.0 ↔ 108.0 MHz |
| Power on | radio restarts on the last saved frequency/volume; battery level shown for 3 s |

Battery colours: green ≥ 3.90 V · yellow 3.60–3.90 · orange 3.40–3.60 · red slow blink 3.30–3.40 · red fast blink < 3.30 (50 mV hysteresis). Below 3.30 V a 50 ms red flash every 10 s; below 3.25 V the radio is powered down until the cell reads above 3.45 V. Magenta blink = no RDA5807M answered at I2C 0x11. Without the divider (A0 reads < 1 V) the battery features are skipped.

Settings at the top of the sketch: de-emphasis (`DEEMPH_50US`, default 75 µs for the Americas), tune step, default station/volume, `VBAT_CAL`, NeoPixel brightness, battery thresholds.

**Not possible on this hardware** (unlike the single board): checking the battery with the power switch OFF (EN keeps the regulator off), and showing the charge state (STAT only drives the optional LEDs). USB serial prints a log at 115200 baud when a computer is attached.
