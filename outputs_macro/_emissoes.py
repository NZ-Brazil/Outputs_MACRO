"""Classificação do inventário de CO2, compartilhada pela 18 e pela 19.

CONVENÇÃO: a do MACRO, não a do SEEG. O modelo faz contabilidade de ciclo
cheio — a absorção da biomassa entra como remoção e a combustão de biomassa
entra como emissão. O SEEG trata as duas como ciclo neutro e não reporta
nenhuma delas. As duas leituras são legítimas e dão números muito diferentes
(2050: líquido -499,9 Mt na convenção MACRO, -160,3 na do SEEG), mas só a do
MACRO reconcilia com o cap que o modelo otimizou (614/391/168/-54/-277/-500).

Regra de sinal: valor > 0 é fluxo ENTRANDO no nó co2_emitted_BR (emissão);
valor < 0 é fluxo SAINDO dele (remoção). O nome da aresta não decide — para as
térmicas fósseis a co2_edge é positiva (emitem), para os BECCS é negativa
(absorvem).
"""
GRUPO = "Emissions"
NOME  = "Emissions and removals"
COL2  = "Emissions_or_removals"
# UNIDADE E FATOR seguem o padrão 2plat: TONELADAS, como no exemplo do EP
# (2plat_ep_emissions.csv). O flows.csv já grava em toneladas, então o fator é 1.
# Os números citados nas notas continuam em Mt, que é como se lê o resultado —
# divida por 1e6 para comparar. (Correção incorporada de outra rodada, 02/09/2026.)
UNIDADE = "tCO2e GWP100-AR5"
FATOR   = 1.0

# Class_5 é o GÁS, e só o gás. Os pares Class_5/Unit que existem na
# 2plat_all.xlsx são CO2e GWP100-AR5/tCO2e, CO2/tCO2, CH4/tCH4 e N2O/tN2O; a
# linha de convenção da aba do padrão manda o primeiro. O MACRO só rastreia CO2
# — não há CH4 nem N2O — então CO2e == CO2 aqui e o GWP é indiferente; vale o
# rótulo do padrão para o número somar com o dos outros modelos.
#
# A MARCAÇÃO FÓSSIL/BIOGÊNICO SAIU DAQUI. Ela não cabe em nenhuma coluna do
# padrão: nenhum outro modelo faz contabilidade de ciclo cheio, então a
# plataforma não previu o corte. Ele continua recuperável, linha a linha:
#     id 18 -> pelo Class_4, que determina 100% dos casos (BIOGENICO_CLASS4)
#     id 19 -> pelo Class_1: as três famílias de biomassa são biogênicas e
#              Class_1 = 'N/A' é captura direta do ar ou insumo secundário
# É a leitura SEEG: filtrar fora o biogênico. Está no LEIA-ME.
GAS = "CO2e GWP100-AR5"
GAS_FOSSIL = GAS_BIOGENIC = GAS

C2_ELEC = "Electricity generation"
C3_ELEC = "Electricity generation (public service)"
C2_FUEL = "Fuel production"

# nós de onde os ativos de uso final puxam combustível -> (é fóssil?, rótulo)
FONTE_COMBUSTIVEL = {
    "natgas_BR":             (True,  "Natural gas"),
    "gasoline_fossil_BR":    (True,  "Gasoline (fossil)"),
    "jetfuel_fossil_BR":     (True,  "Jet fuel (fossil)"),
    "diesel_fossil_BR":      (True,  "Diesel (fossil)"),
    "ethanol_BR":            (False, "Ethanol"),
    "biodiesel_BR":          (False, "Biodiesel"),
    "renewable_diesel_BR":   (False, "Renewable diesel"),
    "gasoline_renewable_BR": (False, "Renewable gasoline"),
    "jetfuel_SAF_BR":        (False, "Sustainable aviation fuel"),
}

# upstream fóssil -> (Class_3 sub-categoria SEEG, Class_4 produto)
UPSTREAM = {
    "Diesel_fossil_Upstream":    ("Oil refining", "Diesel (fossil)"),
    "Gasoline_fossil_Upstream":  ("Oil refining", "Gasoline (fossil)"),
    "JetFuel_fossil_Upstream":   ("Oil refining", "Jet fuel (fossil)"),
    "natgas_fossil_upstream_BR": ("Oil and natural gas transport", "Natural gas"),
}

# ativos de conversão -> (Class_2, Class_3, Class_4)
CONVERSAO = {
    "BECCSEthanolv2":       (C2_FUEL, "Ethanol production",  "Ethanol"),
    "BECCSDieselv2":        (C2_FUEL, "NA",                 "Biodiesel"),
    "BECCSCharcoal":        (C2_FUEL, "Charcoal production", "Charcoal"),
    "BECCSHydrogen":        (C2_FUEL, "NA",                 "Hydrogen"),
    "BECCSATJ":             (C2_FUEL, "NA",                 "Sustainable aviation fuel"),
    "BioGasifSNG":          (C2_FUEL, "NA",                 "Biomethane"),
    "FischerTropsch":       (C2_FUEL, "NA",                 "Renewable diesel"),
    "HEFA":                 (C2_FUEL, "NA",                 "Renewable diesel"),
    "SyntheticLiquidFuels": (C2_FUEL, "NA",                 "Synthetic liquid fuels"),
    "SyntheticNaturalGas":  (C2_FUEL, "NA",                 "Synthetic methane"),
    "BiomassTransformation":(C2_FUEL, "NA",                 "Biomass residue handling"),
    "BiomassTransformation_coprod": (C2_FUEL, "NA",         "Sugarcane harvesting"),
    "BECCSElectricity":     (C2_ELEC, C3_ELEC,               "Bioelectricity"),
    "ElectricDAC":          ("Carbon storage", "NA",        "Direct air capture"),
}

# geração e conversão fóssil
FOSSIL_ASSET = {
    "ThermalPower{NaturalGas}":       (C2_ELEC, C3_ELEC, "Natural gas"),
    "ThermalPowerCCS{NaturalGas}":    (C2_ELEC, C3_ELEC, "Natural gas with CCS"),
    "ThermalPower{Coal}":             (C2_ELEC, C3_ELEC, "Coal"),
    "ThermalPower{Hydrogen}":         (C2_ELEC, C3_ELEC, "Hydrogen"),
    "ThermalHydrogen{NaturalGas}":    (C2_FUEL, "NA", "Hydrogen (steam methane reforming)"),
    "ThermalHydrogenCCS{NaturalGas}": (C2_FUEL, "NA", "Hydrogen (steam methane reforming with CCS)"),
}

BIOGENICO = set(CONVERSAO) - {"ElectricDAC"}

# Os rótulos de Class_4 da id 18 que são combustão de biomassa. É esta lista
# que substitui o antigo Class_5 = 'CO2 (biogenic)'.
BIOGENICO_CLASS4 = frozenset(
    {rotulo for fossil, rotulo in FONTE_COMBUSTIVEL.values() if not fossil}
    | {c4 for chave, (_, _, c4) in CONVERSAO.items() if chave in BIOGENICO}
    | {"Residue"})


COMBUSTAO_DIRETA = {
    "HEFAv2": "Sustainable aviation fuel",
}


def _class3_producao(c2, c3, c4):
    """Revisão do David (09/09/2026): nas linhas de 'Fuel production' sem
    sub-rota declarada (Class_3 = 'N/A'), Class_3 passa a ser o próprio
    Class_4 + ' production' — em vez de ficar N/A."""
    if c2 == C2_FUEL and c3 == "NA":
        return f"{c4} production"
    return c3


def classificar(resource_type, resource_id, origem_combustivel=None):
    """-> (Class_1, Class_2, Class_3, Class_4, Class_5)"""
    rt = str(resource_type)

    # bloco exógeno: tudo o que o MACRO não modela (indústria, resíduos,
    # agropecuária...). Não cabe num único setor do SEEG.
    if rt == "OneWayTransmissionLink{CO2}":
        return ("NA", "NA", "NA",
                "Exogenous emissions (not modelled in MACRO)", GAS_FOSSIL)

    if rt in FOSSIL_ASSET:
        c2, c3, c4 = FOSSIL_ASSET[rt]
        c3 = _class3_producao(c2, c3, c4)
        return ("Energy", c2, c3, c4, GAS_FOSSIL)

    if rt.startswith("UpstreamEmissions"):
        c3, c4 = UPSTREAM.get(str(resource_id), ("NA", "NA"))
        return ("Energy", C2_FUEL, c3, c4, GAS_FOSSIL)

    if rt == "GeneralFuelsEndUse":
        no = str(origem_combustivel or "")
        if no.startswith("residue_BR"):
            fossil, rotulo = False, "Residue"
        else:
            fossil, rotulo = FONTE_COMBUSTIVEL.get(no, (True, "NA"))
        # O MACRO agrega a demanda final: não dá para separar Transportes,
        # Industrial, Residencial etc. como o SEEG faz. Class_2/Class_3 levam
        # rótulos genéricos de combustão (revisão do David, 09/09/2026).
        return ("Energy", "Fuel burning", "Various energy end uses", rotulo,
                GAS_FOSSIL if fossil else GAS_BIOGENIC)

    # Ativos cuja emissão a equipe pediu para reportar no bloco de queima, com o
    # rótulo do combustível que eles abastecem, para somar com a linha que já
    # existe (pedido da equipe, 11/09/2026). O HEFAv2 entrega JetFuel_SAF no
    # jetfuel_SAF_BR, o mesmo nó que o ATJ abastece; sem esta entrada ele caía
    # no fallback final e saía com o resource_type cru na Class_4.
    if rt in COMBUSTAO_DIRETA:
        return ("Energy", "Fuel burning", "Various energy end uses",
                COMBUSTAO_DIRETA[rt], GAS_BIOGENIC)

    if rt in CONVERSAO:
        c2, c3, c4 = CONVERSAO[rt]
        c3 = _class3_producao(c2, c3, c4)
        return ("Energy", c2, c3, c4,
                GAS_BIOGENIC if rt in BIOGENICO else GAS_FOSSIL)

    return ("Energy", "NA", "NA", rt, GAS_FOSSIL)


def origens_combustivel(d):
    """{resource_id: nó de onde puxa combustível} para os ativos de uso final."""
    fe = d[(d.resource_type == "GeneralFuelsEndUse") & (d.edge == "fuel_edge")
           & (d.value < 0)]
    return dict(zip(fe.resource_id, fe.node_in))
