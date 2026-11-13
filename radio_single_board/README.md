# OpenALD: PCB, assembly files and 3D-printed case (v1.0)

OpenALD is an ATmega328PB + RDA5807M (RRD-102 module) FM radio, **programmable over its USB-C port** (CH340K USB-serial, Arduino IDE / MiniCore). It runs from one 18650 cell (reverse-polarity protected), charges over USB-C (TP4056 + DW01A/FS8205A protection) and uses an XC6206 3.3 V LDO. Controls are a thumbwheel encoder with push for volume and tuning (**press the wheel = battery check**; there is no separate battery-check button any more), and a slide power switch that sticks out of the case. A **3-LED battery-level bar** runs as a **vertical column centred across the front face** near the jack end (so it stays well above the rim when the radio stands USB-C-down in the OpenALD Dock), and the TP4056 red/green charge LEDs sit next to the USB-C. The headphone cable acts as the antenna. The board silkscreen reads **OpenALD v1.0**.

> **Note:** I couldn't open the attached spec file on the build machine. This design follows the written summary of the spec instead, so compare it against your original.

> **OpenALD v1.0 is untested hardware.** This release is the former FM radio rev 4.3 design, renamed and reset to v1.0, with no electrical changes. Since then (all still v1.0): the level bar moved to a vertical column near the jack end for the charging dock, and on 2026-11-11 the separate battery-check button SW2 was removed (the wheel press does its job through a small P-FET, Q4) and the bar was centred across the board and moved up (see "Wheel press replaces the battery-check button"). On 2026-11-12 the USB-C receptacle J1 moved 0.9 mm toward the board edge and the case got the Feather's straight cable-plug recess plus assembly notches (see "USB-C 0.9 mm out to the case face"). It passes ERC, DRC and the 3D case-fit check. Pre-release rev 4.2 had two full datasheet reviews, and rev 4.3 (which only changed the charge-current resistor) had its own independent review (see "Pre-release history" below). No board has been built or programmed yet. Build one or two first.

The hardware in this v1.0 package is the ~900 mA charge-current design (R3 = 1.2k, TP4056 PROG). Charge time for a 3000 mAh 18650 is about 3.7 h if the chip holds 900 mA through the CC phase, likely closer to ~4 h in the closed case if the TP4056 thermally throttles. Use a **≥ 1 A charger**. A laptop USB 2.0 port is only rated 500 mA. If you need to charge from a laptop USB-A port, change **R3 to 2.4k (C22940, Basic) for ~460 mA**. See the pre-release rev 4.3 notes for the thermal estimate, USB source details, and the first-board cell-temperature check.

## Board at a glance
| | |
|---|---|
| Size | **38.0 x 87.0 mm**, 1.6 mm FR-4, 2 layers, 1 oz, 3 mm corner radius |
| Mounting | 4x M2 holes (2.2 mm) at (3.2, 3.2), (34.8, 3.2), (3.2, 83.8), (34.8, 83.8) mm from the top-left corner |
| Top side | All SMT parts (including the 3 level-bar LEDs), plus the power switch (THT) and the hand-soldered RRD-102 module |
| Bottom side | MPD BH-18650-PC holder only (THT, hand-soldered) |
| Copper | GND pour on both layers, stitched with 102 GND vias (rev 4.2: 89 stitching vias on two offset 2.5 mm grids, 3 thermal vias in the TP4056 pad, plus routed GND vias). Power nets are 0.5 mm, signals 0.25 mm (0.15 mm minimum at the TQFP/ESSOP pins). Vias are 0.6/0.3 mm (0.8/0.4 mm on power). The autorouter ran with a 0.45 mm edge keep-out |
| ERC | **0 errors**, 2 accepted warnings (`fab/erc_report.txt`): pin_to_pin on U3 pins 3/6 (PE0 tied to GND, PE1 tied to +3V3 for ATmega328P-AU drop-in). This is intentional |
| DRC | **0 errors, 0 unconnected pads, 0 schematic-parity issues** (re-run after the 2026-11-11 wheel-press / centred-bar update). 62 cosmetic silkscreen warnings are waived: 8 silk_edge_clearance (the jack, wheel and switch overhang the edge on purpose), 24 silk_over_copper (reference text over pads/vias) and 30 silk_overlap. Min track 0.187 mm (rule 0.15 mm), tracks/vias ≥ 0.75 mm from the edge (`fab/drc_report.txt`) |

## How charging is shown (power switch off or on)
The power switch cuts VSYS. In rev 4 the MCU also runs from USB with the switch off (see "Power path"), so firmware can show the charging animation on its own while USB is plugged in (optional). The rev 3 options still work:
1. **Always, with no MCU needed:** the TP4056's own LEDs, **D3 red = charging and D4 green = full**, light from USB power. They shine through their own two light tunnels just left of the USB-C. This works with the switch off.
2. **With the switch off, hold the wheel pressed in:** the wheel's push switch turns on P-FET Q4, which powers the MCU from the battery (through D10, and VSYS through D2) for as long as the wheel is held in. While held, the MCU reads nCHRG and shows the charging animation or the level on the bar. Releasing the wheel powers it off again.
3. **With the switch on:** a short press of the wheel any time shows the level on the bar, or the charging animation if USB is charging. Plugging USB in while the radio is on also shows the charging animation once for 3 s.

Rev 4 powers the MCU from USB through its **own** LDO (U6) instead of feeding VBUS into VSYS. That way the FM module and the battery divider stay off. Note that while USB is powering the MCU with the switch off, BAT_ADC reads about 0 V, so the cell voltage isn't measurable then. For the level while charging, hold the wheel in (VSYS then sees the cell through Q4 and D2) or switch on.

## Files
```
kicad/                     KiCad 9 project (open openald.kicad_pro)
  openald.kicad_sch       schematic (PDF in docs/openald-schematic.pdf)
  openald.kicad_pcb       routed board
  openald.pretty/         custom footprints: RRD-102 module, Mitsumi SIQ-02FVS3, HRO SK-12E12-G5 switch (U3/U7/U8 use stock KiCad footprints)
  openald.kicad_sym       custom symbols;  openald.3dshapes/  simple 3D models for previews and the fit check
fab/
  openald-gerbers-jlcpcb.zip   Gerbers + Excellon drill files (upload this)
  openald-BOM-jlcpcb.csv       JLC assembly BOM (Comment, Designator, Footprint, LCSC Part #)
  openald-CPL-jlcpcb.csv       JLC pick-and-place (Designator, Mid X, Mid Y, Layer, Rotation), corrected for EasyEDA origins
  openald-centroid.csv         standard centroid / XY file (Designator, Comment, Footprint, Mid X, Mid Y, Rotation, Layer); same positions as the JLC CPL
  openald.pos                  KiCad ASCII position file (mm); same corrected positions as the centroid/CPL, plus hand-soldered U4 and BT1
  jlc_cpl_fit.json              per-part fit of the EasyEDA footprints (offsets, rotations, pad match)
  openald-BOM-human.csv        full BOM with MPNs, qty, live LCSC stock and price, links, plus hand-solder and off-board parts
  openald-BOM-pcbway.xlsx      PCBWay SMT assembly BOM (official template filled; qty per board; title says 5PCS)
  openald-BOM-nextpcb.xls      NextPCB assembly BOM (official template filled; qty per board)
  minimal/                      JLC files for a 4-part "hotplate" assembly only (see below)
    openald-BOM-jlcpcb-minimal.csv
    openald-CPL-jlcpcb-minimal.csv
    openald-centroid-minimal.csv
    openald-minimal.pos
    openald-LCSC-order-handsolder.csv   remaining LCSC parts for 5 boards, with labelled spares
    cost_estimate.txt
  erc_report.txt, drc_report.txt, lcsc_lookup.json, cost_summary.json
case/
  openald_case.scad       parametric OpenSCAD case (includes case_params.scad)
  case_params.scad         AUTO-GENERATED from the PCB by scripts/gen_case_params.py
  case_top.stl, case_bottom.stl   heat-set-insert version (default)
  nut_variant/             same case with M2 hex-nut pockets instead of inserts
  case_fit_report.txt      3D interference check of the assembled PCB against both halves and the LED tunnel walls
previews/                  pcb_top.png, pcb_bottom.png, pcb_closeup_led_bar.png, pcb_closeup_reverse_polarity.png,
                           pcb_closeup_polarity_marks_bottom.png (rev 4.2), schematic-1.png, case_closed.png, case_*.png,
                           closeup_led_bar.png, closeup_front_usb_leds.png, cutaway_led_tunnels.png (section through the bar),
                           closeup_power_switch.png, closeup_usb_c.png, closeup_thumbwheel.png, closeup_jack_end.png,
                           cpl_overlay_<REF>.png (EasyEDA/JLC footprint vs KiCad pads; rev 4 adds U3/U6/U7/U8, rev 4.2 Q2/Q3, 2026-11-11 Q4),
                           pcb_closeup_usb_serial.png
docs/openald-schematic.pdf
scripts/                   generator scripts. run_all_pcb.sh regenerates everything up to DRC,
                           make_fab.py the fab outputs (add --minimal for the hotplate assembly set),
                           make_vendor_boms.py the PCBWay/NextPCB BOMs (templates in scripts/templates/),
                           build_case.sh the case, its checks and the renders
```

## Ordering at JLCPCB (assembled)
1. Upload `fab/openald-gerbers-jlcpcb.zip`. Settings: 2 layers, 38x87 mm, 1.6 mm, any colour, HASL (lead-free) or ENIG.
2. Turn on **PCB Assembly**, top side.
3. Upload `openald-BOM-jlcpcb.csv` and `openald-CPL-jlcpcb.csv`. If a site asks for a centroid or XY file instead, use `openald-centroid.csv` (same positions, plus value and footprint columns). If it asks for a `.pos` or KiCad position file, use `openald.pos`. U4, BT1 and J3 have no JLC placement, so they show as "not selected". Leave them that way, because you hand-solder them (J3 is not fitted).
4. **SW1 (SK-12E12-G5) is a through-hole part.** If you want JLC to solder it, pick **Standard PCBA**, which adds JLC's THT soldering fee. To keep the cheaper Economic SMT-only service, deselect SW1 and hand-solder it, which is 5 easy joints. Buy it from LCSC (C136720) in that case.
5. **Check every part's orientation in JLC's placement preview** before paying. The CPL has per-part corrections fitted against the EasyEDA footprints JLC uses (see "What changed in rev 3.1"), so the preview should show every part on its pads. The pin-1 and polarity marks to watch are U1, U2, Q1, Q2, Q3, Q4 (SOT-23 FETs), U3 (TQFP-32 pin-1 dot), U5, U6, U7 (CH340K), U8 (USBLC6), D2, D7, D8, D9, D10 and the LEDs D1, D3, D4, D5, D6 (cathode = pad 1, on the left for the bar LEDs). Also check that J1, J2, SW1 and SW3 face the board edge.
6. Parts cost about **$7.32 per board** for the JLC-placed parts (LCSC qty-10 prices from the cached 2026-11-10 lookup, including SW1). The 2026-11-11 wheel-press update removed SW2 (Panasonic EVQ-P7A01P, C79167, Extended, $0.187) and added Q4 (AO3401A, C15127, Basic, $0.081) + R25 (1M, C22935, Basic, $0.002): **−$0.10 per board** vs the previous $7.43, and **one fewer extended part type**. Rev 4.1 was $7.28, **+$0.42 over rev 3.1 ($6.86)**: the ATmega328PB costs more than the ATtiny84A, plus the CH340K ($0.55), the USBLC6 ($0.16), the second XC6206 ($0.13), 3 more B5819W and some passives. On top of that come the PCB, the assembly fee, and the Economic-PCBA extended-part loading fee (~$3.07 per part type per order). There are **11 extended part types**, but **C16581 (TP4056) is a JLC *Preferred* extended part, which has no loading fee**, so **10 types are charged**: C12624, C132230, C136720, C165948, C2830320, C2925423, C351410, C7519, C95562, C968586. That's about **$31 per order** (was ~$34 with SW2; about $28 if you deselect the through-hole SW1 and hand-solder it). Hand-solder and off-board parts add roughly $10 per unit: module ~$1-2, holder ~$3, cell ~$5, screws and inserts.
7. Stock checked 2026-11-10 (re-checked for rev 4.3): **ATmega328PB-AU (C132230) still only 735** (was 2,168 earlier today), R3 1.2k (C22765) 2,137,483 (Basic), AO3401A (C15127) 1,635,833, AO3400A (C20917) 990,950, 1M (C22935) 4,069,811. Earlier check (fallback ATmega328P-AU C14877: 22,013, same footprint and CPL), **CH340K (C968586) 33,016** (CH340N C2977777: 48,107 and CH340C C84681: 97,260 exist, but they are different packages and would need a footprint change), USBLC6-2SC6 (C7519) 28,286, SIQ-02FVS3 1,298, PJ-320D-4A 1,522, SK-12E12-G5 15,527 (EVQ-P7A01P no longer used). Re-check stock before ordering.

## BOM files for PCBWay and NextPCB
`fab/openald-BOM-pcbway.xlsx` and `fab/openald-BOM-nextpcb.xls` are the official vendor templates, filled from the v1.0 human BOM. Quantities are **per board** (75 placements, 37 line items). The PCBWay title says **5PCS** to match a 5-board order; NextPCB has no order-qty field — set the board count on their quote form. U4, BT1 and J3 are marked **DNS** (PCBWay) / **DNP** (NextPCB) so the assembler will not fit them: hand-solder U4 and BT1 yourself, and do not fit a header on J3. SW1 is listed as through-hole (PCBWay Type `thru-hole`). Off-board items (the 18650 cell, M2 screws and inserts) are not in these files; they stay in `openald-BOM-human.csv`. Manufacturer is filled only when the project data names one; most passives, the LEDs, the Schottkys, the beads, U4 and J3 leave that column blank. If you are soldering the boards yourself, buy a few extra 0603 passives and LEDs — quantities were not inflated for spares. Regenerate with `scripts/make_vendor_boms.py`.

## Minimal JLC assembly (hotplate parts only)
If you have a hot-air station and want JLC to place only the parts that are painful by hand, use the files in `fab/minimal/`. Upload the same Gerbers (`fab/openald-gerbers-jlcpcb.zip`), but use:

- `fab/minimal/openald-BOM-jlcpcb-minimal.csv`
- `fab/minimal/openald-CPL-jlcpcb-minimal.csv`

(or the matching centroid / `.pos` if the site asks for those). Regenerated with `python3 scripts/make_fab.py --minimal`. Positions use the same `JLC_CORR` EasyEDA origin/rotation fixes as the full CPL; `jlc_cpl_fit.py --check` and a pad-fit of this 4-row CPL both pass.

**JLC places these four parts (all top side):**

| Ref | Part | Why it is in the minimal set |
|---|---|---|
| J1 | HRO TYPE-C-31-M-12 mid-mount USB-C (C165948) | Mid-mount body sits in board-edge slots; hard to align and easy to melt with an iron or hot air |
| U1 | TP4056 ESOP-8 (C16581) | Exposed pad under the package; needs reflow or a hotplate to solder reliably |
| U3 | ATmega328PB-AU TQFP-32, 0.8 mm pitch (C132230) | No exposed pad, so hot air *can* do it, but 0.8 mm pitch is easy to bridge; factory placement is much more reliable |
| U7 | CH340K ESSOP-10 (C968586) | Exposed pad under the package; same as U1 |

**Looked at, but left off (your hot-air station is enough):** U2 (DW01A, SOT-23-6), Q1 (FS8205A, SOT-23-6 in this design — not TSSOP-8), U8 (USBLC6-2SC6, SOT-23-6), Q2/Q3/Q4 (SOT-23) and U5/U6 (SOT-23-3). All of those have side-only pins and no bottom-only pad. U4, BT1 and J3 stay hand-soldered / unfitted as before.

**Estimated JLC cost for 5 boards (estimate only, not a live quote):** about **$36** before shipping, tax or tariff, using the published Economic PCBA table (setup $8.18, stencil $1.53, $3.07 feeder × 3 extended types, SMT joints, $0.45 confirm-placement) plus ~$2 for 5 bare boards and **$14.35** in parts (qty-1 prices: the 328PB is $1.86 each at qty 5). The TP4056 is a Preferred extended part, so it has no feeder fee. The other three are Extended. Details are in `fab/minimal/cost_estimate.txt`. JLC keeps the Economic stencil; it is not shipped. If you want a stencil for the remaining SMT, order a separate frameless one from JLC (~$3) for hand paste + hot air.

**Parts you buy and solder yourself:** `fab/minimal/openald-LCSC-order-handsolder.csv` is an LCSC order list for everything else on the board that has an LCSC number. Quantities are **5 boards plus labelled spares** (+10 on 0603 passives, +3 on 0603 LEDs and SOD-123 diodes, +2 on 0805/1206 caps, +1 on SOT-23s and unique mechanicals). The Mitsumi wheel (SW3) spare is marked optional because that part is about $3. You also still need the RRD-102 module (U4), the MPD BH-18650-PC holder (BT1), an 18650 cell, and the M2 screws and inserts — those are not in the LCSC list; see the human BOM.

## Hand assembly after JLC delivers the board
| Ref | Part | Notes |
|---|---|---|
| U4 | RRD-102V2.0 RDA5807M module (11x11 mm, 2.0 mm pitch) | Solder flat on its pads, chip side up. Check the L/R pads (see caveats). |
| SW1 | HRO SK-12E12-G5, if JLC didn't fit it | Seat it fully, with the knob pointing off the right edge, and solder the 3 pins and 2 tabs. |
| BT1 | MPD BH-18650-PC holder, bottom side | Polarity is printed on the bottom silk: large "+" / "BAT+" beside the holder at the USB-C end, "−" / "BAT−" at the jack end. **The holder itself can be soldered either way round** (its two pins are symmetric), so fit it with its moulded **+ end (flat contact) on the square pad at the USB-C end** and the spring (−) at the jack end, then check with a meter before inserting a cell. A reversed cell is now harmless (rev 4.2), but the radio won't run until it is turned round. |
| J3 | 2x3 ISP pads | Do not fit a header (the case won't close over it). Use a 2x3 pogo clip/adapter once, to burn the bootloader. |

## Programming
**Once per board, burn the bootloader over ISP:**
1. Arduino IDE -> Boards Manager: install **MiniCore** (MCUdude; board-manager URL `https://mcudude.github.io/MiniCore/package_MCUdude_MiniCore_index.json`).
2. Tools: Board **ATmega328**, Variant **328PB** (or **328P / 328PA** if you fitted the C14877 fallback), Clock **Internal 8 MHz**, BOD **2.7 V** (or 1.8 V), EEPROM retained, Bootloader **Yes (UART0)**, Baud rate: the default (38400 for 8 MHz internal is the safest; 115200 is often unreliable on the RC oscillator).
3. Connect a **3.3 V** ISP programmer (USBasp set to 3.3 V, or an Arduino-as-ISP with a level-safe setup) to the J3 pogo pads (standard 6-pin AVR ISP, pin 1 = MISO). Either let the programmer supply 3.3 V on VCC, or set it to "no power" and power the board from USB-C with the switch off. **Never put 5 V on VCC.** It would back-feed the RDA5807M through the I2C lines and push 5 V into U6's output.
4. Tools -> **Burn Bootloader**. This sets the fuses (internal 8 MHz) and writes Optiboot.

**After that, upload over USB-C:** plug in USB-C (the power switch can stay **off**, and the radio stays unpowered), choose the CH340 serial port, and click **Upload** with the same MiniCore settings. DTR# auto-resets the MCU into Optiboot. Windows needs the WCH CH340/CH341 driver (CH341SER), and macOS 11+ / Linux include one.

**Power switch:** slide toward the headphone-jack end = **ON**; toward the USB-C end = OFF. On an SPDT slide switch, the slider joins the common pin (2) to the outer pin on the knob's side, so the knob at the pin-3 end connects 2-3. Pin 2 is VBAT and pin 3 is VSYS, so 2-3 = ON. Pin 3 is the pin nearest the jack end. Check with a meter before closing the case.

## ATmega328PB pin map (TQFP-32) - MiniCore Arduino pin names
| Pin | Port | Arduino | Net | Function |
|---|---|---|---|---|
| 1 | PD3 / INT1 | D3 | ENC_B | encoder B (internal pull-up) |
| 2 | PD4 | D4 | - | **spare** since 2026-11-11 (was ENC_SW). The wheel press is now read on PC1 / BTN_SENSE (pin 24) |
| 3 | PE0 | (D23) | GND | tied to GND for ATmega328P drop-in. **Leave as input, no pull-up** |
| 4 | VCC | | +3V3 | MCU rail (U6), 100 nF C7 |
| 5 | GND | | GND | |
| 6 | PE1 | (D24) | +3V3 | tied to +3V3 for ATmega328P drop-in. **Leave as input, no pull-up** |
| 7, 8 | PB6, PB7 | | - | no crystal (internal 8 MHz RC); spare |
| 9 | PD5 / OC0B | D5 | LVL1 | level LED 1 (D1, bottom of the column / lowest), 1k, active high, PWM |
| 10 | PD6 / OC0A | D6 | LVL2 | level LED 2 (D5, middle), 1k, active high, PWM |
| 11, 12 | PD7, PB0 | D7, D8 | - | spare |
| 13 | PB1 / OC1A | D9 | LVL3 | level LED 3 (D6, top of the column, nearest the jack / full), 1k, active high, PWM |
| 14 | PB2 | D10 | - | spare |
| 15 | PB3 / MOSI | D11 | MOSI | ISP only (J3) |
| 16 | PB4 / MISO | D12 | MISO | ISP only (J3) |
| 17 | PB5 / SCK | D13 | SCK | ISP only (J3) |
| 18 | AVCC | | +3V3 | 100 nF C13 |
| 19 | ADC6 | A6 | - | spare (analog only) |
| 20 | AREF | | AREF | 100 nF C14 (use the internal 1.1 V reference) |
| 21 | GND | | GND | |
| 22 | ADC7 | A7 | - | spare (analog only) |
| 23 | PC0 / ADC0 | A0 | BAT_ADC | battery voltage (VSYS), 47k/12k divider + 100 nF (rev 4.1) |
| 24 | PC1 / ADC1 | A1 | BTN_SENSE | **wheel press** (SW3 S → Q4 → VBTN → 4.7k/10k divider; **high = pressed**, no pull-up: `pinMode(A1, INPUT)`; can also be read as ADC1, threshold ≈ 1.3 V). Wakes the MCU via PCINT9 |
| 25 | PC2 | A2 | CHRG_SENSE | TP4056 nCHRG through Schottky D7; enable the internal pull-up; **low = charging** |
| 26 | PC3 | A3 | - | spare |
| 27 | PC4 / SDA0 | A4 (SDA) | SDA | I2C to RDA5807M (1k series R16, 4.7k pull-up R14 to +3V3R) |
| 28 | PC5 / SCL0 | A5 (SCL) | SCL | I2C (1k series R17, 4.7k pull-up R15 to +3V3R) |
| 29 | PC6 / RESET | | nRESET | 10k pull-up R10, ISP RESET, DTR# auto-reset via 100 nF C19 |
| 30 | PD0 / RXD0 | D0 | MCU_RX | from CH340K TXD (10k pull-up R19) |
| 31 | PD1 / TXD0 | D1 | MCU_TX | to CH340K RXD through 1k R20 |
| 32 | PD2 / INT0 | D2 | ENC_A | encoder A (internal pull-up) |

**Pin budget:** 16 I/O are used, and PB0, PB2, PB6, PB7, PC3, PD4, PD7 and ADC6/7 are spare (not broken out). nSTDBY (full) isn't read: "full" is the same as "USB present, not charging, cell ≥ 4.10 V". The green D4 shows "full" in hardware.

Firmware notes: use the hardware TWI (`Wire`). The RDA5807M uses I2C address 0x10 for sequential access and 0x11 for random access. Before talking to the radio, check that it is powered (switch on), because with only USB present the +3V3R rail and the I2C pull-ups are off. Measure BAT_ADC against the internal 1.1 V reference (`analogReference(INTERNAL)`): V_sys = ADC/1023 x 1.1 x 59/12 (rev 4.1 divider 47k/12k). With these values 4.2 V reads about 0.85 V (ADC ≈ 795 with a nominal 1.1 V reference); calibrate the reference once per board, since it is only guaranteed 1.0-1.2 V. **Don't call `Wire.begin()` while the radio rail is off** (switch off): it enables the AVR's internal pull-ups on SDA/SCL, which would trickle ~80 µA per line into the unpowered RDA5807M; start `Wire` only after V_sys > 3 V, and call `Wire.end()` plus `pinMode(SDA/SCL, INPUT)` before the radio loses power. Keep BOD at 2.7 V (8 MHz needs ≥ ~2.4 V). If you only need it for programming, call `Serial.end()` and leave PD1 as an input when you don't need serial.

### Firmware spec: thumbwheel encoder (SIQ-02FVS3)

Paper-verified against the Mitsumi SIQ series datasheet ([LCSC copy of the official PDF](https://datasheet.lcsc.com/datasheet/pdf/7bff72617d5a3503f5ed21ab02a77dea.pdf?productCode=C2925423)). Nothing here has been tested on hardware.

The part is a 15-detent quadrature encoder plus a momentary slide/push switch. Terminals A and B are the encoder contacts, S is the push switch, and C is the common for all three (see the datasheet "CIRCUIT" diagram). On this board C is tied to GND, A goes to **D2 / PD2 / INT0** and B to **D3 / PD3 / INT1**. **The push switch S no longer goes to an MCU pin** (2026-11-11, it replaced the battery-check button): S drives the gate of P-FET **Q4** (AO3401A) with a 1 MΩ pull-up R25 to VBAT. Pressing the wheel pulls the gate to GND, Q4 switches VBAT onto VBTN, and the MCU sees the press as **BTN_SENSE high on A1 / PC1** (4.7k/10k divider; no internal pull-up). The same path powers the MCU when the power switch is off, so holding the wheel in is the off-state battery check. The S contact carries only ~4 µA (VBAT / 1 MΩ). A and B have no external pull-ups, no RC filters and no ESD diodes: enable the ATmega328PB internal pull-ups (20–50 kΩ, DS40001906) in `setup()` with `INPUT_PULLUP`. At 3.3 V that is about 66–165 µA per closed contact, under the 0.5 mA / 5 V DC rating. The datasheet does not specify a minimum wetting current or a bounce time.

The output is a 2-bit Gray-code quadrature waveform, **one full cycle (four valid state changes) per detent** (24° ±3°, 15 detents per turn). Clockwise, A leads B. At rest in a detent, A and/or B may already be low, so do **not** use INT0/INT1 low-level interrupts to wake from Power-down — the MCU would never stay asleep. Pin-change interrupts on PD2/PD3 (`PCINT18/19`, PCI2) for the turn and on PC1 (`PCINT9`, PCI1) for the press do wake from Power-down and Standby on any edge (BTN_SENSE idles low and goes high on a press). INT0/INT1 any-edge interrupts are fine while awake, but a 1 ms poll of the state table below also debounces, so a timer tick is the simplest approach. Count **one step per detent** (accumulate ±4 transitions), not one step per edge, or volume will jump four units per click.

**Wheel behaviour (v1.0, 2026-11-11):**

| Action | Power switch ON | Power switch OFF |
|---|---|---|
| Turn | volume | nothing (MCU unpowered, or on USB only) |
| **Short press** (released < 500 ms, no turn while pressed) | **battery check**: bar shows the level (or the charging animation) for 3 s | — |
| **Hold pressed** | after 500 ms with no turn: **seek** (next station) | **battery check while held**: the press itself powers the MCU; bar shows level / charging until release |
| Push and turn | tune (step the frequency); no battery check, no seek | — |

The switch-off case is detected at power-on: a power-on reset with BTN_SENSE already high means "wheel-powered" (see the battery-bar spec). There is no mute function on the wheel (there never was one); add one in firmware if you want it, e.g. double-press.

Example (MiniCore, board "ATmega328PB", 8 MHz internal). Call `encoder_setup()` from `setup()`, and `encoder_poll()` from a 1 ms tick or from `loop()` if you wait on `millis()`.

```cpp
// D2=ENC_A (PD2/INT0), D3=ENC_B (PD3/INT1), A1=BTN_SENSE (PC1): wheel press, HIGH = pressed
// (SW3 S -> Q4 gate; Q4 -> VBTN -> 4.7k/10k divider). Common C = GND. D4 (PD4) is spare.
const uint8_t PIN_A = 2, PIN_B = 3, PIN_SW = A1;
// prev<<2|curr -> +1 / -1 for a valid 1-step Gray-code move; 0 = bounce or invalid
static const int8_t ENC_TAB[16] = {
  0,-1,+1,0, +1,0,0,-1, -1,0,0,+1, 0,+1,-1,0
};
static uint8_t enc_prev;
static int8_t  enc_accum;
static int8_t  enc_step;        // +1 / -1 once per detent; consume in the main loop
static uint8_t sw_hist, sw_down, sw_turned;
static uint16_t sw_ms;
volatile uint8_t battery_check_request, seek_request;   // consumed by the main loop

void encoder_setup() {
  pinMode(PIN_A, INPUT_PULLUP);
  pinMode(PIN_B, INPUT_PULLUP);
  pinMode(PIN_SW, INPUT);         // external 10k pull-down R7; do NOT enable the pull-up
  enc_prev = (digitalRead(PIN_A) ? 2 : 0) | (digitalRead(PIN_B) ? 1 : 0);
}

void encoder_poll() {            // call every 1 ms
  uint8_t now = (digitalRead(PIN_A) ? 2 : 0) | (digitalRead(PIN_B) ? 1 : 0);
  enc_accum += ENC_TAB[(enc_prev << 2) | now];
  enc_prev = now;
  if (enc_accum >= 4)  { enc_step += 1; enc_accum = 0; }
  if (enc_accum <= -4) { enc_step -= 1; enc_accum = 0; }

  sw_hist = (sw_hist << 1) | (digitalRead(PIN_SW) ? 0 : 1);   // 0 = pressed (BTN_SENSE high)
  if (!sw_down && (sw_hist & 0x1F) == 0x00) { sw_down = 1; sw_ms = 0; sw_turned = 0; }  // 5 ms pressed
  if (sw_down) {
    if (enc_step) sw_turned = 1;            // push-and-turn = tune (main loop reads enc_step + sw_down)
    if (sw_ms < 60000) sw_ms++;
    if ((sw_hist & 0x1F) == 0x1F) {         // released
      if (sw_ms < 500 && !sw_turned) battery_check_request = 1;   // short press: show the bar for 3 s
      sw_down = 0;
    } else if (sw_ms == 500 && !sw_turned) {
      seek_request = 1;                     // long press: start seek
    }
  }
}
```

To sleep in Power-down and wake on a turn or a press, enable PCI2 for PD2/PD3 and PCI1 for PC1 (`PCMSK2 |= _BV(PCINT18)|_BV(PCINT19); PCMSK1 |= _BV(PCINT9); PCICR |= _BV(PCIE2)|_BV(PCIE1);`) and use empty `ISR(PCINT2_vect)` and `ISR(PCINT1_vect)`. Do not rely on INT0/INT1 level wake. Leave the spare PD4 as `INPUT_PULLUP` (or output low) so it doesn't float. BTN_SENSE reads high above VIH = 0.6 × VCC: full cell 2.86 V vs 1.98 V needed; at the 3.25 V cutoff about 2.2 V vs ~1.7 V (VCC ≈ 2.85 V behind D8/D10 + U6). Same divider and margins as the old button.

### Firmware spec: battery-level bar (no firmware is included; this is the intended behaviour)

| Item | Behaviour |
|---|---|
| Default | All three level LEDs **off**. |
| Trigger | **Short press of the thumbwheel** (BTN_SENSE high, released within 500 ms without turning). Debounce 5–30 ms. With the power switch off, holding the wheel in powers the MCU and is the trigger by itself. |
| Show | Light the bar for **3 s** after the short press (while held, when wheel-powered with the switch off). Measure *before* turning the LEDs on: average 16 ADC samples with the LEDs off, and use 50 mV hysteresis between bands. |
| Levels (not charging) | **≥ 3.90 V: ●●●** · **3.60-3.90 V: ●●○** · **3.40-3.60 V: ●○○** · **3.30-3.40 V: LED 1 blinks slowly** (1 Hz) · **< 3.30 V: LED 1 blinks fast** (4 Hz) = very low, charge now. |
| Very low while playing | When the radio is on and V < 3.30 V, flash LED 1 for 50 ms every 10 s even without a press. Below **3.25 V** (was 3.10 V before the rev 4.2 review), mute the RDA5807M (power-down bit) and sleep the MCU. Reason: the MCU rail is about 0.26 V below the cell (D8 + U6), and the 2.7 V BOD level can trip anywhere from 2.5 to 2.9 V (DS40001906 Table 33-7), so on a worst-case chip a 3.10 V cut-off would never run and the radio would keep playing until the DW01A. The DW01A cuts the cell off at 2.4-2.6 V (typ. 2.5 V) as a backstop. |
| Charging (CHRG_SENSE low) | The cell reads high while charging: during the ~900 mA constant-current phase it reads about 0.1-0.2 V above its resting voltage. **Estimate = V - 0.15 V.** Light the LEDs for the estimated level solid and **blink the next LED at 1 Hz** ("filling"). If the estimate is already at 3 LEDs, blink LED 3 until charging ends. |
| Charged (CHRG_SENSE high, V ≥ 4.10 V) | ●●● solid. The firmware can't tell "full on USB" from "just unplugged", and both show 3 LEDs, which is correct. |
| USB plugged in while on | On a falling edge of CHRG_SENSE, run the charging display once for 3 s. |
| Switch off, USB only (rev 4) | The MCU runs from USB (BTN_SENSE low, BAT_ADC ≈ 0 V). Keep the RDA5807M off, since it's unpowered anyway. Optionally show the charging animation (CHRG_SENSE low) without a level. With the cell voltage unknown, light LED 1 and blink LED 2. Otherwise sleep. |
| Switch off, wheel held in | The MCU powers up through Q4 → D10 (and VSYS through D2) only while the wheel is held in. On a power-on reset with BTN_SENSE high, treat it as "wheel-powered" (battery check only, no seek). Add **about +0.1-0.15 V** to the reading for D2's drop (B5819W at ~0.1 mA; calibrate). Show the level or charging state while the wheel is held, and keep the RDA5807M powered down. The power disappears on release. If power is still there 0.5 s after release, the switch is on: start the radio normally. |
| Brightness | 100 % is fine indoors. Optional: 25-50 % software PWM (≥ 200 Hz) if you find it too bright in the dark. |

**LED brightness (KT-0603G, C12624):** the datasheet gives Vf 2.6-3.1 V and 210-430 mcd at 5 mA. Its I-V curve gives about 2.4 V at 1 mA for a typical part. With 1k from the 3.3 V pin that's **about 0.85 mA typical, and 0.4 mA for the highest-Vf bin**. From the relative-intensity curve, 1 mA gives roughly 0.3x the 5 mA brightness, so about **40-130 mcd per LED**. That's clearly visible through the 2.4 x 1.4 mm windows indoors and in daylight, and it may be a bit bright in a dark room (use PWM). When wheel-powered with the switch off on a nearly empty cell, the rail drops to about 3.0-3.1 V and the LEDs get dimmer but stay visible. The TP4056 LEDs run from USB 5 V through 1k: about 3 mA red and 2.4 mA green.

## Design corrections (carried over from the original pre-release)
- **Headphone drive:** the module's audio outputs carry a DC bias, so they now go through 100 uF series caps (C10, C11; about 50 Hz corner into 32 ohm) and 600 ohm ferrites (FB1, FB2).
- **Antenna network:** the headphone ground goes to board GND through ferrite FB3, which makes the cable's ground conductor the antenna. It is coupled into FM_ANT with 1 nF (C12). The module's supply is filtered with 10 ohm + 22 uF + 100 nF.
- **ADC divider:** it sits on switched VSYS, so it draws nothing when the radio is off. 47k/12k with 100 nF at the pin (rev 4.1; was 100k/33k).
- **USB-C:** CC1 and CC2 each have their own 5.1k pull-down. VBUS has 10 uF. Charge current is set to about 900 mA (R3 = 1.2k, C22765, Basic; see rev 4.3). Use a ≥ 1 A charger; a laptop USB 2.0 port is only rated 500 mA. Red/green charge LEDs (D3/D4) show through their own light tunnels next to the USB-C.
- **Battery check with the switch off:** holding the thumbwheel in turns on P-FET Q4 (gate pulled up to VBAT by 1M R25, pulled to GND by the wheel's push switch), which powers VSYS through Schottky D2 and the MCU rail through D10 while you hold it; firmware shows the battery level on the 3-LED bar. (Until 2026-11-11 a separate button, SW2, did this.)

## 3D-printed case
- Two halves split at the PCB's bottom face. The PCB is clamped between bosses at the 4 corner holes. **4x M2 x 12 mm screws** go in from the bottom into M2 heat-set inserts (OD 3.2-3.5 mm) in the top half. The nut variant uses M2 x 16 mm screws with M2 nuts on the top face.
- Outer size **43 x 92 x 33.4 mm**: top half 9.8 mm, bottom half 23.6 mm plus a 1.2 mm lip. Corners are rounded at 5.5 mm in plan view and 2 mm on the top and bottom edges. Walls are 2 mm, floor and ceiling 1.6 mm.
- Openings, all generated from the real footprint positions:
  - **Top edge:** 3.5 mm jack hole (6.8 mm, chamfered). (The battery-check button hole and printed plunger are gone since 2026-11-11; that part of the wall is solid.)
  - **Front (top) face:** the 3-LED level bar as a vertical column **centred across the face** near the jack end (three 2.4 x 1.4 mm rounded windows at 2.8 mm pitch on the centre line, window centres 75.3 / 78.1 / 80.9 mm from the USB-C edge of the PCB = 77.8 / 80.6 / 83.4 mm from the case's USB-C end; D1's tunnel leans 2.3 mm from its LED up to the lowest window) and, at the USB-C end, the two 1.6 mm charge-LED windows just left of the USB-C. Every window has a 0.4 mm rounded rim and its own light tunnel (3.2 x 2.0 mm bore, 0.8 mm walls, ending 0.2 mm above the PCB).
  - **Right side:** thumbwheel in a smooth 1 mm-deep pocket; the wheel stands out about 1.35 mm from the pocket floor. Below it is the power-switch slot, with rounded edges inside and out and engraved "OFF" / "ON" labels; the 3.5 x 2.5 mm knob sticks out 2.8 mm.
  - **Bottom edge:** USB-C centred, in a straight-walled **13.0 x 7.6 mm, 1.5 mm deep cable-plug recess** (corner r 3.0, r 1.0 rounded rim, mouth 15.0 x 9.6 mm), with a 9.44 x 3.76 mm rounded connector opening through the last 0.5 mm of wall. The receptacle face is **1.60 mm inside the case face, 0.10 mm behind the recess floor** (since 2026-11-12; was 2.50 behind a 12.8 x 7.4 filleted bowl), so a cable plug body can go all the way in.
  - **Assembly notches (2026-11-12):** the wheel dial, the switch knob and the USB-C shell all reach into or through a wall, and the top half is lowered straight down over the assembled board. The top half's wheel slot, switch slot and USB-C opening therefore continue down to the split line, and the bottom half has matching tabs that fill the wheel and switch notches up to 0.5 mm below the dial / knob (the lip fills the USB one). Before this the top half could not be lowered over the wheel or the switch knob (overlap 30 / 19 mm³ in the new assembly-path check).
- **Fit check** (`case_fit_report.txt`): every fitted part (KiCad STEP models plus this project's meshes, including the switch knob; J1 as a rounded-end shell) was intersected with both halves and separately with the LED tunnel walls, with **0 interferences**. Since 2026-11-12 it also checks the assembly path: every part reaching past an inner wall face (J1, SW1 knob, SW3 dial), swept down to the split, must miss the top half (all OK). The tunnel walls end 0.20 mm above the PCB. The closest parts to the tunnel walls are D1 inside its slanted tunnel (0.31 mm), the other LEDs inside theirs (0.60 mm) and the USB-C shell (0.73 mm). The check was tested by deliberately shrinking the top clearance, which made it flag the jack, switch and wheel.
- **Print settings (PLA or PETG):** 0.2 mm layers (0.12-0.16 mm gives smoother fillets on the top face), 3 perimeters, 20-25 % infill, no supports. `case_bottom.stl` prints floor-down. `case_top.stl` is exported flipped, so it prints face-down; the light tunnels and the bosses then point up. The windows are on the bed side, so they print clean with no supports. For the thin-skin option, set `led_window="skin"`, use white or natural filament, and keep the first two layers at 0.2 mm. Press the heat-set inserts in at about 220 C (PLA) or 245 C (PETG).
- Customise via the tunables at the top of `openald_case.scad` (clearances, `led_window`, tunnel bore/wall/gap, window sizes, pocket depths, label size, `fastener="nut"`). After changing the PCB, run `scripts/build_case.sh`.

## Known caveats and unverified items
1. **Spec not read.** The attached spec file couldn't be opened.
2. **RRD-102 L/R pads:** the footprint follows the manufacturer's RRD-102V2.0 spec (pin 2 = R, pin 3 = L); one third-party trace swaps them. A swap only mirrors the stereo; fix it in firmware.
3. **Light-tunnel seal:** the walls stop 0.2 mm above the board to allow for print and board tolerances. A little light can still creep under them or through the FR-4. If you see bleed between segments, set `tun_gap = 0` (the walls then touch the solder mask) or paint the inside of the tunnels black. The KT-0603G has a water-clear lens, so it looks like a bright dot. Sanding the window or using the skin option diffuses it.
4. **Switch direction and rating:** check the ON direction with a meter. The HRO SK-12E12-G5 datasheet gives no current rating. The equivalent G-Switch part (C2848870) is rated 1 A at 24 V DC, which is fine for this radio (well under 100 mA, plus the battery-check path). The width of the tab slots isn't dimensioned in the datasheet. I used 0.7 x 1.5 mm slots for its 0.4 mm tabs, so check the first boards.
5. **SW1 needs THT:** it needs JLC Standard PCBA (THT fee) or a hand-soldering step.
6. **CPL**: fitted against the EasyEDA footprints (rev 3.1 + the rev 4 parts), but still glance at JLC's preview. JLC's engineers sometimes re-rotate parts by hand during their DFM review.
7. **Charging while on:** the radio runs from the battery while the TP4056 charges it, so leave it off to charge to full.
8. **LDO dropout:** 3.3 V starts to sag below about 3.45 V on the battery.
9. **Plugs** whose overmold is wider than 6.8 mm may not seat fully in the jack.
10. **3D models:** the models for the jack, wheel, USB-C, switch and module are approximations from datasheets. Print one case and test-fit before a batch.
11. **No firmware** is included. The battery-bar behaviour is specified above. Calibrate the 0.15 V charging offset, the ~0.1-0.15 V D2 drop and the internal 1.1 V reference on your board with a meter.
12. **Alternatives considered** (not used): XKB SS-12D11G5 (C692484, rated 3 A), a bigger switch, but its 9.2 mm tab offset would need more board depth.
13. **Charger status:** CHRG_SENSE only says "charging" or "not charging". Confirm on the first board that PC2 reads high with USB unplugged (the TP4056 nCHRG pin is open-drain and high-impedance without input power).
14. **LED colour choice:** if you prefer red/yellow/green or all-red, KT-0603R (C2286) is a basic part (1.5k for 1 mA) and KT-0603Y (C2287) is extended (+$3 fee). Change design.py and re-run.
15. **OpenALD v1.0 is untested.** The ATmega328PB/CH340K circuit follows the WCH and Microchip datasheets and standard Arduino practice, but no board has been built. Check on the first board: CH340K enumeration, auto-reset, Optiboot upload, that the radio rail stays at 0 V with the switch off and USB in, the actual charge current (~900 mA), and how hot the TP4056 gets in the closed case. Use a ≥ 1 A charger; do not expect a laptop USB 2.0 port to supply this board.
16. **USB data routing:** the D+/D- pair is short (about 18-23 mm) and coupled, but not impedance-controlled (2-layer 1.6 mm board). That's fine for 12 Mbit/s full-speed USB.
17. **Auto-reset clamp diode omitted** (see the rev 4 table). The about 8.3 V DTR# edge on RESET is within the pin's 13 V rating. If uploads are flaky, add a small Schottky from RESET to +3V3.
18. **UART back-feed:** with USB unplugged and serial enabled, MCU TXD (idle high) leaks at most about 150 uA (datasheet worst case) into the unpowered CH340K, limited by R20. That's negligible during Optiboot's 1 s window. Disable `Serial` in normal firmware to avoid any drain.
19. **MCU rail on a low cell:** the extra D8 diode means the MCU's 3.3 V sags about 0.25 V earlier than the radio's (from a cell of about 3.6 V). The MCU itself is rated down to 2.7 V at 8 MHz, and the bar LEDs get a little dimmer.
20. **ATmega328PB stock** at LCSC is low (735 on the rev 4.2 check, 2,168 earlier the same day). If it runs low, use ATmega328P-AU C14877 (same footprint and CPL correction; choose the 328P variant in MiniCore).

## Pre-release history

OpenALD v1.0 is a rename and version reset of the last pre-release board (FM radio rev 4.3). Nothing electrical changed; the only layout change is the level bar move below. The project was briefly called **OpenALS** before being renamed **OpenALD** (it is a device, not a system). The notes below are kept so the design decisions, reviews, and checklists are not lost. File names in these notes have been updated to the OpenALD paths; silkscreen quotes and revision names are left as they were at the time.

### USB-C 0.9 mm out to the case face (still v1.0, 2026-11-12)
Victor's test print of the Feather case showed a cable plug barely holding with the receptacle 2.5 mm inside the case, and he asked for the single board to match the Feather fix. Version stays **v1.0**; case size (43 x 92 x 33.4 mm), USB-C centring, switch, jack, wheel, battery holder and LED positions are unchanged.
* **J1 moved 0.9 mm toward the board edge** (KiCad y 183.35 → 184.25; placement.py `J1` 83.35 → 84.25). Its shell now overhangs the PCB edge by 0.9 mm, so the mouth is **1.60 mm inside the case bottom face** and 0.10 mm behind the new recess floor, the same as the Feather. HRO's recommended layout puts the board edge 5.79 mm from the Ø0.6 locating holes; it is now 5.35 mm (was 6.25), so the shell overhangs about 0.45 mm more than HRO's drawing suggests and the old position was about 0.45 mm further back. All four shell-leg slots stay on the board (front slots end 0.9 mm from the edge). Nothing else moved: in the CPL only J1 changed (Y 5.064 → 4.164).
* **Why J1 and not the whole PCB:** the PCB already sits 0.5 mm from the USB-end wall, so moving it 0.9 mm would have meant thinning that wall to 1.1 mm (the 1.5 mm recess would then break through), moving every opening and LED window relative to the case, and pulling the jack 0.9 mm further inside the case.
* **Re-routed:** the USB pair pre-route in `route_pcb.py` moved with J1, then the board was re-routed with Freerouting (`run_all_pcb.sh 100`; the best of three runs: 909 tracks, 184 vias, 2.20 m of track vs 915 / 200 / 2.19 m before). ERC 0 errors / 2 accepted warnings; DRC 0 errors, 0 unconnected, 0 parity, 62 silk-only; `jlc_cpl_fit.py --check` OK; fab, minimal set and PCBWay/NextPCB BOMs regenerated (parts and cost unchanged).
* **Case:** straight 13.0 x 7.6 x 1.5 mm recess with a 1 mm rounded rim (from the Feather case) instead of the 12.8 x 7.4 bowl, plus the assembly notches/tabs described under "3D-printed case". The J1 shell reaches 0.4 mm into the 0.5 mm end wall through the 9.44 x 3.76 opening (0.25 mm clearance all round).
* **Dock:** both radios now give 6.0 mm insertion on the dock's 4.0 mm pads. A board built before this change (J1 flush) would only get 5.1 mm in the updated dock.

### Wheel press replaces the battery-check button; level bar centred (still v1.0, 2026-11-11)
Victor asked to drop the separate battery-check button and use the thumbwheel press instead, and to centre the level bar across the board and move it up so it reads clearly above the dock rim. Version stays **v1.0**; case thickness (43 x 92 x 33.4 mm), USB-C (centred), power switch, jack, thumbwheel and battery holder positions are unchanged.

**Circuit (paper design, not built):**
```
VBAT --R25 1M--+-- WHEEL_SW_N --- SW3 pin S (wheel push) --- SW3 pin C = GND
               |
VBAT ---(S) Q4 AO3401A (G = WHEEL_SW_N) (D)--> VBTN --D10--> VMCU (MCU LDO U6)
                                                 \--D2--> VSYS ;  VBTN --R6 4.7k-- BTN_SENSE (PC1) --R7 10k-- GND
```
* **Removed:** SW2 Panasonic EVQ-P7A01P (C79167, Extended), its 3D model and the case's button hole + printed plunger (`button_plunger.stl` is gone; that stretch of the jack-end wall is now solid).
* **Added:** Q4 AO3401A P-FET (C15127, Basic, same part and JLC rotation correction as Q2) and R25 1 MΩ (C22935, Basic), at the old SW2 spot on the jack-end edge (Q4 at 29.4, 2.6; R25 at 25.8, 2.2 mm).
* **Kept, now driven by Q4:** D2 (VBTN → VSYS), D10 (VBTN → VMCU), R6/R7 (BTN_SENSE divider). Nothing else in the circuit changed.
* **SW3 S moved off PD4.** WHEEL_SW_N sits at VBAT (up to 4.2 V) when released, which is too high for a 3.3 V pin, so the press is read on **BTN_SENSE (PC1, high = pressed)** instead; PD4 is spare. Wake from sleep on PCINT9 (PC1) plus PCINT18/19 (turn).
* **Current:** released, the gate sits at the source (Vgs = 0): no current except Q4 leakage into R6/R7 (AO3401A IDSS ≤ 1 µA max at 30 V, far lower at 4 V). Pressed: ~4 µA in R25 plus whatever Q4 then powers. Q4's Vgs = −Vcell (−3.0…−4.2 V) is well inside its ±12 V rating and fully enhances it (RDS(on) < 85 mΩ at −2.5 V; the MCU + radio draw < 30 mA).
* **Wheel mapping:** short press = battery check (3 s), hold = seek, push-and-turn = tune, turn = volume; with the power switch off, holding the wheel in shows the battery level while held (see the encoder firmware spec).

**Level bar centred and moved up:** D6 / D5 / D1 now sit on the board centreline **x = 19.0 mm at y = 6.1 / 8.9 / 14.0 mm** (KiCad, from the top-left; was x = 24.0, y = 9.4 / 12.4 / 15.4). The centreline is also where the holder's − pad (19, 2.5) and its locating-peg hole (19, 11.34, 3.2 mm) are, so D6 sits just below the − pad, D5 just above the peg hole and D1 just below it. The three case windows stay evenly spaced (2.8 mm pitch, centres at board y = 6.1 / 8.9 / 11.7 mm); D1's light tunnel leans 2.3 mm from the LED up to its window. **Height above the dock rim** (window centre, radio standing on the pocket floor, rim 50.8 mm above it): **D6 32.6 mm, D5 29.8 mm, D1 27.0 mm** (previously 29.3 / 26.3 / 23.3 mm), i.e. about 24–30 mm above the bottom of the rim's 3 mm lead-in chamfer. A centred *horizontal* row up there was tried first and rejected: the jack's courtyard reaches x = 16.53 mm, which leaves too little width for three LEDs with printed tunnel walls between them. FB1/FB2 moved from (22.4, 5.0 / 6.8) to (24.0, 10.4 / 12.4) to free the column.

**Re-checked:** ERC 0 errors / 2 accepted warnings; board fully re-routed (Freerouting) → DRC 0 errors, 0 unconnected, 0 parity, 62 silk-only warnings; `jlc_cpl_fit.py --check` OK; case fit 0 interferences (closest: D1 0.31 mm inside its slanted tunnel); fab, minimal set and PCBWay/NextPCB BOMs regenerated (75 placements, 37 lines). **Cost:** −$0.10 per board in parts and one fewer JLC extended-part loading fee (~−$3.07 per order). **Untested:** the press-to-power path, BTN_SENSE timing on release, the slanted D1 tunnel's brightness, and the wheel press feel.

### Level bar moved for the dock (still v1.0, 2026-11-11)
The OpenALD Dock holds the radio USB-C-down in a 2 in (50.8 mm) deep pocket, which would hide a bar next to the USB-C. **D1/D5/D6 now form a vertical column at x = 24.0 mm, y = 15.4 / 12.4 / 9.4 mm** (KiCad, from the top-left corner; D1 lowest, D6 nearest the jack, 3 mm pitch). That puts the bar about 20 mm above the dock rim. R11-R13 stay where they were; only the LVL routes changed. Nothing else moved. **The USB-C (still centred), power switch, jack, thumbwheel, battery holder, button and the case thickness (43 x 92 x 33.4 mm) are unchanged.** The TP4056 charge LEDs D3/D4 stay next to the USB-C. They are hidden while docked, so firmware should show charging on the bar (CHRG_SENSE, see the firmware spec). The board was re-routed. Re-checked: ERC 0 errors / 2 accepted warnings, DRC 0 errors / 0 unconnected / 58 silk warnings, case fit 0 interferences, `jlc_cpl_fit.py --check` OK, fab files, vendor BOMs and previews regenerated (`scripts/render_pcb_previews.py`). The dock interface is in `../charging_dock/DOCK_INTERFACE.md`.

### What changed in rev 4.3 (charge current ~900 mA, 2026-11-10)
R3 (TP4056 PROG) is now **1.2k 0603 1%, C22765, 0603WAF1201T5E, Basic** (stock 2,137,483, $0.0034). That is the value the TOPPOWER REV 2.4 datasheet lists for **900 mA**. The formula used throughout this project, \(I_\mathrm{BAT} = 1100 \times 1\,\mathrm{V} / R_\mathrm{PROG}\), gives **~917 mA**. Nothing else on the board moved, the case is unchanged (`case_params.scad` is byte-identical to rev 4.2; case is still 43 × 92 × 33.4 mm), and the silkscreen title now reads "FM RADIO v4.3".

**Why 1.2k, not 1.3k.** 1.3k 0603 (0603WAF1301T5E, C22767) is a JLC *Extended* part (stock 365,951, $0.002) and would add a $3 extended-part fee. By the same 1100/R formula it only gives ~846 mA, just under the 850–950 mA target. 1.33k (C22838, 0603WAF1331T5E) is also Extended and gives ~827 mA. 1.2k is Basic, is the datasheet table entry for 900 mA, and stays in the 850–950 mA window. (Some generic TP4056 write-ups use \(I = 1200 / R\), which would make 1.2k look like 1 A; that is not this datasheet. This project's README has used the 1100 formula and the 1.4k = 780 mA / 1.6k = 690 mA table all along.)

**Charge time.** A 3000 mAh 18650 is about **3.7 h** if the chip holds 900 mA through the CC phase plus a typical CV tail (was ~4.5 h at 730 mA). See the thermal note below: inside the closed case the chip will likely throttle at the start of CC, so the first charge may run closer to **~4 h**.

**USB source.** The board still advertises Default USB Power (5.1k CC pull-downs). Charging draws about **920–950 mA** from VBUS (the charge current plus the TP4056's own current and the red LED; a little more if you are also programming). That needs a **≥ 1 A charger** (phone charger or USB-C charger). A laptop **USB 2.0** port is only rated **500 mA** and will be overloaded; a **USB 3.x** port is rated 900 mA, right at the limit. If you need to charge from a laptop USB-A port, change **R3 to 2.4k (C22940, Basic) for ~460 mA**: charging then takes ~7 h, and nothing else changes.

**Thermal (datasheet estimate, not measured).** Worst-case dissipation in the TP4056 is at the start of CC, with a 3.0 V cell and high VBUS. Charge current flows through Q2 and the FS8205A, so the BAT pin sits about 0.12 V above the cell (Q2 ≤ 85 mΩ at −2.5 V plus ~50 mΩ typ in the protection FETs). At 917 mA that is VBAT ≈ 3.12 V:

| VBUS | P in U1 at start of CC (~3.0 V cell) | Mid-charge (3.7 V cell) |
|---|---|---|
| 5.0 V | ~1.72 W | ~1.08 W |
| 5.25 V | ~1.95 W | ~1.31 W |

The datasheet's thermal regulation kicks in at about **140–145 °C** (page 8 says ~145 °C, page 10 says ~140 °C; current falls to zero if the die goes past 150 °C). This is a 2-layer 1.6 mm board with 3 vias in the ESOP-8 exposed pad, inside a closed 43 × 92 × 33.4 mm case, so at 1.7–2.0 W the die will very likely hit that limit and the chip will cut the current until the cell voltage rises and the dissipation drops. That only makes charging slower; it does not damage the chip. This has not been measured on hardware.

**Other parts at ~920 mA (all fine on paper):**
- **Q2 AO3401A:** max drop 78 mV (85 mΩ × 917 mA), ~71 mW (typ ~45–55 mV / 40–50 mW). Rated −4 A. Still well inside limits; the cell finishes a few millivolts further behind the 4.2 V float (still < 10 mV at C/10).
- **Q3 AO3400A:** only drives Q2's gate; no charge current.
- **Power traces:** VBUS, VBAT, BAT_P, BATN and GND are still ≥ 0.375 mm on 1 oz copper (VSYS/VMCU 0.5 mm). That is tighter than at 730 mA but still around the ~1 A the earlier reviews quoted for a 0.3 mm neck-down.
- **USB-C (HRO TYPE-C-31-M-12)** and the **diode-OR parts (D8/D9/D10)** are not in the cell charge path (D8–D10 only feed the MCU rail). The connector is a standard 16-pin mid-mount used well above 1 A.
- **Battery holder (MPD BH-18650-PC):** the datasheet does not state a current rating. The contacts are nickel-plated stainless spring and nickel-plated steel PC pins, the sort routinely used at 1–2 A; 0.9 A is a light load for them.
- **Cell:** the BOM calls for a typical 18650 (flat or button top; protected cells up to ~69 mm fit the holder), usually 2000–3500 mAh. 0.9 A is about 0.26–0.45 C, which is a normal and conservative charge rate for those cells. Do not use a much smaller or badly worn cell.

**JLC / checks.** No new extended part (still 12 extended types, of which 11 carry the ~$3.07 Economic-PCBA loading fee; the TP4056 C16581 is a *Preferred* extended part with no fee, see the rev 4.3 review). JLC-placed parts **$7.43 per board** at live qty-10 prices (was $7.50 on the rev 4.2 build; the 1.2k is $0.001 more than the 1.5k, the rest is price drift). ERC **0 errors** (the same 2 accepted PE0/PE1 warnings). DRC **0 errors, 0 unconnected pads, 0 schematic-parity issues** (the same 58 cosmetic silkscreen warnings). `jlc_cpl_fit.py --check` OK (0603 resistors need no CPL correction). Case fit **0 interferences** (closest still the LEDs in the light tunnels, 0.60 mm). The 3D previews that show the title (`previews/pcb_top.png`, `previews/pcb_closeup_led_bar.png`) were re-rendered in the rev 4.3 review and now show "FM RADIO v4.3"; the other close-ups don't include the title and are otherwise unchanged.

**Not verifiable without hardware:** actual charge current, how much the TP4056 throttles in the closed case, charge time, VBUS current from a given charger, and Q2's drop while charging.

### Design review (rev 4.3, 2026-11-10)
An independent, from-scratch review of rev 4.3, focused on the new ~900 mA charge current but covering the whole design. **No hardware errors were found. The schematic, PCB, Gerbers, JLC BOM/CPL, centroid, .pos and case are unchanged** (BOM/CPL/centroid/.pos byte-identical after regenerating with `JLC_CORR`; Gerbers identical apart from timestamps). Changes are documentation, cost accounting and preview images only.

**How it was checked**
- Fresh `kicad-cli sch export netlist`: **242 nodes, all 225 connected pin assignments match `scripts/design.py`, 0 mismatches**, and every unconnected pin is intentionally NC. Every PCB pad's net (pcbnew) matches `design.py` too (the 6 SW3 "MP" retention pads are unnumbered and netless, as intended).
- Pinouts re-read from the cached datasheets and compared with the netlist pin functions: TP4056 ESOP-8 (1 TEMP, 2 PROG, 3 GND, 4 VCC, 5 BAT, 6 STDBY, 7 CHRG, 8 CE, EP GND), DW01A (1 OD, 2 CS/VM, 3 OC, 4 TD, 5 VCC, 6 GND), FS8205A SOT-23-6 (1 S1, 2/5 D, 3 S2, 4 G2, 6 G1), AO3401A / AO3400A (1 G, 2 S, 3 D), XC6206 SOT-23 (1 VSS, 2 VOUT, 3 VIN), CH340K ESSOP-10 (1 UD+, 2 UD−, 3 GND + EP, 4 DTR#, 5 CTS#, 6 RTS#, 7 VCC, 8 TXD, 9 RXD, 10 V3), USBLC6-2SC6 (1/6 I/O1, 2 GND, 3/4 I/O2, 5 VBUS), ATmega328PB TQFP-32 (all 32 pins), USB-C A/B pins, PJ-320D-4A, SIQ-02FVS3, RRD-102. All correct.
- **R3 = 1.2k:** the TOPPOWER REV 2.4 table (p.9) lists 1.2k = 900 mA (formula 1100/R = 917 mA). PROG pin current 1 V / 1.2k = 0.83 mA (abs max 1.2 mA), BAT pin abs max 1.2 A. OK. Trickle (cell < 2.9 V) ≈ 90 mA, termination ≈ 90 mA.
- **Charge-path copper at ~920 mA:** VBUS, VBAT, BAT_P, BATN, GND tracks are 0.5 mm with short 0.375 mm sections (longest: VBAT ~30 mm, BAT_P ~19 mm at 0.375 mm). 0.375 mm on 1 oz outer copper carries ~1.2 A at a 10 °C rise (IPC-2221) and adds only ~25 mΩ over 19 mm. GND pours on both layers. OK. U1's exposed pad has 3 × 0.3 mm GND vias into the B.Cu pour.
- **Power states traced again** (battery only, USB only, both, switch off/on, programming with the switch off, button held, reversed cell with/without USB, over-discharge, dead short): same conclusions as the rev 4.2 review; nothing in rev 4.3 changes them. The DW01A still can't false-trip at the end of charge (it sees VBAT − BATN ≤ 4.242 V vs its 4.25 V minimum trip).
- **Logic levels / sensing:** BAT_ADC 0.86 V max (internal 1.1 V reference ≥ 1.0 V), BTN_SENSE ≤ 2.9 V, CHRG_SENSE ≈ 0.5 V when charging (V_IL 0.99 V), I2C low ≈ 0.6–0.7 V, CH340K TXD weak-high (~3.4 V idle with R19), RESET peak ~8.3 V (13 V rating). LEDs 0.4–0.85 mA (bar) and ~3 / 2.4 mA (charge). OK.
- **JLC:** every LCSC number re-looked-up live: manufacturer part, package and value match `design.py` for all 35 BOM lines. `jlc_cpl_fit.py --check` OK. ERC 0 errors (2 accepted PE0/PE1 warnings). DRC 0 errors / 0 unconnected / 0 parity (58 waived silkscreen warnings). Board thickness 1.6 mm. Case: `case_params.scad` regenerated from the board is byte-identical, fit re-run with **0 interferences** (closest 0.60 mm, LEDs in the tunnels).

**Corrected (no hardware change)**
| # | Problem | Fix |
|---|---|---|
| 1 | Cost text said 12 extended part types / ~$36 in fees. The TP4056 (C16581) is a JLC **Preferred** extended part, which has **no** Economic-PCBA loading fee (JLC PCBA FAQ). | README and `cost_summary.json` now say 11 charged types, ~$34 (≈$31 with SW1 hand-soldered; JLC doesn't charge a loading fee for through-hole parts). `make_fab.py` now reports fee-bearing types separately. |
| 2 | `pcb_top.png` and `pcb_closeup_led_bar.png` still showed "FM RADIO v4.2". | Re-rendered from the rev 4.3 board with `kicad-cli pcb render` at the same framing. |
| 3 | README status lines said rev 4.3 had no review of its own, and the rev 4.2 "decision" item still read as current (R3 = 1.5k). | Updated; the old item is marked superseded. |

**Risks and options (not changed: judgment calls)**
1. **Cell heating while charging (new emphasis at 900 mA).** U1 sits on the top side partly over the **+ end of the 18650** (bottom side): its body spans x = 4.3–11.7 mm, the cell x ≈ 9.8–28.3 mm, and the holder's + pad is ~2 mm below U1 at y = 75.4 mm. At the start of a charge it can dissipate ~1.7–2.0 W, the die may run up to its ~140 °C regulation point, and the board around it gets hot inside the closed case. The TP4056 **TEMP pin is grounded** (no cell NTC), so nothing limits charging on cell temperature. Li-ion cells are normally charged at 0–45 °C. **On the first board, measure the cell surface at the + end during the first 30 min of charging a flat cell, with the case closed.** If it goes above ~45 °C, go back to **R3 = 1.5k (C22843, 0603WAF1501T5E, the rev 4.2 part: ~730 mA, ~1.3 W)** or 2.4k (~460 mA). A cell NTC on TEMP would need a layout change (not done).
2. **More thermal vias under U1** (e.g. 5–6 instead of 3) would lower the die temperature a little and reduce throttling, but they also push more heat into the bottom pour right next to the cell. Left as is.
3. **CH340K DTR# configuration pull-down.** WCH: a 4.7k pull-down on DTR# during enumeration makes the CH340K ask the host for more bus current in its configuration descriptor. Without it, it asks for the default (low) budget. This only matters for hosts or hubs that enforce power budgets; the board draws ~0.95 A while charging either way, which no USB data port's budget covers. Optional, not added (it would also cost ~1 mA from VBUS whenever DTR# idles high).
4. **USB source.** Unchanged from the rev 4.3 notes: ≥ 1 A charger; a laptop USB 2.0 port (500 mA) will be overloaded. 2.4k is the low-current option.
5. **ATmega328PB stock** is still 735 at LCSC (live check). The ATmega328P-AU fallback (C14877) drops in.
6. Everything in "Only a real board can confirm" (rev 4.2/4.1) still applies, plus the actual charge current, throttling, charge time and cell temperature.

### What changed in rev 4.2 (battery reverse-polarity protection, 2026-11-10)
Inserting the 18650 backwards no longer damages the board. In rev 4.1 a reversed cell drove large currents through the DW01A/FS8205A and TP4056 internal diodes and could kill the charger, protection IC/FETs, regulators and MCU.

| Ref | Part | LCSC (JLC library, live stock 2026-11-10, price @1) | Connection |
|---|---|---|---|
| Q2 | **AO3401A** P-MOSFET, SOT-23 (AOS) | **C15127**, Basic, 1,635,833, $0.094 | D = BAT_P (holder + contact, BT1 pin 1), S = VBAT, G = Q2_G |
| Q3 | **AO3400A** N-MOSFET, SOT-23 (AOS) | **C20917**, Basic, 990,950, $0.087 | D = Q2_G, S = BATN (cell −, BT1 pin 2), G = Q3_G |
| R23 | 10k 0603 | C25804, Basic (already on the board) | BAT_P → Q3_G (gate resistor, no DC current) |
| R24 | 1M 0603 | C22935, Basic, 4,069,811 | VBAT → Q2_G (Q2 gate pull-up) |

Key datasheet values (AOS AO3401A rev 3.1 / AO3400A): AO3401A V_DS −30 V, V_GS ±12 V, I_D −4 A, V_GS(th) −0.5…−1.3 V, R_DS(on) < 60 mΩ at −4.5 V and < 85 mΩ at −2.5 V (47/60 mΩ typ), I_DSS ≤ 1 µA, body diode 2 A. AO3400A V_DS 30 V, V_GS ±12 V, V_GS(th) 0.65…1.45 V, R_DS(on) < 48 mΩ at 2.5 V. Max V_GS in this circuit is 4.24 V (full cell), so **no gate zener is needed**.

**Topology and why.** Q2 is a high-side P-FET between the holder's + contact and *every* other battery node: VBAT = TP4056 BAT, DW01A VCC (through R4), C2, SW1 and SW2 (and so VSYS, the ADC divider and the D2/D10 battery-check path). It has to be on the high side: the low side already carries the DW01A/FS8205A pack protection, and a FET there would sit inside the DW01A's VSS/CS reference. A low-side N-FET gated from VBAT was rejected too, because the TP4056 drives VBAT whenever USB is plugged in and would switch that FET on even with a reversed cell. For the same reason Q2's gate isn't simply tied to BATN or GND. With USB plugged in and a reversed cell, VBAT would sit above BATN/GND and could bias Q2 partly on (worst case a ~80 mA trickle-charge loop through the reversed cell, with ~0.4 W in Q2). Instead, **Q3 looks only at the cell itself** (gate on the + contact, source on the − contact):
- **Cell inserted correctly:** Q3 V_GS = +V_cell → Q3 on → Q2 gate pulled to BATN → Q2 V_GS = −V_cell (−2.5…−4.2 V) → Q2 fully on. A MOSFET channel conducts both ways, so the 730 mA TP4056 charge current flows backwards through Q2 just like the load current does. The DW01A trip points are unchanged: it still senses VBAT−BATN (at most ~2.6 mV of Q2 drop at radio load), and its over-current/short sensing across the FS8205A (CS vs VSS) isn't in Q2's path. The battery ADC and battery-check button see the same VBAT as before (±3 mV). If the DW01A cuts the FS8205A (over-discharge), Q2 stays on, because its control is the cell itself, not GND, so the charger can still recover the cell.
- **Cell reversed, no USB:** Q3 V_GS = −V_cell → off. R24 holds Q2's gate at its source → Q2 off, and its body diode (anode at the + contact, which is now the cell's negative end) is reverse biased. The holder's + contact now touches only Q2's drain and, through R23, Q3's insulated gate, so **there is no current path through the board** (leakage ≤ ~1 µA: Q2 I_DSS plus gate leakage). VBAT, VSYS, the DW01A, the TP4056, the regulators and the MCU just float together with the cell's − contact, and none of them sees any voltage. The only copper that goes negative is the short BAT_P trace (Q2 drain, R23, Q3 gate). Q2 V_DS = −4.2 V max (rated −30 V) and Q3 V_GS = −4.2 V max (rated ±12 V).
- **Cell reversed with USB plugged in:** the TP4056 drives VBAT to ~4.2 V, but Q3 doesn't look at VBAT, so it stays off and Q2 stays off (V_GS = 0, V_DS up to −8.4 V, rated −30 V). No current flows into the cell. The radio won't turn on, and the charge LEDs behave as if no cell were fitted (the TP4056's usual no-battery flicker). Take the cell out and turn it round. Nothing needs replacing.

**Trade-offs.** Added series drop with the cell fitted correctly: **typ. ~35-45 mV, max 62 mV at the 730 mA charge current** (≤ 85 mΩ). That's 45 mW in Q2, nothing to worry about thermally. At radio load (20-30 mA) the drop is **≤ 2.6 mV**. The TP4056 regulates its BAT pin (VBAT), so during CC charging the cell runs ≤ 62 mV behind. At termination (C/10 ≈ 73 mA) the difference is ≤ 6 mV, so the cell ends ~6 mV short of 4.2 V (≈0.5 % capacity), and charging takes a minute or two longer. **Standby drain +4.2 µA** (R24, always while a cell is fitted; total with the DW01A and the TP4056 BAT pin ≈ 7-9 µA, about 5-7 mAh/month against a typical 18650's 2-3 %/month self-discharge). The extra 60-85 mΩ in the short-circuit loop slightly lowers the short current, so a hard short may trip the DW01A's 150 mV over-current detector (7-20 ms) instead of its short detector (0.4 ms). It still disconnects, but see "Design review (rev 4.2)": during a hard short Q2 runs partly on its body diode for up to the 7-20 ms over-current delay, so a short is a stress event for Q2 (and, as before, for the FS8205A). A cell run below ~1.5 V (already damaged by Li-ion standards) may not switch Q2/Q3 fully on and may not start charging.

**Layout.** Q2 sits next to the TP4056 and the holder's + pad (USB end, top side), Q3 sits by the DW01A/FS8205A near the holder's − pad (jack end), and R23/R24 sit at the left edge below R3. BAT_P is in the 0.5 mm Power net class. The Q2_G/Q3_G gate lines (0.25 mm, ~90-110 mm long) carry no DC current. **No part that touches the case moved** (USB-C centred, LED bar, switch, jack, wheel, battery holder and button are unchanged), so `case/case_params.scad` is byte-identical to rev 4.1, and the case STLs and thickness (43 x 92 x 33.4 mm) are unchanged. The board was re-routed (Freerouting). The TP4056 centre thermal via is now placed before routing, and `stitch_gnd.py` adds a second, half-pitch stitching grid, for 89 stitching vias + 3 TP4056 pad vias (102 GND vias in total). **Silkscreen:** large 3 mm **+** and **−** marks (and "BAT+"/"BAT−") on the bottom, in the free strips on both sides of the holder at each end, so they stay visible with the holder fitted. Smaller + / − marks on the top next to the holder's solder pads. The title now reads "FM RADIO v4.2". Previews: `previews/pcb_closeup_reverse_polarity.png`, `previews/pcb_closeup_polarity_marks_bottom.png`, and JLC footprint overlays `cpl_overlay_Q2.png` / `cpl_overlay_Q3.png`.

**JLC.** Both FETs and both resistors are Basic parts, so there are no new extended-part fees (still 12 types, about $36 per order). CPL corrections from `jlc_cpl_fit.py`: Q2 (C15127) +0.071 mm / +180°, Q3 (C20917) +0.021 mm / +180° (EasyEDA SOT-23 origin = pad-bbox centre, pins 1/2 on the right). The check passes with all 3 pads on their KiCad pads. **Cost:** JLC-placed parts **$7.50 per board** (was $7.28). +$0.185 is the four new parts (Q2 $0.094, Q3 $0.087, R23/R24 $0.004), and the rest is live LCSC price drift (mainly the 22 µF C8).

**Checks (rev 4.2):** ERC 0 errors (the same 2 accepted PE0/PE1 warnings). DRC **0 errors, 0 unconnected pads, 0 schematic-parity issues** (58 cosmetic silkscreen warnings, see "Board at a glance"). Min track 0.187 mm (≥ 0.15). Tracks/vias ≥ 0.75 mm from the board edge (autorouter 0.45 mm keep-out, DRC 0.3 mm rule). Case fit **0 interferences** (closest to the light-tunnel walls: the LEDs inside them at 0.60 mm). `jlc_cpl_fit.py --check` OK.

**Not verifiable without hardware:** the polarity behaviour is from datasheet analysis only. On the first board, (1) measure the Q2 drop while charging (expect < 60 mV between the holder + pad and the TP4056 BAT pin), (2) insert a cell backwards for a second, with and without USB, and check that VBAT (TP4056 pin 5) stays near 0 V measured against the holder's − pad and nothing gets warm, and (3) measure the standby current (≈ 7-9 µA). The AO3401A/AO3400A R_DS(on) at 2.5-4.2 V gate drive is datasheet-typical, and the TP4056 no-battery LED pattern with a reversed cell varies by TP4056 clone.

### Design review (rev 4.2, 2026-11-10)
A second, independent review of rev 4.2 done from scratch, as if by someone who hadn't designed it. Sources: a fresh `kicad-cli sch export netlist` (61 nets; all 242 pin-to-net assignments match `scripts/design.py`, 0 mismatches), the pads and tracks read from `openald.kicad_pcb` with pcbnew, and the datasheets cached on the build machine (`/workspace/tools/ds`, `/workspace/ds`). **Result: no hardware errors found, so the schematic, PCB, Gerbers, BOM/CPL/centroid/.pos, case and previews are unchanged and this stays rev 4.2.** The only changes are three README corrections, listed below.

#### Corrected (documentation only, no hardware change)
| # | Severity | Problem | Fix |
|---|---|---|---|
| 1 | Low (firmware spec) | The firmware spec muted the radio below a 3.10 V cell. The MCU rail is about 0.26 V below the cell (D8 B5819W ~0.25 V at ~5 mA, plus the U6 dropout), so at 3.10 V the MCU sees about 2.84 V. The BODLEVEL=101 (2.7 V) trip point is **2.5-2.9 V** (ATmega328PB DS40001906A, Table 33-7). On a high-BOD chip the MCU would sit in reset from a cell of about 3.16 V, never mute the radio, and the cell would run down to the DW01A cut-off. | Cut-off raised to **3.25 V** (MCU ≈ 3.0 V) in the firmware spec and the power-path note. Keep BOD at 2.7 V. |
| 2 | Low (assembly) | The MPD BH-18650-PC's two pins are symmetric (72.9 mm apart), so the holder can be soldered in backwards. Electrically that is now harmless (rev 4.2), but the radio would only run with the cell inserted against the holder's own markings. Also, the KiCad library footprint's two 3.2 mm locating holes are offset 8.445 / 8.845 mm from the pins, while the MPD Rev G drawing (77.7 mm body, holes 10.68 mm from the − end, 55.61 mm apart) puts them about 0.3-0.6 mm differently. The holes are only for optional 2-56 screws, which this design doesn't use, so this doesn't matter. | Hand-assembly table: fit the holder's moulded + end (flat contact) on the square pad at the USB-C end, and check it with a meter. |
| 3 | Info (accuracy) | The rev 4.2 text said "Q2 handles 27 A pulsed" for a hard short. In fact, in a dead short of VBAT/VSYS to GND, VBAT−BATN collapses to I x R(SW1 + traces + FS8205A) ≈ 1.5-2 V. Q2's gate is at BATN, so Q2 drops out of full enhancement and conducts partly through its body diode (V_SD up to ~1 V, AO3401A datasheet). Estimate: ~10 A and ~10 W in Q2 until the DW01A's over-current delay ends (130-170 mV threshold, 7-20 ms; the DW01A still works at a ~2 V supply). That's a single-event stress inside the SOT-23 rating envelope, not a design error. A hard short can only come from an internal fault (no battery node is exposed), and the FS8205A saw a similar ~10 W / 7-20 ms event in rev 4.1. | Text corrected. Listed under "only hardware can confirm". |

#### Decision for you (not changed)
- *(Superseded: rev 4.3 sets R3 = 1.2k, ~900 mA; the same 2.4k option still applies.)* **USB charge current vs. a PC's USB 2.0 port.** R3 = 1.5k sets ~730 mA (TP4056: I = 1100 x 1 V / R_PROG). With 5.1k CC pull-downs the board is a "Default USB Power" sink, which is **500 mA from a USB 2.0 port** (900 mA from USB 3.x). Charging a flat cell from a laptop USB-A port while programming therefore draws ~755 mA, over spec. Most ports tolerate it, but a strictly current-limited port could sag VBUS while you upload (the CH340K needs VCC ≥ 4.0 V). Wall chargers are fine. If you program from a PC a lot, change **R3 to 2.4k (C22940, basic) for ~460 mA**: charging takes ~7 h instead of ~4.5 h for 3000 mAh, and nothing else changes. I left it at 730 mA because it's a charge-time vs. compliance choice.

#### Verified OK (by datasheet unless noted)
- **Reverse-polarity block (Q2 AO3401A C15127 / Q3 AO3400A C20917, R23 10k, R24 1M)**: SOT-23 pin 1 G, 2 S, 3 D in the AOS datasheets, the KiCad symbols and the EasyEDA symbols for both LCSC parts. Netlist: Q2 D = BAT_P (BT1 pin 1, square pad), S = VBAT, G = Q2_G; Q3 D = Q2_G, S = BATN, G via R23 from BAT_P; R24 VBAT→Q2_G. BAT_P touches only Q2 drain and R23. Node voltages:
  - *Cell correct:* Q3 V_GS = +V_cell, Q2 V_GS = −V_cell (≤ 4.24 V vs ±12 V). Q2 R_DS(on) ≤ 85 mΩ at −2.5 V, so ≤ 62 mV at 730 mA. The DW01A senses VBAT−BATN, the same node the TP4056 regulates (float 4.158-4.242 V < V_OC min 4.25 V), so there are no false trips.
  - *Reversed, no USB:* Q3 V_GS = −4.2 V (off). Q2 V_GS = 0 (R24), its body diode is reverse biased, and V_DS = −4.2 V. Every other node floats with BATN, and there is no current path.
  - *Reversed, USB in:* VBAT = 4.2 V above GND ≈ BATN. Q2 V_DS ≈ −8.4 V (rated −30 V), Q3 V_DS ≈ 4.2 V, Q3 V_GS = −4.2 V, no current in R23/R24. DW01A 4.2 V supply (abs max 10 V), TP4056 BAT 4.2 V.
  - *Reversed insertion while USB is in and no cell was fitted:* Q2/Q3 can latch on through leakage, putting 4.2 V on the empty holder, just like rev 4.1. On insertion, Q3 turns off within a few µs (R23 x 630 pF). Q2 turns itself off as soon as VBAT falls to ~0.9 V above its gate (held at BATN), so only C2's charge (~85 µJ) and then ≤ ~73 mA of TP4056 trickle current (for ~1 ms, R24 x Ciss) reach the cell. No node goes below GND.
  - *Over-discharge:* the DW01A opens the FS8205A, and Q2 stays on because its drive comes from the cell. Charging still recovers the cell through the FS8205A body diode as in rev 4.1 (DW01A 0 V-charge ≥ 1.2 V). R24 then draws ~2.5 µA directly from the cell, alongside the DW01A's ≤ 4 µA power-down current.
- **USB-C J1 (HRO TYPE-C-31-M-12)**: CC1/CC2 each 5.1k to GND. D+ A6/B6 and D− A7/B7 tied. VBUS A4/A9/B4/B9. Shell to GND. Pad positions read from the PCB. **USBLC6-2SC6 (ST)**: 1/6 D+, 3/4 D−, 2 GND, 5 VBUS. Its VBUS-GND diode also clamps hot-plug ringing on VBUS.
- **TP4056 (TOPPOWER REV 2.4)**: TEMP grounded (disables NTC, p.4 pin description), CE = VCC, PROG 1.5k (~730 mA). nCHRG/nSTDBY are open-drain and rated to 10 V independent of VCC, so D7/PC2 can't back-feed VBUS through them. EP to GND with 3 vias. Thermal regulation at 145 °C.
- **DW01A (Rev B) / FS8205A**: DW01A 1 OD, 2 VM/CS, 3 OC, 4 TD, 5 VCC (100 Ω + 100 nF), 6 GND = BATN, CS 1k to pack −. FS8205A SOT-23-6 pins 1 S1, 2/5 D, 3 S2, 4 G2, 6 G1 (datasheet drawing = EasyEDA C2830320 symbol). S1 = BATN/G1 = OD, S2 = GND/G2 = OC: correct.
- **XC6206P332MR (Torex)**: SOT-23 1 VSS, 2 VOUT, 3 VIN for U5 and U6. VIN abs max 7 V, operating 6 V; VMCU ≤ ~5.0 V. Ceramic caps OK (1 µF in, 10 µF out).
- **Diode OR**: D8 VSYS→VMCU, D9 VBUS→VMCU, D10 VBTN→VMCU, D2 VBTN→VSYS, D7 PC2→nCHRG (KiCad pin 1 = K on every one). B5819W 40 V / 1 A.
- **Power states traced**: off / no USB ≈ 7-9 µA (DW01A, TP4056 BAT, R24). Off + USB: MCU + CH340K only, VSYS ≈ D8 leakage. On: all. Button held: MCU via D10, VSYS via D2. Reversed cell: as above. The MCU is never unpowered while VBUS or +3V3R is up, so LED, GPIO and UART pins can't back-feed. The I2C pull-ups go to +3V3R (firmware must not enable the pull-ups while the radio is off; already noted).
- **ATmega328PB-AU (DS40001906A)**: all 32 TQFP pins match the datasheet pinout, including PE0 = GND, PE1 = +3V3 (ERC's 2 intentional warnings), PE2/PE3 = ADC6/7 spare, AVCC = +3V3, AREF 100 nF. Abs max: any pin −0.5 V to VCC+0.5 V, RESET −0.5 V to +13 V. Max sensed inputs: BTN_SENSE 2.9 V at VCC 3.3 V, BAT_ADC ≤ 0.86 V vs V_INT 1.0-1.2 V, ADC source 9.6k (≤ 10k recommended). PC1 high at a 3.0 V cell = 2.04 V > V_IH 0.6 VCC. Auto-reset pulse below V_IL2 (0.1 VCC) ≈ 0.27 ms ≫ minimum. 8 MHz needs ≥ ~2.4 V.
- **CH340K (WCH CH340DS1)**: ESSOP-10 pins 1 UD+, 2 UD−, 3 GND (+EP), 4 DTR#, 5 CTS#, 6 RTS#, 7 VCC, 8 TXD, 9 RXD, 10 V3, matching the KiCad symbol and the EasyEDA C968586 symbol. 5 V mode: VCC 4.0-5.3 V, V3 = 100 nF only. VIH 2.3 V (MCU TX 3.3 V OK). TXD/RXD/RTS# have built-in back-flow diodes; TXD is weak-high. DTR# is push-pull without a diode, but it only drives C19.
- **RRD-102 (RDA5807M)**: application circuit (spec p.4) 1 GND, 2 R OUT, 3 L OUT, 4 RCLK NC, 5 ANT, 6 SDA, 7 SCL, 8/9 NC, 10 VDD (10 Ω + 47 µF + 100 nF recommended, 22 µF used). Footprint pins 1-5 and 6-10 face each other, pin 1 opposite pin 10. I2C low level at the MCU with 1k series + 4.7k pull-up ≈ 0.6-0.7 V < V_IL 0.99 V.
- **PJ-320D-4A**: KiCad pads R2/R1/T/S sit 3.2/6.2/10.2/11.3 mm from the mouth = datasheet pins 4/3/2/1. Tip = HP_L, R1 = HP_R, R2 + S = common (3-pole and both 4-pole standards).
- **SIQ-02FVS3 (Mitsumi)**: terminals A, S, C, B (A/B encoder, S slide-push, C common) on 2.53/2.95/2.53 mm pitch match the footprint order after the −90° rotation. Rating 0.5 mA / 5 V vs ≤ 0.17 mA internal pull-ups.
- **SW1 SK-12E12-G5 / SW2 EVQ-P7A01P / LEDs / caps**: as in the rev 4.1 review. DC-bias derating checked where it matters: C10/C11 100 µF 6.3 V X5R at ~1.5 V bias → ~60-70 µF, low-frequency corner into 32 Ω ≈ 75-85 Hz. C5/C18 10 µF 10 V at 3.3 V → ~5-6 µF (XC6206 needs ≥ 1 µF). C1/C2 10 µF 25 V at 4-5 V → ~7 µF.
- **PCB**: DRC 0 errors / 0 unconnected / 0 parity (58 waived silkscreen warnings). Power nets ≥ 0.375 mm (VBUS, VBAT, BAT_P, BATN, GND), VSYS/VMCU 0.5 mm, enough for 730 mA charge on 1 oz copper. GND pours on F.Cu and B.Cu with 102 GND vias. USB pair 0.2 mm, 17.8/23.1 mm. Q2_G/Q3_G are long (107/89 mm) but carry no DC current and are driven hard whenever a cell is fitted correctly. `jlc_cpl_fit.py --check`: correction table OK. Q2/Q3/U2/Q1/U1/U3/U7 EasyEDA pads land on the KiCad pads (`fab/jlc_cpl_fit.json`, `previews/cpl_overlay_*.png`).
- **Case**: `case_params.scad` is byte-identical to rev 4.1, thickness unchanged (43 x 92 x 33.4 mm), `case_fit_report.txt` 0 interferences.
- **Live JLC stock (2026-11-10 evening)**: ATmega328PB-AU C132230 **735** (low). Fallback ATmega328P-AU C14877 21,328, now a JLC *preferred* extended part (no extended-part fee). CH340K 32,944, AO3401A 1,632,471, AO3400A 981,994, SIQ-02FVS3 1,298, PJ-320D-4A 1,527, EVQ-P7A01P 3,478, TP4056 104,993, DW01A 92,820, FS8205A 186,310, USBLC6 27,939, XC6206 485,927, B5819W 720,800, TYPE-C-31-M-12 275,446, SK-12E12-G5 15,529, KT-0603G 309,093. No part changes, cost unchanged ($7.50 per board for the JLC-placed parts, prices drift day to day).

#### Only a real board can confirm
1. Reverse polarity: insert a cell backwards for a second, with and without USB, and also *after USB has been plugged in with the holder empty*. VBAT (TP4056 pin 5) must stay ≥ 0 V vs the holder's − pad, and nothing may get warm.
2. Q2 drop while charging (< 60 mV, holder + pad to TP4056 pin 5) and standby current (≈ 7-9 µA).
3. Hard-short behaviour (optional, destructive-risk test, only on a spare board): the DW01A should disconnect within ~20 ms.
4. Headphone jack: check tip = left with a plug and a meter before soldering U4 (the PJ-320D pin-to-contact mapping comes from drawing geometry).
5. USB enumeration, auto-reset and Optiboot upload, ideally while charging a flat cell from a laptop port (see the R3 decision above).
6. The rev 4.1 list below still applies (ADC calibration, L/R, audio level, thermal while charging, RESET undershoot, mechanical fit).

### Design review (rev 4.1, 2026-11-10)
A full, skeptical review of rev 4 against the real KiCad netlist (`kicad-cli sch export netlist`, all 232 pin-to-net assignments compared with `scripts/design.py`: 0 mismatches), the routed PCB and the manufacturers' datasheets. Three genuine problems were found and fixed. **Nothing moved on the board**: same placement, same routing, same CPL (byte-identical), same case (`case_params.scad` byte-identical).

#### Fixed
| # | Severity | Problem | Fix |
|---|---|---|---|
| 1 | **Medium** (wrong/clipped battery readings on some chips) | Battery divider R8/R9 = 100k/33k put a full cell (TP4056 float 4.158-4.242 V) at **1.04-1.05 V** on PC0. The ATmega328PB internal 1.1 V reference is only guaranteed **1.0-1.2 V** (DS40001906, VINT, p.359), so on a low-reference part the ADC clips at 1023 near full charge and the bar can't tell 4.0 V from 4.2 V. Source impedance was 25k (the datasheet optimises the ADC for ≤ 10k, DS40001906 p.295). | **R8 = 47k (C25819), R9 = 12k (C22790, basic)**. Full cell = 0.86 V (14 % headroom below the 1.0 V worst case), source impedance 9.6k, C6 100 nF kept. New formula below. |
| 2 | **Medium** (false "button pressed", bar lights by itself when warm) | When SW2 is open, VBTN is only held down by R6+R7 = 147k. D2 (VSYS→VBTN) and D10 (VMCU→VBTN) are reverse-biased by ~4-4.7 V, and the B5819W leaks **~5 µA each at 25 °C and roughly 10x that at 75 °C** (JSCJ B5819W datasheet, reverse-characteristics curve; max 1 mA at 40 V). 10 µA x 147k ≈ 1.5 V on VBTN → **~1.0 V on PC1 at room temperature, already above VIL max (0.3 VCC = 0.99 V)**, and a solid "high" in a warm pocket. | **R6 = 4.7k (C23162), R7 = 10k (C25804)**, same 0.68 ratio, both already on the board. VBTN now sits at ~0.15 V (25 °C) / ~0.6 V (≈60 °C) with the button open. Pressing it costs 0.29 mA, only while held. Firmware can also read PC1 as ADC1 for extra margin (threshold ≈ 1.3 V). |
| 3 | **Low** (EMI/RF and charger heat) | Only **10 GND vias** joined the top and bottom GND pours, and the TP4056 exposed pad (up to ~1.3 W while charging at 730 mA) had 2 vias. | `scripts/stitch_gnd.py` (now part of `run_all_pcb.sh`) adds **92 GND stitching vias** (0.6/0.3 mm, 2.5 mm grid, only where the via sits fully inside both pours and outside every top-side courtyard) plus **1 more thermal via in the TP4056 pad** (103 GND vias total). DRC re-run clean. |

Also changed: silk now reads "FM RADIO v4.1". Cost impact: **+$0.0002 per board** (12k replaces 33k/100k lines; no new extended parts, still 12 extended types / about $36 per order).

#### Checked and OK (datasheet-verified unless noted)
- **Netlist**: every pin of U1, U2, Q1, U3, U5-U8, J1, J2, SW1-SW3, U4, BT1, J3 maps to the intended net (pin names taken from the KiCad symbols and compared with the datasheets below).
- **USB-C (HRO TYPE-C-31-M-12, C165948)**: CC1 (A5) and CC2 (B5) each 5.1k to GND (sink, default USB power); D+ = A6/B6, D- = A7/B7 tied for both orientations; SBU open; shield to GND; 10 µF on VBUS (USB limit).
- **TP4056 (TOPPOWER datasheet REV 2.4)**: pin 1 TEMP to GND (disables NTC sensing, as the datasheet allows), pin 2 PROG 1.5k → I = 1100 x 1 V / 1.5k ≈ **730 mA** (table: 1.4k = 780 mA, 1.6k = 690 mA) = 0.2-0.25 C for a 3000-3500 mAh 18650; pin 4/8 VCC/CE = VBUS (enabled); pin 5 BAT to the cell + (correct for low-side protection); nCHRG/nSTDBY open-drain to the LEDs; EP to GND with now 3 vias. Thermal: up to ~1.3 W at a deeply discharged cell; the chip's own thermal regulation lowers the current if it gets hot, which only makes charging slower.
- **DW01A + FS8205A**: DW01A pin 1 OD, 2 CS, 3 OC, 4 TD (NC), 5 VCC via 100 Ω (R4) with 100 nF (C3) to its pin 6 GND = cell − (BATN), CS through 1k (R5) to pack − (GND) - matches the DW01A datasheet application circuit. FS8205A SOT-23-6 (datasheet drawing): 1 S1, 2/5 common drain, 3 S2, 4 G2, 6 G1. S1 = BATN with G1 = OD (discharge FET), S2 = GND with G2 = OC (charge FET): correct. Trip points 4.30 V / 2.4-2.5 V / 150 mV over-current (≈ 3 A with ~50 mΩ of FETs).
- **XC6206P332MR (Torex datasheet)**: SOT-23 pin 1 VSS, **2 VOUT, 3 VIN**, which both U5 and U6 use. VIN max 6.0 V operating (VMCU ≈ 4.7 V from USB), 1 µF in / 10 µF ceramic out. Dropout is tens of mV at this radio's 10-30 mA.
- **Diode OR / orientation** (KiCad pad 1 = cathode, matched to the EasyEDA cathode pad by `jlc_cpl_fit.py`): D8 VSYS→VMCU, D9 VBUS→VMCU, D10 VBTN→VMCU, D2 VBTN→VSYS, D7 PC2→nCHRG. All correct.
- **What is powered in each state** (nets traced): switch off, no USB: only the DW01A (~3 µA), the TP4056 BAT pin (≤ 2 µA) and, since rev 4.2, the Q2 gate pull-up R24 (4.2 µA). Switch off + USB: TP4056, CH340K, U6 → MCU; VSYS/+3V3R off (only diode leakage, see risks). Switch on: everything; USB present → D9 feeds the MCU. Button held: MCU via D10, VSYS via D2 (radio rail powered, RDA5807M stays disabled after reset).
- **Back-feed paths**: VBUS→battery only through the TP4056; MCU→radio rail blocked because the I2C pull-ups go to +3V3R and the MCU pins are open-drain (see the Wire note in "Firmware notes"); MCU→unpowered CH340K blocked inside the CH340K (WCH CH340DS1 §7.8: TXD/RXD/RTS# have built-in diodes, ≤ 150 µA in the other direction); the CH340K is never powered without the MCU (VBUS always feeds U6 through D9).
- **CH340K (WCH CH340DS1, ESSOP-10)**: 1 UD+, 2 UD-, 3 GND (+EP), 4 DTR#, 5 CTS#, 6 RTS#, 7 VCC, 8 TXD, 9 RXD, 10 V3 - matches the footprint. VCC = VBUS with 100 nF, **V3 = 100 nF only (5 V mode)**. No crystal needed. UD+ → J1 D+, UD- → J1 D-. TXD → PD0 (RXD), PD1 (TXD) → 1k → RXD: crossed correctly. **Logic levels at VCC = 5 V are safe for the 3.3 V MCU**: the CH340K TXD only drives low and has a weak ~75k pull-up behind its blocking diode (§7.8), so with R19 (10k to +3V3) the line idles at ~3.4-3.5 V, inside the ATmega's VCC + 0.5 V limit, with < 20 µA of injection. MCU TXD high (3.3 V) is above the CH340K's VIH min of 2.3 V at 5 V (§6.2); low with 1k and ≤ 300 µA pull-up current stays < 0.7 V (VIL max 0.9 V). DTR# is push-pull 5 V without a diode (§7.8), but it only drives C19.
- **Auto-reset**: DTR# → 100 nF → RESET, 10k pull-up (1 ms pulse) - standard Arduino. The RESET pin is rated −0.5 V to +13 V (DS40001906 p.350); the rising edge reaches ~8.3 V (OK), the falling edge briefly undershoots below −0.5 V and is clamped by the pin's ESD structure through C19 - the same as Arduino Nano/Pro Mini boards (see risks).
- **USBLC6-2SC6 (ST)**: 1/6 I/O1 = D+, 3/4 I/O2 = D-, 2 GND, 5 VBUS.
- **ATmega328PB-AU (DS40001906, TQFP-32 pinout)**: all 32 pins as in the pin map below. Pin 3 = PE0 tied to GND and pin 6 = PE1 tied to +3V3: safe on the 328PB as long as firmware never makes PE0/PE1 outputs (MiniCore leaves them as inputs), and they are the GND/VCC pins on a 328P. VCC, AVCC and AREF each have 100 nF; RESET 10k pull-up; ISP J3 = standard 6-pin AVR ISP (1 MISO PB4, 2 VCC, 3 SCK PB5, 4 MOSI PB3, 5 RESET, 6 GND). Speed grade: 8 MHz needs ≥ ~2.4 V (DS p.353, linear 4 MHz@1.8 V → 10 MHz@2.7 V), so keep **BOD = 2.7 V**. Sensed inputs never exceed VCC + 0.5 V: BTN_SENSE ≤ 0.68 x 4.24 = 2.9 V; CHRG_SENSE is isolated by D7; I2C lines are pulled to +3V3R, which can sit up to ~0.33 V above the MCU's +3V3 on a low cell (D8 drop) - inside the 0.5 V limit, through 1k + 4.7k. TWI0 (PC4/PC5), USART0 (PD0/PD1), INT0/INT1 (PD2/PD3) for the encoder, PWM on OC0B/OC0A/OC1A for the bar.
- **RRD-102V2.0 module (manufacturer spec "RRD-102V2.0 (CPU RDA5807M)")**: top view 1 GND, 2 R-out, 3 L-out, 4 RCLK (NC), 5 FM antenna, 6 SDA, 7 SCL, 8/9 GP2/GP3 (NC), 10 VDD - matches the footprint (pin 1 bottom right, 6 top left). The module carries its own 32.768 kHz crystal. Its spec confirms the rest of the circuit: it **drives 32 Ω headphones directly through series capacitors** (C10/C11, 100 µF), has internal 47k pull-ups and recommends 1k series resistors on SDA/SCL (R16/R17), recommends 10 Ω + 47 µF + 100 nF on VDD (here 10 Ω + 22 µF + 100 nF, adequate), and uses the **earphone common as the antenna through 600 Ω @ 100 MHz beads** on L, R and GND (FB1-FB3, exactly the same part value). RDA5807M VDD 1.8-3.3 V (XC6206 3.3 V minus the 10 Ω drop ≈ 3.1 V). I2C 0x10/0x11.
- **PJ-320D-4A (C95562)**: tip = L, ring 1 = R, ring 2 + sleeve = headphone common (works with 3-pole headphones and both 4-pole standards). Pad names from the KiCad library footprint, which cites the LCSC datasheet; the EasyEDA pad fit agrees 4/4.
- **SIQ-02FVS3 (Mitsumi)**: terminals A, PUSH, COM, B (datasheet) = footprint A, S, C, B; rating 0.5 mA / 5 V, the MCU's internal pull-ups draw ~0.1 mA. **EVQ-P7A01P (Panasonic)**: 1-1 and 2-2 pad pairs are internally joined, SPST between them, rated 10 µA-50 mA / 12 V. **SK-12E12-G5**: knob toward pin 3 (jack end) joins 2-3 = ON, matching the engraved ON label.
- **LEDs**: bar 0.85 mA each from 3.3 V via 1k; red/green charge LEDs ~3 / 2.4 mA from 5 V via 1k (TP4056 status pins sink up to 10 mA).
- **Capacitor ratings**: 10 µF 25 V (VBUS, VBAT), 10 µF 10 V (3.3 V rails), 22 µF 25 V, 100 µF 6.3 V (audio, ~1.5 V bias), 1 µF 50 V - all adequate. All resistors 0603 1 % 100 mW; worst dissipation is R21/R22 at ~10 mW.
- **PCB**: DRC 0 errors / 0 unconnected / 0 parity issues; power nets 0.5 mm (a few 0.38/0.3 mm neck-downs at pads: 1 oz 0.3 mm carries ~1 A, above the 730 mA charge current); USB pair 0.2 mm, 18-23 mm long (fine for 12 Mbit/s); thermal reliefs 0.3 mm gap / 0.4 mm spokes, solid connection on the TP4056 pad and the MCU/CH340K grounds; pin-1 / polarity marks on silk. JLC doesn't need fiducials for standard assembly (it adds its own tooling rails if needed). `jlc_cpl_fit.py --check`: correction table OK, every part's EasyEDA pads land on the KiCad pads.
- **Case**: `case_params.scad` is byte-identical to rev 4.0 (no part moved), thickness unchanged (43 x 92 x 33.4 mm); fit check re-run: **0 interferences**.
- **Stock (live, 2026-11-10)**: ATmega328PB-AU C132230 2,168 ($1.86 @1); ATmega328P-AU fallback C14877 22,013; CH340K C968586 33,016; USBLC6 C7519 28,286; SIQ-02FVS3 1,298; PJ-320D-4A 1,522; EVQ-P7A01P 3,478; SK-12E12-G5 15,527; 12k C22790 1,094,121 (basic).

#### Remaining risks that only a real board can settle
1. **First power-up and programming**: CH340K enumeration, Optiboot upload at 38400 baud on the internal RC oscillator, and auto-reset timing. If auto-reset is flaky, add a small Schottky from RESET (anode) to +3V3 (cathode) across R10.
2. **RESET undershoot**: the DTR# falling edge drives RESET briefly below the −0.5 V absolute maximum (limited by C19, exactly like the Arduino Nano/Pro Mini). Common practice, but not strictly inside the rating.
3. **Schottky leakage at high temperature**: with the switch off and USB in, D8 leakage lifts VSYS slightly (~0.3 V at 25 °C into the new 59k divider, more when hot), so the radio rail is not at exactly 0 V. Harmless (the RDA5807M stays disabled), but use "VSYS < 2.5 V" rather than "0 V" to detect "USB only" in firmware.
4. **SW2 inrush**: pressing the button with the switch off charges ~45 µF of rail capacitance through the EVQ-P7A contacts (rated 50 mA resistive). Brief peaks are above that rating; tactile switches usually tolerate it, but watch for contact wear.
5. **Reverse-polarity protection (rev 4.2)** is verified on paper only (see "What changed in rev 4.2"): check the Q2 drop while charging and a brief reversed insertion on the first board. Still follow the large "+" / "−" marks on the bottom silk.
6. **ADC calibration**: the internal reference is ±9 %, so calibrate once per board (measure the cell with a meter and store a correction factor in EEPROM). The D2 drop while button-powered (~0.1-0.15 V at ~0.1 mA) and the charging offset should also be calibrated.
7. **Audio level and FM sensitivity** with your headphones and cable length, and the L/R pad assignment (the manufacturer spec used here says pin 2 = R, pin 3 = L; one third-party trace swaps them - fix in firmware if needed).
8. **Mechanical**: the jack, switch, wheel and USB 3D models are datasheet approximations; print one case first. The thumbwheel overhangs the board edge, so JLC may add break-away rails for assembly.
9. **Thermal while charging inside a closed case**: the TP4056 may throttle its current; charging just takes longer.

### What changed in rev 4 (USB programming: ATmega328PB + CH340K)
| Area | Change |
|---|---|
| MCU | U3 **ATtiny84A-SSU (C144333) replaced by ATmega328PB-AU (C132230, TQFP-32 7x7)**, internal 8 MHz RC, no crystal. **ATmega328P-AU (C14877) drops in unchanged**: pin 3 (PE0) is tied to GND and pin 6 (PE1) to +3V3, which are GND/VCC on the 328P. Decoupling: 100 nF on VCC (C7), 100 nF on AVCC (C13), 100 nF on AREF (C14), plus the MCU-rail 10 uF (C18). |
| Hardware I2C | SDA/SCL now come from TWI0 (PC4/PC5) through the existing 1k series resistors R16/R17. The 4.7k pull-ups R14/R15 go to the **radio rail +3V3R**, so they can't back-feed the RDA5807M while the radio is unpowered. The ISP pins are now separate from I2C. |
| Level LEDs | LVL1/LVL2/LVL3 sit on PD5/PD6/PB1 (all hardware PWM). **LVL3 no longer shares MISO**, so D6 doesn't flicker during ISP. |
| USB serial | **U7 CH340K (C968586, ESSOP-10)**, powered from **VBUS only** (5 V mode): VCC = VBUS with 100 nF (C15) plus the existing 10 uF VBUS caps C1/C2 next to it, and V3 = 100 nF (C16). The CH340K has its own oscillator and USB pull-up, so it needs no crystal. |
| USB-C data | J1 D+ (A6/B6) and D- (A7/B7) are tied at the connector for both plug orientations. A short pre-routed pair runs to U7 (D+ 17.8 mm, D- 23.1 mm of copper including the ESD taps; locked so the autorouter keeps it). |
| ESD | **U8 USBLC6-2SC6 (C7519)** sits right at the USB-C data pins, with VBUS on pin 5. |
| UART | CH340K TXD -> MCU RXD (PD0) directly, with a 10k pull-up (R19) to the MCU rail. MCU TXD (PD1) -> **1k (R20)** -> CH340K RXD. The CH340K datasheet says its TXD/RXD pins have built-in blocking diodes: no current flows from the MCU into an unpowered CH340K's supply, and leakage is at most 150 uA. R20 limits that further. |
| Auto-reset | CH340K DTR# -> **100 nF (C19)** -> RESET, with the existing 10k (R10) pull-up. This is the standard Arduino circuit. I left out the RESET->VCC clamp diode. When DTR# goes back high, the RESET pin briefly sees about 3.3 V + 5 V ≈ 8.3 V. The ATmega RESET pin has no ESD diode to VCC (it tolerates up to 13 V for high-voltage programming), so 8.3 V is within its rating and well below the ~12 V high-voltage-programming entry. That matches Arduino Pro Mini/Nano practice. Microchip AVR042 recommends the diode mainly for noisy environments. If you want it anyway, you can bodge a small Schottky across R10 (anode RESET, cathode +3V3). *Note: DTR# is a push-pull pin with no back-feed diode, but C19 blocks DC, so it can't power anything.* |
| MCU-only 3.3 V rail | New **U6 XC6206P332MR (C5446)** powers only the MCU (+3V3). It is fed from **VMCU**, a Schottky OR of **switched VSYS (D8)**, **USB VBUS (D9)** and the **battery-check button (D10)**, all B5819W (C8598). C17 1 uF in and C18 10 uF out. The old U5 LDO now feeds only the radio and its pull-ups (**+3V3R**). See "Power path" below. |
| ISP | J3 pogo pads (DNP) are now ATmega328PB MISO (PB4) / SCK (PB5) / MOSI (PB3) / RESET (PC6) / +3V3 / GND, using the standard AVR-ISP 2x3 pinout. You only need them once, to burn the bootloader. |
| Layout | U3 and its parts moved into the old ATtiny area. U7/U8/C15/C16 sit next to the USB-C, and D8/D9/D10/U6 sit between the LDO block and the power switch. **USB-C (centred on the bottom edge), LED bar, power switch, jack, thumbwheel, battery-check button and battery holder are exactly where they were**, so `case/case_params.scad` is byte-identical to rev 3.1. The case didn't change, and neither did its thickness (43 x 92 x 33.4 mm). Silk now reads "FM RADIO v4". |
| CPL | New JLC corrections were fitted with the same EasyEDA-footprint method (`scripts/jlc_cpl_fit.py`): U3 TQFP-32 +270, U7 CH340K +270 (it sits at 90 deg on the board, so its CPL rotation is 0), U8 USBLC6-2SC6 +270, and U6 XC6206 +180 with the same 0.03 mm X nudge as U5. U3, U7 and U8 need no offset. Fit residuals are 0.22 mm (U3, TQFP land length), 0.11 mm (U7), 0.01 mm (U8) and 0.13 mm (U6). The rev 3.1 corrections for the existing parts are unchanged. Overlays: `previews/cpl_overlay_U3.png`, `_U6`, `_U7`, `_U8`. |

#### Power path (programming with the power switch off)
```
VBAT --SW1--> VSYS --+--> U5 XC6206 --> +3V3R : RDA5807M, I2C pull-ups      (radio: only when the switch is ON)
                     +--> R8/R9 --> BAT_ADC
                     +--D8--+
VBUS (USB) ----------------D9--+--> VMCU --> U6 XC6206 --> +3V3 : ATmega328PB only
VBAT --SW2 (held)--> VBTN --D10-+
                        \--D2--> VSYS   (as in rev 3: also lets the ADC see the cell while the button is held)
```
- **Switch off, USB plugged in:** VBUS powers only the MCU (through D9 and U6) and the CH340K. VSYS stays at 0 V, so the **RDA5807M, U5 and the battery divider stay unpowered**. You can upload sketches with the radio off and the battery untouched. The TP4056 still charges as usual.
- **Switch on:** VSYS powers the radio (U5) and the MCU (D8 -> U6). With USB also present, the higher of VSYS-0.3 V and VBUS-0.3 V feeds U6.
- **Switch off, SW2 held:** VBTN feeds the MCU through **one diode (D10)**, like rev 3. D2 still lifts VSYS, so the battery divider reads the cell minus one B5819W drop (**add about +0.1-0.15 V**, calibrate; rev 4.1 divider draws ~70 µA). Firmware keeps the RDA5807M powered down, as before.
- **Battery ADC stays meaningful:** BAT_ADC is still on VSYS, so it reads the cell directly when the switch is on, (cell - ~0.1-0.15 V) when only SW2 is held, and **near 0 V when only USB is powering the MCU** (a few hundred mV from diode leakage). Firmware can use that to tell "USB only, switch off" from the other states (BTN_SENSE low and V_sys < 2.5 V).
- **Cost of the diode:** with the switch on, the MCU's LDO input is VSYS - ~0.25 V, so +3V3 (MCU) starts to sag below a cell of about 3.6 V, while +3V3R (radio) holds up to about 3.45 V as before. At the firmware cut-off (3.25 V cell since the rev 4.2 review) the MCU rail is about 3.0 V, above the 2.9 V worst-case BOD trip. The ADC uses the internal 1.1 V reference, so the battery reading doesn't depend on it.
- **Battery life:** unchanged when the switch is off (the CH340K, U6 and the MCU have no battery path; only the TP4056/DW01A leakage remains, as in rev 3). With the radio on, U6 adds about 1 uA of quiescent current. The CH340K is unpowered without USB. Through the blocking diodes and R20/R19, at most tens of uA (150 uA worst case per datasheet) leak from the MCU UART pins into it, so keep `Serial` closed in normal firmware or set PD1 low/input when VBUS isn't needed.

### What changed in rev 3.1 (JLC pick-and-place fix)
JLC places each part using the **LCSC/EasyEDA footprint**, putting that footprint's origin at the CPL Mid X/Y and turning it by the CPL rotation. For several parts the EasyEDA origin or "zero" orientation differs from KiCad's, so rev 3's CPL put them in the wrong spot in JLC's preview. **Nothing on the PCB moved.** Only `fab/openald-CPL-jlcpcb.csv` changed.

| Ref | Part (LCSC) | Rev 3 CPL (X, Y, rot) | Rev 3.1 CPL (X, Y, rot) | Change | Why |
|---|---|---|---|---|---|
| J2 | PJ-320D-4A jack (C95562) | 11.50, 78.60, 270 | 11.50, 77.80, 0 | rot +90, Y -0.80 | EasyEDA has the jack mouth along -Y and its origin at the pad-group centre |
| SW1 | SK-12E12-G5 slide switch (C136720) | 35.50, 23.00, 90 | 35.50, 22.92, 0 | rot -90, Y -0.08 | EasyEDA pin row runs along Y with the knob at +X (checked against the 3D model) |
| J1 | TYPE-C-31-M-12 USB-C (C165948) | 19.00, 3.65, 0 | 19.00, 5.06, 0 | Y +1.41 | EasyEDA origin is 1.41 mm further in from the board edge (since 2026-11-12 J1 sits 0.9 mm nearer the edge: KiCad 19.00, 2.75 → CPL 19.00, 4.16) |
| SW3 | SIQ-02FVS3 thumbwheel (C2925423) | 33.60, 61.00, 270 | 31.16, 61.00, 270 | X -2.44 | EasyEDA origin is the pad-group centre, not the wheel axis |
| U2 | DW01A (C351410) | 33.40, 77.40, 180 | 33.40, 77.40, 270 | rot +90 | this LCSC SOT-23-6 has pin 1 bottom-left, unlike FS8205A Q1 (bottom-right), so the generic "+180 for SOT-23" rule was wrong for it |
| U5 | XC6206 (C5446) | 22.00, 36.50, 180 | 22.03, 36.50, 180 | X +0.03 | negligible, included for exactness |

All coordinates are in mm from the board's bottom-left corner (Y up). The drill/place origin was moved from (100, 185) to the true corner (100, 187), so every CPL Y and the Gerber/drill coordinates are now 2 mm higher than in rev 3. The Gerbers and CPL still share that origin, and the copper is unchanged. The rev 3 values in the table above have already been shifted into the new frame.

**Parts checked and unchanged:** U1 TP4056 (+270, correct), U3 ATtiny84A (+270; replaced in rev 4), Q1 FS8205A (+180), U5 XC6206 (+180), SW2 EVQ-P7A, all LEDs (D1, D3, D4, D5, D6), the Schottky diodes D2 and D7, and all passives. For the LEDs and diodes I matched polarity by function, not by pad number. The red KT-0603R (C2286) EasyEDA footprint numbers its anode as pad 1, while KiCad's pad 1 is the cathode. At rotation 0 the EasyEDA cathode lands on the KiCad cathode pad for every LED and diode.

**How the corrections were verified:**
- `scripts/jlc_cpl_fit.py` downloads each part's EasyEDA footprint (the same data JLC's preview uses). For each rotation 0/90/180/270 it fits the EasyEDA pads and holes onto the KiCad pads. It keeps the rotation where every pad lands on its own pad with the correct pin number and function, and where the 3D-model body sits on the same side as the KiCad courtyard. That last check settles the symmetric slide switch.
- Re-reading the written CPL: every part's EasyEDA pads land on the KiCad pads.
  - Worst pad-centre offset for most parts: 0.0-0.3 mm. These are land-size differences between the two libraries.
  - U1: 0.43 mm (ESOP-8 land length).
  - SW3: 0.60 mm, only on its two angled 45 deg retention tabs. The datasheet land pattern has those tabs rotated 45 deg, as in the KiCad footprint. EasyEDA draws them as unrotated rectangles. All 10 other pads and both locating holes of SW3 match exactly.
- The correction table lives in `scripts/make_fab.py` (`JLC_CORR`, keyed by LCSC part and footprint, in the footprint's own frame), so it survives regenerating and moving parts. `python3 scripts/jlc_cpl_fit.py --check` re-derives it from EasyEDA and fails if the two disagree.
- Overlay images, `previews/cpl_overlay_<REF>.png`: green = KiCad copper, red dashed = EasyEDA/JLC footprint at the new CPL, orange dotted = where rev 3's CPL put it, * = EasyEDA 3D-model origin. There is one for each of J1, J2, SW1, SW3, U2, U1, U3, U5, Q1, D1, D3, D7 and SW2.
- Footprint data is from the **JLCEDA/EasyEDA official library (https://easyeda.com, https://lceda.cn)**.
- Side note: the EasyEDA *symbol* for XC6206 (C5446) labels pin 2 Vin and pin 3 Vout. The Torex datasheet SOT-23 pinout is 1 VSS, 2 VOUT, 3 VIN, which is what this design uses. Only the label in EasyEDA is wrong, and the pad numbers and placement are unaffected.

**U4 (RRD-102 radio module) is deliberately not in the JLC BOM or CPL.** It is a hand-soldered part, listed in `openald-BOM-human.csv` with a buy link. I checked JLC/LCSC for parts JLC could place:
- RRD-102 modules: RDA5807MRRD-102V2.0 (C9900205627) and RRD-102BC (C9900241000).
- M-RDA5807M LCC-10 11x11 mm (C9900132695).
- Bare RDA5807M chips: MSOP-10 C82537 and C9900056628.
- RDA5807MP/MS SOP-8 (C167245, C167246) and RDA5807FP SOP-16 (C77689).

Every one showed **0 in stock**, and the C99... entries are placeholder "new arrival" listings. Hand-soldering stays the plan. Alternatively, you can send JLC your own modules as consigned parts.

### What changed in rev 3 (battery-level bar)
| Request | Change |
|---|---|
| 3 LEDs instead of the RGB LED | The 5 mm flat-top RGB LED, its printed spacer and its case hole are gone. **D1, D5, D6 are KENTO KT-0603G emerald-green 0603 LEDs (LCSC C12624)**, all JLC-placed. JLC's basic library has no green or yellow 0603 LED, only red (C2286) and white. C12624 is already on the board as the "charged" LED D4, so it **adds no new extended-part fee**. Each LED has a **1k resistor (R11-R13, C21190, basic)** for about 1 mA (see "LED brightness"). |
| Bar near the bottom front, centred above the USB-C | The LEDs sit in a row at x = 15 / 19 / 23 mm, y = 71.25 mm (4 mm pitch). The middle LED is on the board centre line, straight above the centred USB-C. They fit between the battery holder's alignment-peg hole (19, 67) and its + pad (19, 75.4). In the case frame they are 15.75 mm from the USB-C end. To make room, U1 (TP4056), C2 and R3 moved left and R21/R22 moved up 1 mm. The TP1 test pad is removed (PA0 is used now). |
| One light tunnel per LED, no bleed | The lid has a printed bore around every 0603 LED: a 3.2 x 2.0 mm bore with 0.8 mm walls (shared between neighbours), running from the ceiling down to **0.2 mm above the PCB**. Each window sees only its own LED. The two charge LEDs (D3 red, D4 green) got the same kind of tunnels. |
| Window style | **Open windows with a 0.4 mm rounded rim** (default): 2.4 x 1.4 mm rounded "bar segments" for the level bar and 1.6 mm round holes for the charge LEDs. I chose open holes because they work with **any filament colour**, give the brightest and sharpest segments, and don't depend on how translucent the plastic is. The thin-skin option is one switch away: `led_window = "skin"` in `case/openald_case.scad` leaves a 0.4 mm skin (2 layers) over each window. It looks seamless and keeps dust out, but it only glows through with white or natural, translucent PLA/PETG. |
| Off by default, show on button press | The LEDs are only lit when you press the **battery-check button SW2** (top edge, next to the headphone jack; it is the button the original design already used for "battery check"). See the firmware spec below. |
| Level while charging, blink when very low | The MCU reads the TP4056 **nCHRG** status on PA0 through Schottky D7 (B5819W, C8598, basic, already on the board as D2). While charging it shows an estimated level with a "filling" blink. Below 3.4 V the first LED blinks, and below 3.3 V it blinks fast. |
| Charging indication with the power switch off | See "How charging is shown" below. In short, the TP4056's own red/green LEDs always work, and holding the button shows the bar. No extra parts were needed apart from D7. |

Earlier revisions (still in place): USB-C centred on the bottom edge (board 38 x 87 mm), HRO SK-12E12-G5 slide switch with a 3.5 x 2.5 mm knob sticking out 2.8 mm, and smooth filleted recesses for the USB-C plug and the thumbwheel. Case 43 x 92 x 33.4 mm. (Older revision snapshots were kept on the original build machine only; their notes are summarised in `../HANDOFF.md`.)

