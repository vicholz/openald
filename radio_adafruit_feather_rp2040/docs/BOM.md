# OpenALD Feather RP2040 v1.0 — bill of materials (direct-mount wheel and switch, no PCB)

Prices were checked on 2026-11-11 and are in USD, without shipping or tax (items added on 2026-11-24 are not price-checked). There is **no PCB to order**: the wheel is bought loose and glued into the printed frame, the switch presses into a groove in the case wall (no screws), and everything is hand-wired to the Feather. (The retired controls-board BOM is in `../archive/controls_board_pcb/fab/`.)

| # | Item | Source | Qty | Unit USD | Link / note |
|---|---|---|---|---|---|
| 1 | Adafruit Feather RP2040 (#4884) | Adafruit | 1 | 11.95 | [adafruit.com](https://www.adafruit.com/product/4884) product page, 2026-11-11 |
| 2 | FM module (the one Victor has): **27.25 × 27.25 mm, 1.6 mm board, Ø3.8 corner holes on a 20 mm square, 4-pin 90° through-board header and a 6.35 × 14 mm headphone jack (1 mm past the board), both centred on the bottom edge** | — | 1 | — | on hand; not priced |
| 3 | 18650 holder, PC pin, MPD BH-18650-PC | DigiKey BH-18650-PC-ND | 1 | 3.35 | [digikey.com](https://www.digikey.com/en/products/detail/mpd-memory-protection-devices/BH-18650-PC/3029216) qty-1 snapshot, 2026-11-11 |
| 4 | Protected button-top 18650 cell, e.g. Samsung 35E protected 3500 mAh (~69.3–69.8 mm) | 18650 Battery Store | 1 | 11.99 | [18650batterystore.com](https://www.18650batterystore.com/products/samsung-35e-protected) snapshot, 2026-11-11 |
| 5 | STEMMA QT / Qwiic JST SH 4-pin cable 100 mm (#4210), one end cut, soldered to the FM module's header pins under the deck | Adafruit | 1 | 0.95 | [adafruit.com](https://www.adafruit.com/product/4210) (showed out of stock; #4209/#4397 same price) |
| 6 | JST PH 2-pin cable 100 mm (#261), battery lead | Adafruit | 1 | 0.75 | [adafruit.com](https://www.adafruit.com/product/261) |
| 7 | **Thumbwheel encoder with push, Mitsumi SIQ-02FVS3** (loose, glued into the deck cradle) | LCSC C2925423 | 1 | 3.18 | [lcsc.com](https://www.lcsc.com/product-detail/C2925423.html) JLC/LCSC parts API, 2026-11-11 |
| 8 | **Slide switch SS-12F16, SPDT (1P2T), panel mount**: G4 (4 mm knob) by default; G6 works (`SW_L=6`); LCSC stocks only the G050 (`SW_L=5`) | LCSC C2876006 (G050) or any SS-12F16-G4/G6 | 1 | 0.08 | [lcsc.com](https://www.lcsc.com/product-detail/C2876006.html) G050 price, 2026-11-11; G4/G6 not price-checked |
| 9 | **USB-C receptacle breakout, power-only, with 5.1 k CC pull-downs** (dock charging port; the case assumes a 12.7 × 10 × 1.0 mm board with the receptacle on its edge, overhanging 0.5 mm — measure yours and edit `BRK_*` in `scripts/layout.py`) | any | 1 | — | not price-checked (added 2026-11-24) |
| 10 | Schottky diode SS14 or 1N5817 (breakout VBUS → Feather USB pin) and optional **M3 × 8 screws + M3 nuts** (×3) for the FM module | any | 1 + 3 | — | not price-checked (added 2026-11-24). The case itself snaps shut: the old M2 screws and inserts are gone |
| 11 | Battery divider: 2 × 220 k + 1 × 100 nF, inline in heat-shrink (needed for the battery gauge) | any | 1 set | — | not price-checked |
| 12 | Optional dock-visible charge LEDs: 3 mm THT red + green (diffused), 2 × 1.5 k | any | 1 set | — | not price-checked |
| 13 | **Hookup wire** 28–30 AWG silicone, ~8 colours, ~1.5 m total (about 12 leads of ~120 mm), 32–36 AWG enamel for the optional STAT tap, 1.5–2 mm heat-shrink, medium CA or 5-min epoxy, thin double-sided tape (≤ 0.2 mm, not foam) or glue dots for the holder | any | — | — | not price-checked |
| 14 | Filament (PLA/PETG): front shell 8.8 + back shell 13.8 + deck 2.0 cm³ ≈ 25 cm³ (~31 g) | — | — | — | — |

**Priced items total: $32.25** per radio (Feather, holder, cell, two cables, wheel, switch). Add the USB-C breakout, the diode, the optional M3 screws/nuts, the divider/LED parts, wire and filament. The FM module is already on hand. Compared with the controls-board version this drops the JLC PCB order (board, assembly, ~$6 of extended-part fees and shipping).
