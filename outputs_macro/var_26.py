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
GRUPO = "Energy supply and use"    # era "Economy" (revisão do David, 09/09/2026)
UNIDADE = "US$"

# Escreve 0 para o tipo ausente no período, de modo que toda série tenha 6 anos.
PREENCHER_ZEROS = True

# OneWayTransmissionLink{NaturalGas} é 0,0 nos seis períodos.
DESCARTAR = {"OneWayTransmissionLink{NaturalGas}"}

# Nome legível de cada tipo de ativo, no mesmo espírito da planilha
# ethanol_flows: produto ou serviço primeiro, rota tecnológica entre parênteses.
ROTULO = {
    "BECCSEthanolv2":                     "Ethanol",
    "BECCSDieselv2":                      "Biodiesel (FAME)",
    "BECCSATJ":                           "Sustainable aviation fuel (alcohol-to-jet)",
    "BECCSCharcoal":                      "Charcoal (carbonization)",
    "BECCSElectricity":                   "Bioelectricity",
    "BECCSHydrogen":                      "Hydrogen (biomass gasification)",
    "BioGasifSNG":                        "Biomethane (biomass gasification)",
    "HEFA":                               "HEFA",
    # o modelo manda HEFAv2; sem esta chave o rótulo cru vazava (11/09/2026)
    "HEFAv2":                             "HEFA",
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
    # soma com TransmissionLink{Electricity}: mesmo rótulo (11/09/2026)
    "OneWayTransmissionLink{Electricity}":"Electricity transmission",
    "TransmissionLink{Electricity}":      "Electricity transmission",
}


def gerar(root: Path, **kw):
    # Agrega pelo RÓTULO, não pelo tipo cru: dois tipos que compartilham rótulo
    # viram uma linha só. Hoje isso vale para TransmissionLink{Electricity} e
    # OneWayTransmissionLink{Electricity}, que a equipe pediu para somar em
    # "Electricity transmission" (11/09/2026). Antes desta agregação os dois
    # saíam como duas linhas com o MESMO Class_1 e o mesmo ano, o que quebra a
    # chave da plataforma — o valor total não muda, só deixa de vir partido.
    por_ano, rotulos, sem_rotulo = {}, set(), set()
    for p, year in PERIODS.items():
        g = custos_por_tipo(root, p)
        d = {}
        for (t, c), v in g.items():
            if c != "Investment" or t == "Total" or t in DESCARTAR:
                continue
            if t not in ROTULO:
                # O tipo cru vai para a saída para o valor não sumir, mas o
                # nome do ativo do modelo não pode chegar ao dashboard. Isso já
                # aconteceu: HydroRes, MustRun e OneWayTransmissionLink{Charcoal}
                # apareceram numa rodada da plataforma e não nas nossas, porque
                # aqui esses ativos não investiram. O aviso existe para o
                # próximo caso ser visto na hora de rodar, e não semanas depois
                # numa planilha da equipe.
                sem_rotulo.add(t)
            d[ROTULO.get(t, t)] = d.get(ROTULO.get(t, t), 0.0) + v
        por_ano[year] = d
        rotulos |= set(d)

    if sem_rotulo:
        print(f"      [26] AVISO: {len(sem_rotulo)} tipo(s) de ativo sem rótulo "
              f"em ROTULO — o nome cru vai sair na Class_1: "
              + ", ".join(sorted(sem_rotulo)))

    out = []
    for rot in sorted(rotulos):
        for year in PERIODS.values():
            if rot not in por_ano[year] and not PREENCHER_ZEROS:
                continue
            # Class_1 vira o rótulo do tipo de investimento (era Class_2), e
            # Class_2 vira "NA" (revisão do David, 09/09/2026).
            out.append(row(GRUPO, NOME, c1=rot, c2="NA",
                           unit=UNIDADE, territory="BR", year=year,
                           value=round(por_ano[year].get(rot, 0.0), 5)))
    return out
