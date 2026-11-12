# OpenALD Feather RP2040 v1.0 — bill of materials (direct-mount wheel and switch, no PCB)

Prices were checked on 2026-11-11 and are in USD, without shipping or tax. There is **no PCB to order** any more: the wheel is bought loose and glued into the printed frame, the switch screws into the case wall, and everything is hand-wired to the Feather. (The retired controls-board BOM is in `../archive/controls_board_pcb/fab/`.)

| # | Item | Source | Qty | Unit USD | Link / note |
|---|---|---|---|---|---|
| 1 | Adafruit Feather RP2040 (#4884) | Adafruit | 1 | 11.95 | [adafruit.com](https://www.adafruit.com/product/4884) product page, 2026-11-11 |
| 2 | RDA5807M FM module, 26.9 × 26.9 mm, on-board 3.5 mm jack (the one Victor already has) | — | 1 | — | on hand; not priced |
| 3 | 18650 holder, PC pin, MPD BH-18650-PC | DigiKey BH-18650-PC-ND | 1 | 3.35 | [digikey.com](https://www.digikey.com/en/products/detail/mpd-memory-protection-devices/BH-18650-PC/3029216) qty-1 snapshot, 2026-11-11 |
| 4 | Protected button-top 18650 cell, e.g. Samsung 35E protected 3500 mAh (~69.3–69.8 mm) | 18650 Battery Store | 1 | 11.99 | [18650batterystore.com](https://www.18650batterystore.com/products/samsung-35e-protected) snapshot, 2026-11-11 |
| 5 | STEMMA QT / Qwiic JST SH 4-pin cable 100 mm (#4210), one end cut | Adafruit | 1 | 0.95 | [adafruit.com](https://www.adafruit.com/product/4210) (showed out of stock; #4209/#4397 same price) |
| 6 | JST PH 2-pin cable 100 mm (#261), battery lead | Adafruit | 1 | 0.75 | [adafruit.com](https://www.adafruit.com/product/261) |
| 7 | **Thumbwheel encoder with push, Mitsumi SIQ-02FVS3** (loose, glued into the frame cradle) | LCSC C2925423 | 1 | 3.18 | [lcsc.com](https://www.lcsc.com/product-detail/C2925423.html) JLC/LCSC parts API, 2026-11-11 |
| 8 | **Slide switch SS-12F16, SPDT (1P2T), panel mount**: G4 (4 mm knob) by default; G6 works (`SW_L=6`); LCSC stocks only the G050 (`SW_L=5`) | LCSC C2876006 (G050) or any SS-12F16-G4/G6 | 1 | 0.08 | [lcsc.com](https://www.lcsc.com/product-detail/C2876006.html) G050 price, 2026-11-11; G4/G6 not price-checked |
| 9 | M2 × 3 pan-head screws for the switch (M2 × 4 also fits) | any | 2 | — | not price-checked |
| 10 | M2 × 12 mm screws (case) | any | 4 | — | not price-checked |
| 11 | M2 brass heat-set inserts, OD 3.2–3.5 × L ≤ 4.5 mm | any | 4 | — | not price-checked |
| 12 | Battery divider: 2 × 220 k + 1 × 100 nF, inline in heat-shrink (needed for the battery gauge) | any | 1 set | — | not price-checked |
| 13 | Optional dock-visible charge LEDs: 3 mm THT red + green (diffused), 2 × 1.5 k | any | 1 set | — | not price-checked |
| 14 | **Hookup wire** 28–30 AWG silicone, ~8 colours, ~1.5 m total (about 12 leads of ~120 mm), 32–36 AWG enamel for the optional STAT tap, 1.5–2 mm heat-shrink, medium CA or 5-min epoxy, double-sided foam tape | any | — | — | not price-checked |
| 15 | Filament (PLA/PETG): top 10.8 + bottom 18.1 + frame 2.9 cm³ ≈ 32 cm³ (~40 g) | — | — | — | — |

**Priced items total: $32.25** per radio (Feather, holder, cell, two cables, wheel, switch). Add screws, inserts, the divider/LED parts, wire and filament. The FM module is already on hand. Compared with the controls-board version this drops the JLC PCB order (board, assembly, ~$6 of extended-part fees and shipping).
