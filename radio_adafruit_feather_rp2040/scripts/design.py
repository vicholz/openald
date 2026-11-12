"""OpenALD Feather RP2040 v1.0 - controls board: parts, values, footprints, LCSC numbers, pin->net map.
The board carries the volume/tune thumbwheel (with push), the EN power switch, the battery-voltage divider for the
Feather (which has no battery monitor) and two charge-status LEDs that mirror the Feather's MCP73831 STAT pin so the
charge state is visible above the dock pocket. Everything else lives on the Adafruit Feather RP2040."""
import os as _os,sys as _sys; _sys.path.insert(0,_os.path.dirname(_os.path.abspath(__file__)))
import layout as _L
R0603="Resistor_SMD:R_0603_1608Metric"; C0603="Capacitor_SMD:C_0603_1608Metric"
def R(ref,val,lcsc,n1,n2,grp,mpn=""):
    return dict(ref=ref,lib="Device:R",val=val,fp=R0603,lcsc=lcsc,mpn=mpn,pins={"1":n1,"2":n2},grp=grp)
def C(ref,val,lcsc,n1,n2,grp,mpn=""):
    return dict(ref=ref,lib="Device:C",val=val,fp=C0603,lcsc=lcsc,mpn=mpn,pins={"1":n1,"2":n2},grp=grp)
P=[]
# wire pads to the Feather (THT, 1.8 mm pitch, wires come up through the frame slot from below)
P+=[dict(ref="J1",lib="Connector_Generic:Conn_01x09",val="FEATHER WIRES",fp="openald_fctl:WirePads_1x09_P1.80mm",lcsc="",mpn="(wire pads)",grp="io",
         nobom=False,hand=True,pins={str(i+1):n for i,n in enumerate(_L.PADS)})]   # order = layout.PADS (pad 1 nearest the wheel)
# power switch: SPDT, common (2) = Feather EN; knob toward pin 1 = EN to GND = OFF; pin 3 open = ON (EN pulled up on the Feather)
P+=[dict(ref="SW1",lib="Switch:SW_SPDT",val="POWER (SK-12E12-G5)",fp="openald_fctl:SW_Slide_SPDT_Angled_HRO_SK-12E12-G5",lcsc="C136720",mpn="HRO SK-12E12-G5",
         grp="pwr",tht=True,hand=True,pins={"1":"GND","2":"EN","3":None})]
# thumbwheel encoder with push: common C to GND, A/B/S to Feather GPIO with the RP2040's internal pull-ups
P+=[dict(ref="SW2",lib="openald_fctl:SIQ-02FVS3",val="SIQ-02FVS3",fp="openald_fctl:Mitsumi_SIQ-02FVS3",lcsc="C2925423",mpn="Mitsumi SIQ-02FVS3",grp="ui",
         pins={"A":"ENCA","B":"ENCB","C":"GND","S":"ENCSW"})]
# battery monitor for Feather A0: VBAT/2 (220k/220k, 9.5 uA), 100 nF at the ADC node
P+=[R("R1","220k","C22961","VBAT","BSNS","pwr","UNI-ROYAL 0603WAF2203T5E"), R("R2","220k","C22961","BSNS","GND","pwr","UNI-ROYAL 0603WAF2203T5E"),
    C("C1","100nF","C14663","BSNS","GND","pwr","Samsung CC0603KRX7R9BB104")]
# charge-status mirror: Feather MCP73831 STAT (tap at Feather R2 pad 2). STAT low = charging -> D1 red (from VBUS);
# STAT high = charge complete -> D2 green (to GND); STAT Hi-Z (no USB / no cell) -> both off (red 2.0 V + green 3.1 V > 5 V)
P+=[R("R3","1.5k","C22843","VBUS","LEDR_A","ui","UNI-ROYAL 0603WAF1501T5E"),
    dict(ref="D1",lib="Device:LED",val="RED CHG",fp="LED_SMD:LED_0603_1608Metric",lcsc="C2286",mpn="Hubei KENTO KT-0603R",grp="ui",pins={"1":"STAT","2":"LEDR_A"}),
    R("R4","1.5k","C22843","STAT","LEDG_A","ui","UNI-ROYAL 0603WAF1501T5E"),
    dict(ref="D2",lib="Device:LED",val="GREEN FULL",fp="LED_SMD:LED_0603_1608Metric",lcsc="C12624",mpn="Hubei KENTO KT-0603G",grp="ui",pins={"1":"GND","2":"LEDG_A"})]
# NPTH locating holes for the printed frame pegs (board only)
for i in range(2):
    P.append(dict(ref=f"H{i+1}",lib="",val="PEG 2.1",fp="openald_fctl:PegHole_2.1mm",lcsc="",grp="mech",boardonly=True,nobom=True,pins={}))
PARTS={p["ref"]:p for p in P}
