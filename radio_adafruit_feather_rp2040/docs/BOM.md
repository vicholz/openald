# OpenALD Feather RP2040 v1.0 — bill of materials (t116u: bottom-end USB-C, no PCB)

Prices were checked on 2026-11-11 and are in USD, without shipping or tax (items added on 2026-11-24 are not price-checked). There is **no PCB to order**: the wheel is bought loose and glued into the printed cradle, the switch presses into a groove in the case wall (no screws), and everything is hand-wired to the Feather's header pads. t116u (2026-11-24) dropped the USB-C breakout, the Schottky diode, the JST PH and STEMMA QT cables and the optional 3 mm charge LEDs: the Feather's own USB-C is the dock port and its own LEDs show through the front face. (The retired controls-board BOM is in `../archive/controls_board_pcb/fab/`.)

| # | Item | Source | Qty | Unit USD | Link / note |
|---|---|---|---|---|---|
| 1 | Adafruit Feather RP2040 (#4884) | Adafruit | 1 | 11.95 | [adafruit.com](https://www.adafruit.com/product/4884) product page, 2026-11-11 |
| 2 | FM module (the one Victor has): **27.25 × 27.25 mm, 1.6 mm board, Ø3.8 corner holes on a 20 mm square, 4-pin 90° through-board header and a 6.35 × 14 mm headphone jack (1 mm past the board), both centred on the bottom edge** | — | 1 | — | on hand; not priced |
| 3 | 18650 holder, PC pin, MPD BH-18650-PC | DigiKey BH-18650-PC-ND | 1 | 3.35 | [digikey.com](https://www.digikey.com/en/products/detail/mpd-memory-protection-devices/BH-18650-PC/3029216) qty-1 snapshot, 2026-11-11 |
| 4 | Protected button-top 18650 cell, e.g. Samsung 35E protected 3500 mAh (~69.3–69.8 mm) | 18650 Battery Store | 1 | 11.99 | [18650batterystore.com](https://www.18650batterystore.com/products/samsung-35e-protected) snapshot, 2026-11-11 |
| 5 | Optional **M3 × 8 screws + M3 nuts** (×3) for the FM module (the front-shell posts clamp it anyway) | any | 3 | — | not price-checked. The case snaps shut: no case screws or inserts |
| 6 | **Thumbwheel encoder with push, Mitsumi SIQ-02FVS3** (loose, glued into the deck cradle) | LCSC C2925423 | 1 | 3.18 | [lcsc.com](https://www.lcsc.com/product-detail/C2925423.html) JLC/LCSC parts API, 2026-11-11 |
| 7 | **Slide switch SS-12F16, SPDT (1P2T), panel mount**: G4 (4 mm knob) by default; G6 works (`SW_L=6`); LCSC stocks only the G050 (`SW_L=5`) | LCSC C2876006 (G050) or any SS-12F16-G4/G6 | 1 | 0.08 | [lcsc.com](https://www.lcsc.com/product-detail/C2876006.html) G050 price, 2026-11-11; G4/G6 not price-checked |
| 8 | Battery divider: 2 × 220 k + 1 × 100 nF, inline in heat-shrink (needed for the battery gauge) | any | 1 set | — | not price-checked |
| 9 | **Hookup wire** 28–30 AWG silicone, ~8 colours, ~1.5 m total (about 13 leads of ~120 mm, incl. the battery leads to the BAT / GND pads), 1.5–2 mm heat-shrink, medium CA or 5-min epoxy, thin double-sided tape (≤ 0.2 mm, not foam) or glue dots for the holder | any | — | — | not price-checked |
| 10 | Filament (PLA/PETG): front shell 9.0 + back shell 14.6 + deck 2.6 cm³ ≈ 26 cm³ (~33 g) | — | — | — | — |

**Priced items total: $30.55** per radio (Feather, holder, cell, wheel, switch). Add the optional M3 screws/nuts, the divider parts, wire and filament. The FM module is already on hand. Compared with the controls-board version this drops the JLC PCB order (board, assembly, ~$6 of extended-part fees and shipping).
