# OpenALD Feather RP2040 v1.0 — pin map (direct-mount wheel and switch)

Nothing here has been hardware-validated yet. There is no controls PCB: the wheel, the switch and the optional parts are wired straight to the Feather (28–30 AWG silicone wire, ~120 mm per lead).

## Feather RP2040 (Adafruit #4884) connections

| Feather pin (silkscreen) | RP2040 GPIO | Goes to | Wire | Notes |
|---|---|---|---|---|
| **D24** | GP24 | Wheel **A** | 30 AWG | Use the internal pull-up. Debounce in firmware: no RC filter. |
| **D25** | GP25 | Wheel **B** | 30 AWG | Use the internal pull-up. |
| **D4** | GP6 | Wheel **S** (push switch) | 30 AWG | Use the internal pull-up. Active low. |
| **GND** (JP1.13, the only GND pin) | — | GND splice → wheel **C**, divider bottom, green LED cathode | 28 AWG to the splice | Heat-shrunk splice in the right channel. The switch OFF-end lug is on the same net via the battery black (−) lead (see below). |
| **EN** | — (enables the AP2112 3.3 V regulator) | Switch **middle lug** (common); wire runs down the left channel and up the battery-wire deck slot to JP3 | 28–30 AWG | Knob at the OFF (USB) end ties EN to GND: the 3.3 V rail, the RP2040 and the FM module turn off. Knob at the ON end leaves EN open (the Feather's own pull-up turns it on). |
| **BAT** (VBAT) | — | Divider top (220 k) | 28–30 AWG | Optional battery gauge. |
| **A0** | GP26 / ADC0 | Divider middle (220 k / 220 k junction, 100 nF to GND) | 30 AWG | VBAT/2. |
| **USB** (VBUS) | — | Optional: 1.5 k → red 3 mm LED anode | 30 AWG | About 2 mA while charging. |
| **STAT tap** (no pad) | — | Optional: red LED cathode, and 1.5 k → green LED anode | 32–36 AWG enamel or wire-wrap | Solder to the **STAT end of Feather R2** (the 10 k in series with the CHG LED), case position (25.92, 7.77). |
| **STEMMA QT** (JST SH 4-pin) | GP2 SDA / GP3 SCL, 3V3, GND | RDA5807M module VCC / GND / SDA / SCL | STEMMA QT cable #4210, one end cut | 3V3 is switched by EN, so the radio turns off with the switch. |
| **JST PH battery** | — | 18650 holder + / − | JST PH cable #261 (cut) | **Check polarity** against the "+" mark on the Feather before plugging in. Red goes to the holder + pin (the USB end). |

Spare pins remain free: A1–A3, D5, D6, D9–D13, SCK, MOSI, MISO, TX and RX. The red LED is D13 / GP13 and the NeoPixel is GP16. Both are visible through the top windows (undocked).

Unchanged from the controls-board version: the GPIO assignment (A = D24, B = D25, push = D4, C = GND, switch common = EN, OFF = GND, divider on A0). Only the physical path changed (wires instead of PCB traces), so `firmware_notes.md` applies as before.

## Mitsumi SIQ-02FVS3 tabs (as mounted)
The four solder tabs are on the body edge facing into the case (toward the FM module), in this order from the USB end toward the top end:

| Order (USB end → top end) | Tab | Case Y (mm) | To |
|---|---|---|---|
| 1 | **B** | 58.5 | D25 |
| 2 | **C** (common) | 61.0 | GND |
| 3 | **S** (push) | 64.0 | D4 |
| 4 | **A** | 66.5 | D24 |

Check the A/B/S/C markings printed on your part's datasheet drawing ("A PUSH COM B" in the land pattern) before soldering. If A and B are swapped, the wheel just counts the other way; swap `PIN_A` / `PIN_B` in firmware.

## SS-12F16 switch lugs (left wall, screwless groove; knob toward the top end = ON)
| Lug | To |
|---|---|
| Outer lug that connects to the middle when the knob is at the **OFF (USB) end** — normally the USB-side lug, **check with a meter** | GND: splice to the battery black (−) lead in the left channel (same net as Feather GND; the switch is on the opposite side from the Feather's only GND pin) |
| Middle lug (common) | EN |
| Other outer lug | not connected |

## Optional dock-visible charge LEDs (3 mm, in the top-half sockets)
MCP73831 STAT is push-pull: low while charging, high (VBUS) when charging is done, Hi-Z when the charger is off or no battery is fitted.

| State | Feather CHG (amber) | red "CHG" | green "FULL" |
|---|---|---|---|
| USB/dock power, charging | on | **on** (VBUS → 1.5k → red → STAT low, about 2 mA) | off |
| USB/dock power, charge complete | off | off | **on** (STAT high → 1.5k → green, about 1–2 mA) |
| No USB power | off | off | off |
| USB power, no cell or charger fault (STAT Hi-Z) | off | possibly a faint glow (red and green in series across VBUS) | possibly a faint glow |

These LEDs are wired to the charger in hardware, so they work with the power switch OFF.
