# OpenALD Feather RP2040 v1.0 — firmware notes

There is no firmware in this package yet. These notes cover what firmware has to know about this hardware. Nothing has been tested on hardware.

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
* A = D24 (GP24), B = D25 (GP25), push = D4 (GP6). Common goes to GND, so set `INPUT_PULLUP` on all three.
* The board has no RC filter. Debounce in firmware: a quadrature state table with 1–2 ms sampling, or PIO.
* Suggested behaviour, the same as the single-board radio: turn changes the volume, push and turn tunes, a long press runs seek.

## Battery voltage (the Feather has no battery monitor)
* A0 (GP26) reads VBAT/2 through 220 k / 220 k (R1/R2) with 100 nF (C1).
* `vbat = adc_raw / 4095 * 3.3 * 2`. With Arduino `analogReadResolution(12)`, average 8–16 samples.
* The source impedance is 110 k. C1 holds the node during sampling, so read no faster than about every 10 ms.
* Divider drain is about 9.5 µA, always on, including when switched OFF.
* Rough charge levels at rest: 4.15 V or more is full, about 3.7 V is half, 3.4 V or less is low. Shut down cleanly below about 3.3 V. A protected cell cuts off near 2.5–2.8 V anyway.

## Power switch / EN behaviour
* OFF means EN is held low: the 3.3 V regulator is off, along with the RP2040, the FM module and the NeoPixel.
* **Off-state drain**: the Feather's EN pull-up (10 k to the battery/USB rail) conducts about 0.4 mA while EN is grounded. That is roughly 9–10 % of a 3500 mAh cell per month.
  Optional mod: replace that pull-up with 100 k to cut the drain to about 40 µA. Total off drain is then about 50 µA including the divider.
* Charging works with the switch in either position. The MCP73831 is powered from VBUS and charges at **200 mA**, so a 3500 mAh cell takes about **18–20 h** from empty. That is slow, and it is a property of the Feather.
* STAT (on J1.7) can also go to a spare GPIO through a 100 k resistor if firmware should know the charge state. That is not done on this board.

## LEDs firmware can use
* Red D13 (GP13) and the NeoPixel (GP16) show through the top windows near the USB end. These are hidden while docked.
* The CHG/FULL mirror LEDs on the controls board are hardware-only and visible while docked.
