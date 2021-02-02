from typing import List, NamedTuple


class Symbol(NamedTuple):
    symbol_marketstack: str
    symbol_tradingview: str
    name: str


SYMBOLS: List[Symbol] = [
    Symbol("ABB.XSTO", "OMXSTO:ABB", "ABB Ltd"),
    Symbol("CGCBV.XHEL", "OMXHEX:CGCBV", "Cargotec Oyj"),
    Symbol("CARL_A.XCSE", "OMXCOP:CARL_A", "Carlsberg B A/S"),
    Symbol("COLO_B.XCSE", "OMXCOP:COLO_B", "Coloplast B A/S"),
    Symbol("DNORD.XCSE", "OMXCOP:DNORD", "D/S Norden"),
    Symbol("DANSKE.XCSE", "OMXCOP:DANSKE", "Danske Bank A/S"),
    Symbol("DSV.XCSE", "OMXCOP:DSV", "DSV Panalpina A/S"),
    Symbol("EQT.XSTO", "OMXSTO:EQT", "EQT AB"),
    Symbol("ESSITY_A.XSTO", "OMXSTO:ESSITY_A", "Essity AB ser. B"),
    Symbol("FABG.XSTO", "OMXSTO:FABG", "Fabege AB"),
    Symbol("BALD_B.XSTO", "OMXSTO:BALD_B", "Fastighets AB Balder ser. B"),
    Symbol("FIA1S.XHEL", "OMXHEX:FIA1S", "Finnair Oyj"),
    Symbol("FORTUM.XHEL", "OMXHEX:FORTUM", "Fortum Corporation"),
    Symbol("GMAB.XCSE", "OMXCOP:GMAB", "Genmab A/S"),
    Symbol("GN.XCSE", "OMXCOP:GN", "GN Store Nord A/S"),
    Symbol("HOLM_A.XSTO", "OMXSTO:HOLM_A", "Holmen AB ser. B"),
    Symbol("ICA.XSTO", "OMXSTO:ICA", "ICA Gruppen AB"),
    Symbol("KNEBV.XHEL", "OMXHEX:KNEBV", "KONE Corporation"),
    Symbol("LATO_B.XSTO", "OMXSTO:LATO_B", "Latour, Investmentab. ser. B"),
    Symbol("NESTE.XHEL", "OMXHEX:NESTE", "Neste Corporation"),
    Symbol("NKT.XCSE", "OMXCOP:NKT", "NKT A/S"),
    Symbol("NOKIA.XHEL", "OMXHEX:NOKIA", "Nokia Corporation"),
    Symbol("TYRES.XHEL", "OMXHEX:TYRES", "Nokian Tyres Plc"),
    Symbol("NDA_FI.XHEL", "OMXHEX:NDA_FI", "Nordea Bank Abp"),
    Symbol("NOVO_B.XCSE", "OMXCOP:NOVO_B", "Novo Nordisk B A/S"),
    Symbol("NZYM_B.XCSE", "OMXCOP:NZYM_B", "Novozymes B A/S"),
    Symbol("ORNBV.XHEL", "OMXHEX:ORNBV", "Orion Corporation B"),
    Symbol("OUT1V.XHEL", "OMXHEX:OUT1V", "Outokumpu Oyj"),
    Symbol("PNDORA.XCSE", "OMXCOP:PNDORA", "Pandora A/S"),
    Symbol("SAS.XSTO", "OMXSTO:SAS", "SAS AB"),
    Symbol("STEAV.XHEL", "OMXHEX:STEAV", "Stora Enso Oyj R"),
    Symbol("SOBI.XSTO", "OMXSTO:SOBI", "Swedish Orphan Biovitrum AB"),
    Symbol("SCA_A.XSTO", "OMXSTO:SCA_A", "Svenska Cellulosa AB SCA ser. B"),
    Symbol("UPM.XHEL", "OMXHEX:UPM", "UPM-Kymmene Corporation"),
    Symbol("VWS.XCSE", "OMXCOP:VWS", "Vestas Wind Systems A/S"),
    Symbol("WRT1V.XHEL", "OMXHEX:WRT1V", "Wärtsilä Corporation"),
    Symbol("SLV", "SLV", "Silver"),
    Symbol("IAU", "IAU", "Gold"),
]
