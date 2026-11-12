"""Single source of truth: parts, values, footprints, LCSC numbers and pin->net connections."""
R0603="Resistor_SMD:R_0603_1608Metric"; C0603="Capacitor_SMD:C_0603_1608Metric"
C0805="Capacitor_SMD:C_0805_2012Metric"; C1206="Capacitor_SMD:C_1206_3216Metric"
def R(ref,val,lcsc,n1,n2,grp,mpn=""):
    return dict(ref=ref,lib="Device:R",val=val,fp=R0603,lcsc=lcsc,mpn=mpn,pins={"1":n1,"2":n2},grp=grp)
def C(ref,val,lcsc,n1,n2,grp,fp=C0603,mpn=""):
    return dict(ref=ref,lib="Device:C",val=val,fp=fp,lcsc=lcsc,mpn=mpn,pins={"1":n1,"2":n2},grp=grp)
P=[]
# ---------------- USB-C input + TP4056 charger ----------------
P+=[dict(ref="J1",lib="Connector:USB_C_Receptacle_USB2.0_16P",val="USB-C (power + USB 2.0 data)",fp="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",lcsc="C165948",mpn="HRO TYPE-C-31-M-12",grp="usb",
        pins={"A4":"VBUS","A9":"VBUS","B4":"VBUS","B9":"VBUS","A1":"GND","A12":"GND","B1":"GND","B12":"GND","S1":"GND",
              "A5":"CC1","B5":"CC2","A6":"USB_DP","B6":"USB_DP","A7":"USB_DN","B7":"USB_DN","A8":None,"B8":None})]
P+=[R("R1","5.1k","C23186","CC1","GND","usb","0603WAF5101T5E"), R("R2","5.1k","C23186","CC2","GND","usb","0603WAF5101T5E"),
    C("C1","10uF 25V","C15850","VBUS","GND","usb",C0805,"CL21A106KAYNNNE")]
P+=[dict(ref="U1",lib="Battery_Management:TP4056-42-ESOP8",val="TP4056",fp="Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.3mm",lcsc="C16581",mpn="TP4056-42-ESOP8",grp="chg",
        pins={"1":"GND","2":"PROG","3":"GND","4":"VBUS","5":"VBAT","6":"nSTDBY","7":"nCHRG","8":"VBUS","9":"GND"})]
P+=[R("R3","1.2k","C22765","PROG","GND","chg","0603WAF1201T5E"),
    C("C2","10uF 25V","C15850","VBAT","GND","chg",C0805,"CL21A106KAYNNNE"),
    R("R21","1k","C21190","VBUS","LEDCHG_A","chg","0603WAF1001T5E"), R("R22","1k","C21190","VBUS","LEDSTB_A","chg","0603WAF1001T5E"),
    dict(ref="D3",lib="Device:LED",val="Red (charging)",fp="LED_SMD:LED_0603_1608Metric",lcsc="C2286",mpn="KT-0603R",grp="chg",pins={"1":"nCHRG","2":"LEDCHG_A"}),
    dict(ref="D4",lib="Device:LED",val="Green (charged)",fp="LED_SMD:LED_0603_1608Metric",lcsc="C12624",mpn="KT-0603G",grp="chg",pins={"1":"nSTDBY","2":"LEDSTB_A"})]
# ---------------- 18650 + DW01A/FS8205A protection ----------------
P+=[dict(ref="BT1",lib="Device:Battery_Cell",val="18650 holder",fp="Battery:BatteryHolder_MPD_BH-18650-PC",lcsc="",mpn="MPD BH-18650-PC",grp="bat",side="B",
        pins={"1":"BAT_P","2":"BATN"},hand=True)]
# ---------------- rev 4.2: reverse-polarity protection (high-side P-FET, gated by an orientation-sensing N-FET) ----------------
# Q2 (AO3401A) sits between the holder + contact (BAT_P) and every other battery node (VBAT: TP4056 BAT, DW01A VCC via R4,
# SW1, Q4, C2).  Q3 (AO3400A) senses the cell itself: its gate sees BAT_P and its source BATN (cell -), so it is on only
# when BAT_P is above BATN (cell the right way round).  Q3 then pulls Q2's gate to BATN -> Q2 fully on (Vgs = -Vcell),
# conducting in both directions (load and TP4056 charge current).  Reversed cell: Q3 Vgs = -Vcell -> off, R24 holds Q2's
# gate at its source -> Q2 off and its body diode (anode BAT_P) is reverse biased, so no loop through the board exists,
# even with USB plugged in (TP4056 driving VBAT cannot turn Q2 on, because Q3 does not look at VBAT).
P+=[dict(ref="Q2",lib="Transistor_FET:AO3401A",val="AO3401A",fp="Package_TO_SOT_SMD:SOT-23",lcsc="C15127",mpn="AOS AO3401A",grp="bat",
        pins={"1":"Q2_G","2":"VBAT","3":"BAT_P"}),
    dict(ref="Q3",lib="Transistor_FET:AO3400A",val="AO3400A",fp="Package_TO_SOT_SMD:SOT-23",lcsc="C20917",mpn="AOS AO3400A",grp="bat",
        pins={"1":"Q3_G","2":"BATN","3":"Q2_G"}),
    R("R23","10k","C25804","BAT_P","Q3_G","bat","0603WAF1002T5E"),     # Q3 gate resistor (no DC current)
    R("R24","1M","C22935","VBAT","Q2_G","bat","0603WAF1004T5E")]      # Q2 gate pull-up to its source (~4 uA while Q3 is on)
P+=[dict(ref="U2",lib="Battery_Management:DW01A",val="DW01A",fp="Package_TO_SOT_SMD:SOT-23-6",lcsc="C351410",mpn="DW01A (PUOLOP)",grp="bat",
        pins={"1":"OD","2":"CS","3":"OC","4":None,"5":"DW_VCC","6":"BATN"}),
    dict(ref="Q1",lib="openald:FS8205A",val="FS8205A",fp="Package_TO_SOT_SMD:SOT-23-6",lcsc="C2830320",mpn="FS8205A (TECH PUBLIC)",grp="bat",
        pins={"1":"BATN","2":"Q_D","3":"GND","4":"OC","5":"Q_D","6":"OD"}),
    R("R4","100","C22775","VBAT","DW_VCC","bat","0603WAF1000T5E"),
    C("C3","100nF","C14663","DW_VCC","BATN","bat",mpn="CC0603KRX7R9BB104"),
    R("R5","1k","C21190","CS","GND","bat","0603WAF1001T5E")]
# ---------------- power switch, wheel-press power path (Q4), LDO ----------------
P+=[dict(ref="SW1",lib="Switch:SW_SPDT",val="POWER (SK-12E12-G5)",fp="openald:SW_Slide_SPDT_Angled_HRO_SK-12E12-G5",lcsc="C136720",mpn="HRO SK-12E12-G5",grp="pwr",tht=True,
        pins={"1":None,"2":"VBAT","3":"VSYS"}),
    # v1.0 wheel-press update (2026-11-11): the separate battery-check button SW2 (EVQ-P7A01P, C79167) is gone. The
    # thumbwheel's push switch (SW3 S -> C = GND) now does its job: R25 holds WHEEL_SW_N (Q4 gate) at VBAT, pressing the
    # wheel pulls it to GND, P-FET Q4 turns on and drives VBTN from VBAT exactly like SW2 did (D2 -> VSYS, D10 -> VMCU,
    # R6/R7 -> BTN_SENSE). So "hold the wheel in with the switch off" still powers the MCU for the battery check, and
    # with the switch on the MCU reads every wheel press on BTN_SENSE (PC1). Released: no current (gate at source).
    # Pressed: 4.2 uA in R25. PD4 is no longer connected (WHEEL_SW_N sits at VBAT, up to 4.2 V, too high for a 3.3 V pin).
    dict(ref="Q4",lib="Transistor_FET:AO3401A",val="AO3401A",fp="Package_TO_SOT_SMD:SOT-23",lcsc="C15127",mpn="AOS AO3401A",grp="pwr",
        pins={"1":"WHEEL_SW_N","2":"VBAT","3":"VBTN"}),   # AO3401A SOT-23: 1 G, 2 S, 3 D (same as Q2)
    R("R25","1M","C22935","VBAT","WHEEL_SW_N","pwr","0603WAF1004T5E"),
    dict(ref="D2",lib="Device:D_Schottky",val="B5819W",fp="Diode_SMD:D_SOD-123",lcsc="C8598",mpn="B5819W SL",grp="pwr",pins={"1":"VSYS","2":"VBTN"}),
    # rev 4.1: 4.7k/10k (was 47k/100k). VBTN floats when SW2 (now Q4) is open, and D2/D10 (B5819W) reverse leakage (JSCJ datasheet:
    # ~5 uA each at 25 C, ~10x at 75 C) into 147k gave ~1 V on PC1 at room temperature (above VIL max) -> false "pressed".
    R("R6","4.7k","C23162","VBTN","BTN_SENSE","pwr","0603WAF4701T5E"), R("R7","10k","C25804","BTN_SENSE","GND","pwr","0603WAF1002T5E"),
    dict(ref="U5",lib="Regulator_Linear:XC6206PxxxMR",val="XC6206P332MR",fp="Package_TO_SOT_SMD:SOT-23-3",lcsc="C5446",mpn="XC6206P332MR-G",grp="pwr",
        pins={"1":"GND","2":"+3V3R","3":"VSYS"}),
    C("C4","1uF","C15849","VSYS","GND","pwr",mpn="CL10A105KB8NNNC"), C("C5","10uF","C19702","+3V3R","GND","pwr",mpn="CL10A106KP8NNNC"),
    # rev 4.1: 47k/12k (was 100k/33k). 100k/33k put a full cell (4.24 V max) at 1.05 V, above the 1.0 V minimum of the
    # ATmega328PB internal 1.1 V reference (DS40001906 VINT 1.0-1.2 V) -> ADC could clip. Now 0.86 V; source 9.6k (<10k per DS).
    R("R8","47k","C25819","VSYS","BAT_ADC","pwr","0603WAF4702T5E"), R("R9","12k","C22790","BAT_ADC","GND","pwr","0603WAF1202T5E"),
    C("C6","100nF","C14663","BAT_ADC","GND","pwr",mpn="CC0603KRX7R9BB104")]
# ---------------- MCU: ATmega328PB-AU (TQFP-32), internal 8 MHz RC; Arduino (MiniCore) pin names in comments ----------------
# Pin 3 (PE0) is tied to GND and pin 6 (PE1) to +3V3 so an ATmega328P-AU (pin 3 = GND, pin 6 = VCC) also drops in;
# firmware must leave PE0/PE1 as inputs without pull-ups (Microchip AN42559 / AT15007).
P+=[dict(ref="U3",lib="MCU_Microchip_ATmega:ATmega328PB-A",val="ATmega328PB-AU",fp="Package_QFP:TQFP-32_7x7mm_P0.8mm",lcsc="C132230",mpn="ATMEGA328PB-AU",grp="mcu",
        pins={"4":"+3V3","18":"+3V3","6":"+3V3","5":"GND","21":"GND","3":"GND","20":"AREF",
              "32":"ENC_A","1":"ENC_B","2":None,                     # PD2/INT0 (D2), PD3/INT1 (D3), PD4 (D4) spare: wheel press is read on BTN_SENSE (PC1)
              "9":"LVL1","10":"LVL2","13":"LVL3",                    # PD5/OC0B (D5), PD6/OC0A (D6), PB1/OC1A (D9): hardware PWM
              "15":"MOSI","16":"MISO","17":"SCK",                    # PB3/PB4/PB5 (D11/D12/D13): ISP only
              "23":"BAT_ADC","24":"BTN_SENSE","25":"CHRG_SENSE",     # PC0/ADC0 (A0), PC1 (A1), PC2 (A2)
              "27":"SDA","28":"SCL","29":"nRESET",                   # PC4/SDA0 (A4), PC5/SCL0 (A5), PC6/RESET
              "30":"MCU_RX","31":"MCU_TX",                           # PD0/RXD0 (D0), PD1/TXD0 (D1)
              "7":None,"8":None,"11":None,"12":None,"14":None,"19":None,"22":None,"26":None}),
    C("C7","100nF","C14663","+3V3","GND","mcu",mpn="CC0603KRX7R9BB104"),     # VCC pin 4
    C("C13","100nF","C14663","+3V3","GND","mcu",mpn="CC0603KRX7R9BB104"),    # AVCC pin 18
    C("C14","100nF","C14663","AREF","GND","mcu",mpn="CC0603KRX7R9BB104"),    # AREF pin 20 (internal 1.1 V reference)
    # TP4056 nCHRG -> PC2 through a Schottky (cathode at nCHRG): reads low only while charging; blocks back-feed into an unpowered MCU
    dict(ref="D7",lib="Device:D_Schottky",val="B5819W",fp="Diode_SMD:D_SOD-123",lcsc="C8598",mpn="B5819W SL",grp="chg",pins={"1":"nCHRG","2":"CHRG_SENSE"}),
    R("R10","10k","C25804","+3V3","nRESET","mcu","0603WAF1002T5E"),
    # I2C pull-ups go to the radio rail: with the radio unpowered (switch off, USB in) they cannot back-feed the RDA5807M
    R("R14","4.7k","C23162","+3V3R","SDA","mcu","0603WAF4701T5E"), R("R15","4.7k","C23162","+3V3R","SCL","mcu","0603WAF4701T5E"),
    dict(ref="J3",lib="Connector_Generic:Conn_02x03_Odd_Even",val="AVR-ISP pogo pads (DNP)",fp="Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical",lcsc="",mpn="2x3 2.54mm header / pogo (DNP)",grp="mcu",
        pins={"1":"MISO","2":"+3V3","3":"SCK","4":"MOSI","5":"nRESET","6":"GND"},dnp=True)]
# ---------------- USB serial (CH340K, powered from VBUS only) + Arduino auto-reset + MCU-only 3.3 V rail ----------------
P+=[dict(ref="U8",lib="Power_Protection:USBLC6-2SC6",val="USBLC6-2SC6",fp="Package_TO_SOT_SMD:SOT-23-6",lcsc="C7519",mpn="ST USBLC6-2SC6",grp="ser",
        pins={"1":"USB_DP","6":"USB_DP","3":"USB_DN","4":"USB_DN","5":"VBUS","2":"GND"}),
    dict(ref="U7",lib="Interface_USB:CH340K",val="CH340K",fp="Package_SO:SSOP-10-1EP_3.9x4.9mm_P1mm_EP2.1x3.3mm",lcsc="C968586",mpn="WCH CH340K",grp="ser",
        pins={"1":"USB_DP","2":"USB_DN","3":"GND","11":"GND","7":"VBUS","10":"CH_V3","8":"MCU_RX","9":"CH_RX","4":"DTR_N","5":None,"6":None}),
    C("C15","100nF","C14663","VBUS","GND","ser",mpn="CC0603KRX7R9BB104"),   # CH340K VCC (5 V from VBUS)
    C("C16","100nF","C14663","CH_V3","GND","ser",mpn="CC0603KRX7R9BB104"),  # CH340K V3: 100 nF to GND in 5 V mode
    R("R19","10k","C25804","+3V3","MCU_RX","ser","0603WAF1002T5E"),         # RXD idle-high pull-up (CH340K TXD is low-drive / weak-high)
    R("R20","1k","C21190","MCU_TX","CH_RX","ser","0603WAF1001T5E"),         # series R, MCU TXD -> CH340K RXD
    C("C19","100nF","C14663","DTR_N","nRESET","ser",mpn="CC0603KRX7R9BB104"), # Arduino auto-reset (DTR# -> 100 nF -> RESET)
    # MCU-only 3.3 V rail: diode-OR of switched VSYS and USB VBUS into a second XC6206. The radio stays on U5 / VSYS.
    dict(ref="D8",lib="Device:D_Schottky",val="B5819W",fp="Diode_SMD:D_SOD-123",lcsc="C8598",mpn="B5819W SL",grp="ser",pins={"1":"VMCU","2":"VSYS"}),
    dict(ref="D9",lib="Device:D_Schottky",val="B5819W",fp="Diode_SMD:D_SOD-123",lcsc="C8598",mpn="B5819W SL",grp="ser",pins={"1":"VMCU","2":"VBUS"}),
    # wheel press (via Q4, formerly button SW2) straight into the MCU rail (one diode drop, like rev 3), so the bar still works on a nearly empty cell
    dict(ref="D10",lib="Device:D_Schottky",val="B5819W",fp="Diode_SMD:D_SOD-123",lcsc="C8598",mpn="B5819W SL",grp="ser",pins={"1":"VMCU","2":"VBTN"}),
    dict(ref="U6",lib="Regulator_Linear:XC6206PxxxMR",val="XC6206P332MR",fp="Package_TO_SOT_SMD:SOT-23-3",lcsc="C5446",mpn="XC6206P332MR-G",grp="ser",
        pins={"1":"GND","2":"+3V3","3":"VMCU"}),
    C("C17","1uF","C15849","VMCU","GND","ser",mpn="CL10A105KB8NNNC"), C("C18","10uF","C19702","+3V3","GND","ser",mpn="CL10A106KP8NNNC")]
# ---------------- UI: 3-LED battery level bar (KT-0603G emerald green, ~1 mA each), encoder ----------------
LEDG=dict(lib="Device:LED",fp="LED_SMD:LED_0603_1608Metric",lcsc="C12624",mpn="KT-0603G",grp="ui")
P+=[dict(LEDG,ref="D1",val="Green (level bar)",pins={"1":"GND","2":"LVL1_A"}),
    dict(LEDG,ref="D5",val="Green (level bar)",pins={"1":"GND","2":"LVL2_A"}),
    dict(LEDG,ref="D6",val="Green (level bar)",pins={"1":"GND","2":"LVL3_A"}),
    R("R11","1k","C21190","LVL1","LVL1_A","ui","0603WAF1001T5E"), R("R12","1k","C21190","LVL2","LVL2_A","ui","0603WAF1001T5E"),
    R("R13","1k","C21190","LVL3","LVL3_A","ui","0603WAF1001T5E"),
    dict(ref="SW3",lib="openald:SIQ-02FVS3",val="SIQ-02FVS3",fp="openald:Mitsumi_SIQ-02FVS3",lcsc="C2925423",mpn="Mitsumi SIQ-02FVS3",grp="ui",
        pins={"A":"ENC_A","B":"ENC_B","C":"GND","S":"WHEEL_SW_N"})]
# ---------------- FM module + headphone/antenna ----------------
P+=[dict(ref="U4",lib="openald:RRD-102",val="RRD-102V2.0 (RDA5807M)",fp="openald:RRD-102_RDA5807M_Module",lcsc="",mpn="RRD-102V2.0 RDA5807M module",grp="fm",
        pins={"10":"FM_VDD","1":"GND","6":"FM_SDA","7":"FM_SCL","5":"FM_ANT","4":None,"3":"FM_L","2":"FM_R","8":None,"9":None},hand=True),
    R("R18","10","C22859","+3V3R","FM_VDD","fm","0603WAF100JT5E"),
    C("C8","22uF","C45783","FM_VDD","GND","fm",C0805,"CL21A226MAQNNNE"), C("C9","100nF","C14663","FM_VDD","GND","fm",mpn="CC0603KRX7R9BB104"),
    R("R16","1k","C21190","SDA","FM_SDA","fm","0603WAF1001T5E"), R("R17","1k","C21190","SCL","FM_SCL","fm","0603WAF1001T5E"),
    C("C10","100uF 6.3V","C15008","FM_L","HPL_C","fm",C1206,"CL31A107MQHNNNE"), C("C11","100uF 6.3V","C15008","FM_R","HPR_C","fm",C1206,"CL31A107MQHNNNE"),
    dict(ref="FB1",lib="Device:FerriteBead_Small",val="600R@100MHz",fp="Inductor_SMD:L_0603_1608Metric",lcsc="C1002",mpn="GZ1608D601TF",grp="fm",pins={"1":"HPL_C","2":"HP_L"}),
    dict(ref="FB2",lib="Device:FerriteBead_Small",val="600R@100MHz",fp="Inductor_SMD:L_0603_1608Metric",lcsc="C1002",mpn="GZ1608D601TF",grp="fm",pins={"1":"HPR_C","2":"HP_R"}),
    dict(ref="FB3",lib="Device:FerriteBead_Small",val="600R@100MHz",fp="Inductor_SMD:L_0603_1608Metric",lcsc="C1002",mpn="GZ1608D601TF",grp="fm",pins={"1":"HP_GND","2":"GND"}),
    C("C12","1nF","C1588","HP_GND","FM_ANT","fm",mpn="CL10B102KB8NNNC"),
    dict(ref="J2",lib="Connector_Audio:AudioJack4",val="3.5mm jack PJ-320D-4A",fp="Connector_Audio:Jack_3.5mm_KoreanHropartsElec_PJ-320D-4A_Horizontal",lcsc="C95562",mpn="HRO PJ-320D-4A",grp="fm",
        pins={"T":"HP_L","R1":"HP_R","R2":"HP_GND","S":"HP_GND"})]
# ---------------- mechanical ----------------
for i in range(1,5):
    P.append(dict(ref=f"H{i}",lib="Mechanical:MountingHole",val="M2",fp="MountingHole:MountingHole_2.2mm_M2",lcsc="",mpn="M2 screw hole",grp="mech",pins={},dnp=False,nobom=True,boardonly=True))
PARTS={p["ref"]:p for p in P}
