# OpenALD Feather RP2040 v1.0 — pin map (t116u: bottom-end USB-C, header-pad wiring)

Nothing here has been hardware-validated yet. There is no PCB: the wheel, the switch, the FM module, the battery and the divider are wired straight to the Feather's header pads (28–30 AWG silicone wire, ~120 mm per lead). Since t116u (2026-11-24) the Feather lies flat at the bottom end and **its own USB-C is the charge / dock port**: there is no USB-C breakout and no Schottky diode any more. The JST battery socket and the STEMMA QT socket stay **empty** (a plug in either would hit the end wall or the wheel).

## Feather RP2040 (Adafruit #4884) connections

| Feather pad (silkscreen) | Header | RP2040 GPIO | Goes to | Wire | Notes |
|---|---|---|---|---|---|
| **D24** | JP1.8 | GP24 | Wheel **A** | 30 AWG | Internal pull-up. Debounced in firmware: no RC filter. |
| **D25** | JP1.7 | GP25 | Wheel **B** | 30 AWG | Internal pull-up. |
| **D4** | JP1.1 | GP6 | Wheel **S** (push switch) | 30 AWG | Internal pull-up. Active low. |
| **3V3** | JP1.14 | — | FM module **VCC** | 28–30 AWG | Switched by EN, so the radio turns off with the switch. |
| **GND** | JP1.13 (the only GND pad) | — | GND splice (right channel) → wheel **C**, divider bottom, 100 nF, and one wire from the left-channel splice (FM **GND**, switch OFF-end lug, battery **−**) | 28 AWG | Heat-shrunk splices. |
| **A0** | JP1.12 | GP26 / ADC0 | Divider middle (220 k / 220 k junction, 100 nF to GND) | 30 AWG | VBAT/2. |
| **SDA** | JP3.12 | GP2 | FM module **SDA** | 30 AWG | I2C1 (`Wire`), 100 kHz. |
| **SCL** | JP3.11 | GP3 | FM module **SCL** | 30 AWG | |
| **EN** | JP3.2 | — (enables the AP2112 3.3 V regulator) | Switch **middle lug** (common) | 28–30 AWG | Knob toward the USB end (OFF) ties EN to GND: the 3.3 V rail, the RP2040, the FM module and the NeoPixel turn off. Knob toward the top end (ON) leaves EN open (the Feather's pull-up turns it on). |
| **BAT** (VBAT) | JP3.1 | — | 18650 holder **+** pin (the USB end) and the divider top (220 k) | 26–28 AWG (battery), 30 AWG (divider) | **Check polarity with a meter** before inserting the cell. Charging: the Feather's MCP73831 from its own USB-C (200 mA). |

Spare pins remain free: A1–A3, D5, D6, D9–D13, SCK, MOSI, MISO, TX and RX. The red LED is D13 / GP13 and the NeoPixel is GP16.

**Visible on-board LEDs (t116u):** the Feather lies components-up under the front face, so its **CHG** LED (amber, charging), its **red** LED and its **NeoPixel** (battery level) each sit under a light tunnel to a hole in the front face; the RESET button is under a pin-hole. In the charging dock the CHG hole is about 4 mm and the NeoPixel about 20 mm above the pocket floor, in the pocket's front window. The battery display stays on the NeoPixel (not moved to the front LEDs).

Unchanged GPIO assignment (A = D24, B = D25, push = D4, C = GND, switch common = EN, OFF = GND, divider on A0, I2C on GP2/GP3). Only the physical path changed.

Diagram: [`wiring_diagram.png`](wiring_diagram.png) / `.svg`. KiCad schematic: [`wiring_schematic/openald-feather-wiring.pdf`](wiring_schematic/openald-feather-wiring.pdf).

## Firmware pin table (`firmware/openald_feather/openald_feather.ino`)
arduino-pico uses RP2040 GPIO numbers as pin numbers, so the sketch uses the GP numbers, not the silk names.

| Signal (net) | Feather silk | RP2040 GPIO | Sketch constant | Mode | Wire to |
|---|---|---|---|---|---|
| ENC_A | D24 | 24 | `PIN_ENC_A = 24` | `INPUT_PULLUP` | wheel A |
| ENC_B | D25 | 25 | `PIN_ENC_B = 25` | `INPUT_PULLUP` | wheel B |
| ENC_SW (push, low = pressed) | D4 | **6** | `PIN_ENC_SW = 6` | `INPUT_PULLUP` | wheel S |
| VBAT_SENSE (VBAT / 2) | A0 | 26 (ADC0) | `PIN_VBAT = 26` | analog, 12 bit | 220k/220k divider middle, 100 nF to GND |
| SDA / SCL | SDA / SCL (JP3.12 / JP3.11) | 2 / 3 (i2c1, `Wire`) | `Wire.setSDA(2)`, `Wire.setSCL(3)` | I2C 100 kHz | RDA5807M SDA / SCL |
| NeoPixel | (on board) | 16 | `PIN_PIXEL = 16` | Adafruit_NeoPixel | — |
| Red LED | D13 (on board) | 13 | `PIN_RED_LED = 13` | output, kept low | — |
| EN | EN | — | — | hardware | switch middle lug |
| GND | GND (JP1.13) | — | — | — | GND splices: wheel C, divider bottom, 100 nF, FM GND, switch OFF lug, battery − |

## Mitsumi SIQ-02FVS3 tabs (as mounted)
The wheel sits on the right wall between the Feather and the FM module (dial centre case Y 58.7, dial 0.95 mm proud of the right face). Its four solder tabs face into the case; their order along the wall depends on which way the part is turned in the cradle — read them off your part (the datasheet land pattern reads "A PUSH COM B") and wire:

| Tab | To |
|---|---|
| **A** | D24 |
| **B** | D25 |
| **S** (push) | D4 |
| **C** (common) | GND (right splice) |

If A and B are swapped, the wheel just counts the other way; swap `PIN_ENC_A` / `PIN_ENC_B` in the firmware.

## SS-12F16 switch lugs (left wall, screwless groove at case Y 56; knob toward the top end = ON)
| Lug | To |
|---|---|
| Outer lug that connects to the middle when the knob is toward the **USB end (OFF)** — **check with a meter** | GND: left-channel splice (with the FM GND and the battery − lead), one wire to the Feather's GND pad |
| Middle lug (common) | EN |
| Other outer lug | not connected |

## Charge indication
No extra LEDs. The Feather's own CHG LED (MCP73831 STAT through a resistor) lights while charging and goes out when the cell is full or no USB power is present; it works with the power switch OFF (the charger runs from VBUS). It is visible through its front-face hole, also in the dock.
