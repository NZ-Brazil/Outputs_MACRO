"""id 26 — Energy-supply investments by type.

Mesma planilha da 24, filtrando category == 'Investment' e descartando a linha
agregada Total. Uma linha por (tipo, ano).
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, custos_por_tipo, row

NOTA  = NOTAS[26]
RESUMO  = RESUMOS[26]

ID    = 26
NOME  = "Energy supply investments"
COL2  = "Variable name"
GRUPO = "Economy"
UNIDADE = "US$"

# Escreve 0 para o tipo ausente no período, de modo que toda série tenha 6 anos.
PREENCHER_ZEROS = True

# OneWayTransmissionLink{NaturalGas} é 0,0 nos seis períodos.
DESCARTAR = {"OneWayTransmissionLink{NaturalGas}"}

# Nome legível de cada tipo de ativo, no mesmo espírito da planilha
# ethanol_flows: produto ou serviço primeiro, rota tecnológica entre parênteses.
ROTULO = {
    "BECCSEthanolv2":                     "Ethanol (BECCS)",
    "BECCSDieselv2":                      "Biodiesel (FAME)",
    "BECCSATJ":                           "Sustainable aviation fuel (alcohol-to-jet)",
    "BECCSCharcoal":                      "Charcoal (carbonization)",
    "BECCSElectricity":                   "Bioelectricity (BECCS)",
    "BECCSHydrogen":                      "Hydrogen (biomass gasification)",
    "BioGasifSNG":                        "Biomethane (biomass gasification)",
    "HEFA":                               "Renewable diesel and SAF (HEFA)",
    "FischerTropsch":                     "Renewable fuels (Fischer-Tropsch)",
    "SyntheticLiquidFuels":               "Synthetic liquid fuels (e-fuel)",
    "SyntheticNaturalGas":                "Synthetic methane (e-fuel)",
    "Electrolyzer":                       "Hydrogen (electrolysis)",
    "ThermalHydrogen{NaturalGas}":        "Hydrogen (steam methane reforming)",
    "ThermalHydrogenCCS{NaturalGas}":     "Hydrogen (steam methane reforming with CCS)",
    "ThermalPower{NaturalGas}":           "Natural gas power",
    "ThermalPowerCCS{NaturalGas}":        "Natural gas power with CCS",
    "ThermalPower{Coal}":                 "Coal power",
    "ThermalPower{Hydrogen}":             "Hydrogen power",
    "VRE{Generic}":                       "Solar and wind",
    "Battery":                            "Battery storage",
    "CO2Injection":                       "CO2 injection",
    "ElectricDAC":                        "Direct air capture",
    "OneWayTransmissionLink{CO2Captured}":"CO2 pipeline",
    "OneWayTransmissionLink{Electricity}":"Electricity transmission (one-way)",
    "TransmissionLink{Electricity}":      "Electricity transmission",
}


def gerar(root: Path, **kw):
    por_ano, tipos = {}, set()
    for p, year in PERIODS.items():
        g = custos_por_tipo(root, p)
        d = {t: v for (t, c), v in g.items()
             if c == "Investment" and t != "Total" and t not in DESCARTAR}
        por_ano[year] = d
        tipos |= set(d)

    out = []
    for t in sorted(tipos):
        for year in PERIODS.values():
            if t not in por_ano[year] and not PREENCHER_ZEROS:
                continue
            out.append(row(GRUPO, NOME, c1="Energy", c2=ROTULO.get(t, t),
                           unit=UNIDADE, territory="BR", year=year,
                           value=round(por_ano[year].get(t, 0.0), 5)))
    return out
