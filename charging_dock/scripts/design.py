"""OpenALD Dock v1.0 - parts, values, footprints, LCSC numbers and pin->net connections (single source of truth).
Power path: USB-C in (J1) -> F1 4 A fuse -> D1 SMBJ22A TVS -> Q1 AO4407A P-FET (gated by U1 HUSB238 PD sink, opens on
no-PD/OVP) -> VIN_SW -> 2x SY8205FCC 5 A buck (U2 -> 5V_A, U3 -> 5V_B, 5.10 V, enabled only above ~12 V) -> 6x SY6280AAC
current-limited switches (~1.45 A each) -> 6 vertical USB-C plugs (J2-J7)."""
R0603="Resistor_SMD:R_0603_1608Metric"; R0805="Resistor_SMD:R_0805_2012Metric"; C0603="Capacitor_SMD:C_0603_1608Metric"
C0805="Capacitor_SMD:C_0805_2012Metric"; C1206="Capacitor_SMD:C_1206_3216Metric"
def R(ref,val,lcsc,n1,n2,grp,mpn="",fp=R0603):
    return dict(ref=ref,lib="Device:R",val=val,fp=fp,lcsc=lcsc,mpn=mpn,pins={"1":n1,"2":n2},grp=grp)
def C(ref,val,lcsc,n1,n2,grp,fp=C0603,mpn=""):
    return dict(ref=ref,lib="Device:C",val=val,fp=fp,lcsc=lcsc,mpn=mpn,pins={"1":n1,"2":n2},grp=grp)
P=[]
# ---------------- USB-C PD input ----------------
P+=[dict(ref="J1",lib="Connector:USB_C_Receptacle_USB2.0_16P",val="USB-C IN (PD sink)",fp="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",lcsc="C165948",mpn="HRO TYPE-C-31-M-12",grp="in",
        pins={"A4":"VBUS","A9":"VBUS","B4":"VBUS","B9":"VBUS","A1":"GND","A12":"GND","B1":"GND","B12":"GND","S1":"GND",
              "A5":"CC1","B5":"CC2","A6":None,"B6":None,"A7":None,"B7":None,"A8":None,"B8":None}),   # power-only: D+/D- not used
    dict(ref="F1",lib="Device:Fuse",val="4A 32V fast",fp="Fuse:Fuse_1206_3216Metric",lcsc="C187596",mpn="Littelfuse 0466004.NRHF",grp="in",pins={"1":"VBUS","2":"VBUS_F"}),
    dict(ref="D1",lib="Device:D_Zener",val="SMBJ22A (TVS, uni)",fp="Diode_SMD:D_SMB",lcsc="C151920",mpn="SMBJ22A",grp="in",pins={"1":"VBUS_F","2":"GND"}),
    C("C1","10uF 50V","C13585","VBUS_F","GND","in",C1206,"CL31A106KBHNNNE"),
    # HUSB238 (DS v1.0): VSET open = 20 V request, ISET 13.7k = 2.25 A; picks the highest PDO <= 20 V offering >= 2.25 A,
    # else steps down (D+/D- left open: BC1.2/Apple detection unused, PD only); GATE (open drain) pulls Q1's gate low once a contract (or default 5 V) is up, releases it on OVP.
    dict(ref="U1",lib="openald:HUSB238",val="HUSB238_002DD",fp="Package_DFN_QFN:DFN-10-1EP_3x3mm_P0.5mm_EP1.55x2.48mm",lcsc="C7471904",mpn="Hynetek HUSB238_002DD",grp="in",
        pins={"1":"VBUS_F","2":None,"3":None,"4":"CC1","5":"CC2","6":None,"7":None,"8":None,"9":"ISET","10":"PD_GATE","11":"GND"}),
    R("R1","13.7k","C22793","ISET","GND","in","0603WAF1372T5E"),
    C("C2","1uF 50V","C15849","VBUS_F","GND","in",mpn="CL10A105KB8NNNC"),
    dict(ref="Q1",lib="openald:AO4407A",val="AO4407A",fp="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",lcsc="C16072",mpn="AOS AO4407A",grp="in",
        pins={"1":"VBUS_F","2":"VBUS_F","3":"VBUS_F","4":"Q1_G","5":"VIN_SW","6":"VIN_SW","7":"VIN_SW","8":"VIN_SW"}),
    R("R2","100k","C25803","VBUS_F","Q1_G","in","0603WAF1003T5E"),     # gate pull-up to source: off by default
    R("R3","47k","C25819","Q1_G","PD_GATE","in","0603WAF4702T5E"),     # Vgs = -Vin*100/147 (13.6 V at 20 V, < 20 V max)
    C("C3","4.7nF 50V","C53987","VBUS_F","Q1_G","in",mpn="0603B472K500NT"),  # slows the turn-on (inrush into C4/C5-C8)
    dict(ref="C4",lib="Device:C_Polarized",val="100uF 35V",fp="Capacitor_SMD:CP_Elec_8x10",lcsc="C2895269",mpn="RVE100UF35V67RV0161",grp="in",pins={"1":"VIN_SW","2":"GND"})]
# ---------------- 2x SY8205FCC buck, 5.10 V (Vref 0.6 V, 75k/10k) ----------------
for s,u,base in (("A","U2",10),("B","U3",30)):
    n=lambda i: f"{i}{base+0}" if False else None
    c=lambda i: f"C{base+i}"; r=lambda i: f"R{base+i}"
    P+=[dict(ref=u,lib="openald:SY8205FCC",val="SY8205FCC",fp="Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm",lcsc="C111875",mpn="Silergy SY8205FCC",grp="buck"+s,
            pins={"1":f"BS_{s}","2":f"LX_{s}","3":f"EN_{s}","4":f"SS_{s}","5":f"FB_{s}","6":f"VCC_{s}","7":"VIN_SW","8":"VIN_SW","9":"GND"}),
        C(c(1),"10uF 50V","C13585","VIN_SW","GND","buck"+s,C1206,"CL31A106KBHNNNE"),
        C(c(2),"10uF 50V","C13585","VIN_SW","GND","buck"+s,C1206,"CL31A106KBHNNNE"),
        C(c(3),"100nF","C14663",f"BS_{s}",f"LX_{s}","buck"+s,mpn="CC0603KRX7R9BB104"),
        C(c(4),"1uF","C15849",f"VCC_{s}","GND","buck"+s,mpn="CL10A105KB8NNNC"),
        C(c(5),"22nF","C21122",f"SS_{s}","GND","buck"+s,mpn="CL10B223KB8NNNC"),
        dict(ref=f"L{1 if s=='A' else 2}",lib="Device:L",val="4.7uH 7A",fp="openald:L_Sunlord_MWSA0604S",lcsc="C408457",mpn="Sunlord MWSA0604S-4R7MT",grp="buck"+s,pins={"1":f"LX_{s}","2":f"5V_{s}"}),
        C(c(6),"22uF 25V","C45783",f"5V_{s}","GND","buck"+s,C0805,"CL21A226MAQNNNE"),
        C(c(7),"22uF 25V","C45783",f"5V_{s}","GND","buck"+s,C0805,"CL21A226MAQNNNE"),
        C(c(8),"22uF 25V","C45783",f"5V_{s}","GND","buck"+s,C0805,"CL21A226MAQNNNE"),
        dict(ref=c(9),lib="Device:C_Polarized",val="470uF 10V",fp="Capacitor_SMD:CP_Elec_6.3x7.7",lcsc="C2858856",mpn="RVT470UF10V67RV0159",grp="buck"+s,pins={"1":f"5V_{s}","2":"GND"}),
        C(c(10),"100pF","C14858",f"5V_{s}",f"FB_{s}","buck"+s,mpn="CL10C101JB8NNNC"),
        R(r(1),"75k","C23242",f"5V_{s}",f"FB_{s}","buck"+s,"0603WAF7502T5E"),
        R(r(2),"10k","C25804",f"FB_{s}","GND","buck"+s,"0603WAF1002T5E"),
        # EN divider: rising threshold 1.2-1.4 V -> 11.2-13.1 V at VIN (typ 12.1 V); off below 10.3-12.1 V.
        # 5 V and 9 V never enable the bucks; 15 V and 20 V always do; 12 V is not supported.
        R(r(3),"100k","C25803","VIN_SW",f"EN_{s}","buck"+s,"0603WAF1003T5E"),
        R(r(4),"12k","C22790",f"EN_{s}","GND","buck"+s,"0603WAF1202T5E")]
# ---------------- 6x slot switch (SY6280AAC, Ilim = 6800/Rset = 1.45 A +-25 %) + plug ----------------
for i in range(1,7):
    rail="5V_A" if i in (1,2,4) else "5V_B"
    P+=[dict(ref=f"U{3+i}",lib="openald:SY6280AAC",val="SY6280AAC",fp="Package_TO_SOT_SMD:SOT-23-5",lcsc="C55136",mpn="Silergy SY6280AAC",grp=f"slot{i}",
            pins={"1":f"SLOT{i}","2":"GND","3":f"ISET{i}","4":rail,"5":rail}),
        R(f"R{50+i}","4.7k","C23162",f"ISET{i}","GND",f"slot{i}","0603WAF4701T5E"),
        C(f"C{50+i}","1uF","C15849",rail,"GND",f"slot{i}",mpn="CL10A105KB8NNNC"),
        C(f"C{60+i}","10uF 25V","C15850",f"SLOT{i}","GND",f"slot{i}",C0805,"CL21A106KAYNNNE"),
        R(f"R{60+i}","22k","C31850",f"SLOT{i}",f"CC{i}S","slot{i}" if False else f"slot{i}","0603WAF2202T5E"),   # Rp: 'default USB power'
        dict(ref=f"J{1+i}",lib="openald:USB_C_Plug_16P",val=f"SLOT {i} plug",fp="openald:USB_C_Plug_HX_TYPE-C-M-16P_Vertical",lcsc="C55200592",mpn="HX TYPE C-M 16P V-SMT",grp=f"slot{i}",hand=True,
            pins={"A1":"GND","A12":"GND","B1":"GND","B12":"GND","S1":"GND","A4":f"SLOT{i}","A9":f"SLOT{i}","B4":f"SLOT{i}","B9":f"SLOT{i}",
                  "A5":f"CC{i}S","B5":None,"A6":None,"A7":None,"B6":None,"B7":None,"A8":None,"B8":None})]
# ---------------- status LED (light pipe in the deck between the centre pockets) ----------------
P+=[dict(ref="D2",lib="Device:LED",val="Green (5 V on)",fp="LED_SMD:LED_0603_1608Metric",lcsc="C12624",mpn="KT-0603G",grp="led",pins={"1":"GND","2":"LEDG_A"}),
    R("R4","1k","C21190","5V_A","LEDG_A","led","0603WAF1001T5E"),
    dict(ref="D3",lib="Device:LED",val="Red (no PD)",fp="LED_SMD:LED_0603_1608Metric",lcsc="C2286",mpn="KT-0603R",grp="led",pins={"1":"GND","2":"LEDR_A"}),
    R("R5","4.7k","C17673","VBUS_F","LEDR_A","led","0805W8F4701T5E",fp=R0805),
    dict(ref="Q2",lib="Transistor_FET:AO3400A",val="AO3400A",fp="Package_TO_SOT_SMD:SOT-23",lcsc="C20917",mpn="AOS AO3400A",grp="led",pins={"1":"5V_A","2":"GND","3":"LEDR_A"}),
    R("R6","100k","C25803","5V_A","GND","led","0603WAF1003T5E")]   # bleeds 5V_A so Q2 turns off (red back on) when the buck stops
# ---------------- mechanical ----------------
for i in range(1,7):
    P.append(dict(ref=f"H{i}",lib="Mechanical:MountingHole",val="M3",fp="MountingHole:MountingHole_3.2mm_M3",lcsc="",mpn="M3 screw hole",grp="mech",pins={},nobom=True,boardonly=True))
for i in range(7,19):
    P.append(dict(ref=f"H{i}",lib="Mechanical:MountingHole",val="peg",fp="MountingHole:MountingHole_2.2mm_M2",lcsc="",mpn="floor-pad locating peg hole",grp="mech",pins={},nobom=True,boardonly=True))
PARTS={p["ref"]:p for p in P}
