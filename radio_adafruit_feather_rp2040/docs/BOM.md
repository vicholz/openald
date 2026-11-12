# OpenALD Feather RP2040 v1.0 — bill of materials

Prices were checked on 2026-11-11 and are in USD, without shipping or tax. The controls-board fab and assembly fees are only quoted by JLCPCB at checkout. Full controls-board BOM: `fab/openald-feather-controls-BOM-human.csv`.

| # | Item | Source | Qty | Unit USD | Link / note |
|---|---|---|---|---|---|
| 1 | Adafruit Feather RP2040 (#4884) | Adafruit | 1 | 11.95 | [www.adafruit.com](https://www.adafruit.com/product/4884) adafruit.com product page, 2026-11-11 |
| 2 | RDA5807M FM module, 26.9 x 26.9 mm, on-board 3.5 mm jack (the one Victor already has) | — | 1 | — |  on hand; not priced |
| 3 | 18650 holder, PC pin, MPD BH-18650-PC | DigiKey BH-18650-PC-ND | 1 | 3.35 | [www.digikey.com](https://www.digikey.com/en/products/detail/mpd-memory-protection-devices/BH-18650-PC/3029216) DigiKey qty-1 price via search snapshot, 2026-11-11 |
| 4 | Protected button-top 18650 cell, e.g. Samsung 35E protected 3500 mAh (~69.3-69.8 mm) | 18650 Battery Store | 1 | 11.99 | [www.18650batterystore.com](https://www.18650batterystore.com/products/samsung-35e-protected) product page snapshot, 2026-11-11 |
| 5 | STEMMA QT / Qwiic JST SH 4-pin cable 100 mm (#4210) - cut one end, solder to the FM module (or #4209 to male headers) | Adafruit | 1 | 0.95 | [www.adafruit.com](https://www.adafruit.com/product/4210) adafruit.com product page, 2026-11-11 (showed out of stock; #4209/#4397 same price) |
| 6 | JST PH 2-pin cable, female connector 100 mm (#261) - battery lead | Adafruit | 1 | 0.75 | [www.adafruit.com](https://www.adafruit.com/product/261) adafruit.com product page, 2026-11-11 |
| 7 | Controls board, JLCPCB 2-layer + SMT (SW2, R1-R4, C1, D1, D2) - files in fab/ | JLCPCB / LCSC | 1 | 3.07 | [jlcpcb.com](https://jlcpcb.com) LCSC parts only, qty-10 price, JLC parts API 2026-11-11; + ~$3 x 2 extended-part fees per order + PCB/assembly/shipping at checkout |
| 8 | Slide switch HRO SK-12E12-G5 (SW1, hand-soldered THT) | LCSC C136720 | 1 | 0.11 | [www.lcsc.com](https://www.lcsc.com/product-detail/C136720.html) JLC parts API 2026-11-11 |
| 9 | M2 x 12 mm screws (socket or pan head) | any | 4 | — | [www.amazon.com](https://www.amazon.com/s?k=M2+x+12mm+socket+head+screws) not price-checked |
| 10 | M2 brass heat-set inserts, OD 3.2-3.5 x L <= 4.5 mm | any | 4 | — | [www.amazon.com](https://www.amazon.com/s?k=M2+heat+set+inserts) not price-checked |
| 11 | Wire: 28-30 AWG silicone (8 colours) + 32-36 AWG enamel/wire-wrap for the STAT tap; double-sided foam tape | any | — | — |  not price-checked |
| 12 | Filament (PLA/PETG): top 10.9 + bottom 18.2 + frame 2.6 cm^3 = ~32 cm^3 (~40 g) | — | — | — |  — |

**Priced items total: $32.17** per radio. That covers the Feather, holder, cell, cables, LCSC parts for the controls board and the switch.
Add about **$6** per JLC order in extended-part fees (SIQ-02FVS3 C2925423 and the green LED C12624; a basic-library green 0603 was out of stock), plus JLC PCB, assembly and shipping, screws, inserts and wire. The FM module is already on hand.

Controls-board LCSC parts (live JLC API, qty-10 unit price):

| Ref | Part | LCSC | Library | Stock | USD |
|---|---|---|---|---|---|
| SW2 | SIQ-02FVS3 | [C2925423](https://www.lcsc.com/product-detail/C2925423.html) | Extended | 1289 | 3.0374 |
| R1,R2 | 0603WAF2203T5E | [C22961](https://www.lcsc.com/product-detail/C22961.html) | Basic | 996093 | 0.0015 |
| C1 | CC0603KRX7R9BB104 | [C14663](https://www.lcsc.com/product-detail/C14663.html) | Basic | 37499256 | 0.006 |
| R3,R4 | 0603WAF1501T5E | [C22843](https://www.lcsc.com/product-detail/C22843.html) | Basic | 3047009 | 0.002 |
| D1 | KT-0603R | [C2286](https://www.lcsc.com/product-detail/C2286.html) | Basic | 6042340 | 0.0077 |
| D2 | KT-0603G | [C12624](https://www.lcsc.com/product-detail/C12624.html) | Extended | 296357 | 0.0119 |
| SW1 (hand) | SK-12E12-G5 | [C136720](https://www.lcsc.com/product-detail/C136720.html) | Extended | 15487 | 0.1132 |
