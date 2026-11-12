# OpenALD Feather RP2040 v1.0 — pin map

Nothing here has been hardware-validated yet.

## Feather RP2040 (Adafruit #4884) connections

| Feather pin (silkscreen) | RP2040 GPIO | Goes to | Wire | Notes |
|---|---|---|---|---|
| **D24** | GP24 | Controls J1.1 **ENCA** (wheel A) | 30 AWG | Use the internal pull-up. Debounce in firmware: the board has no RC filter. |
| **D25** | GP25 | Controls J1.2 **ENCB** (wheel B) | 30 AWG | Use the internal pull-up. |
| **D4** | GP6 | Controls J1.3 **ENCSW** (wheel push) | 30 AWG | Use the internal pull-up. Active low. |
| **EN** | — (enables the AP2112 3.3 V regulator) | Controls J1.4 **EN** → SW1 common | 28–30 AWG | SW1 OFF ties EN to GND, which turns the 3.3 V rail, the RP2040 and the FM module off. ON leaves EN open (the Feather's own 10 k pull-up turns it on). |
| **GND** (JP1.13) | — | Controls J1.5 **GND** | 28 AWG | Common for the wheel, the switch, the divider and the green LED. |
| **USB** (VBUS) | — | Controls J1.6 **VBUS** | 28–30 AWG | Supplies only the red CHG mirror LED (about 2 mA). |
| **STAT tap** (no pad) | — | Controls J1.7 **STAT** | 32–36 AWG enamel or wire-wrap wire | Solder to the **STAT end of Feather R2**, the 10 k resistor in series with the CHG LED. In this repo's case frame that end is at (25.92, 7.77). Optional: skip it and leave D1/D2 off the board. |
| **BAT** (VBAT) | — | Controls J1.8 **VBAT** | 28 AWG | Top of the battery divider. |
| **A0** | GP26 / ADC0 | Controls J1.9 **BSNS** | 30 AWG | VBAT/2 through 220 k / 220 k, with 100 nF at the ADC pin. |
| **STEMMA QT** (JST SH 4-pin) | GP2 SDA / GP3 SCL, 3V3, GND | RDA5807M module VCC / GND / SDA / SCL | STEMMA QT cable #4210, one end cut | 3V3 here is switched by EN, so the radio turns off with the switch. Arduino `Wire` and CircuitPython `board.STEMMA_I2C()` both use this port. |
| **JST PH battery** | — | 18650 holder + / − | JST PH cable #261 (cut) | **Check polarity** against the "+" mark on the Feather before plugging in. Red goes to the holder + pin (the USB end). |

Spare pins remain free: A1–A3, D5, D6, D9–D13, SCK, MOSI, MISO, TX and RX. The red LED is D13 / GP13 and the NeoPixel is GP16. Both are visible through the top windows.

## Controls board J1 (9 THT pads, 1.8 mm pitch, pad 1 nearest the wheel)

| Pad | Net | On the board |
|---|---|---|
| 1 | ENCA | SW2 (SIQ-02FVS3) A |
| 2 | ENCB | SW2 B |
| 3 | ENCSW | SW2 S (push) |
| 4 | EN | SW1 pin 2 (common) |
| 5 | GND | SW1 pin 1 (OFF), SW2 C, R2, C1, D2 cathode, GND pour |
| 6 | VBUS | R3 1.5 k → D1 (red) anode |
| 7 | STAT | D1 cathode; R4 1.5 k → D2 (green) anode |
| 8 | VBAT | R1 220 k (top of the divider) |
| 9 | BSNS | R1/R2 junction, C1 100 nF |

## Charge-mirror LEDs (on the controls board, above the dock line)

MCP73831 STAT is push-pull. It is low while charging, high (VBUS) when charging is done, and Hi-Z when the charger is off or no battery is fitted.

| State | Feather CHG (amber) | D1 red "CHG" | D2 green "FULL" |
|---|---|---|---|
| USB/dock power, charging | on | **on** (VBUS → R3 → D1 → STAT low, about 2 mA) | off |
| USB/dock power, charge complete | off | off | **on** (STAT high → R4 → D2, about 1.3 mA) |
| No USB power | off | off | off |
| USB power, no cell or charger fault (STAT Hi-Z) | off | possibly a faint glow: D1 and D2 in series across VBUS, about 5.0 V needed | possibly a faint glow |

These LEDs are wired to the charger in hardware, so they work with the power switch OFF.
