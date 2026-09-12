# -*- coding: utf-8 -*-
"""Vocabulário de matéria-prima e rota de conversão, seguindo o diagrama da
equipe (Input Feedstocks -> Conversions -> Energy carriers).

Usado pela id 19 para ligar cada remoção à biomassa que a originou.
"""
import re

# commodity de entrada do modelo -> (Class_1 família, Class_2 matéria-prima)
FEEDSTOCK = {
    "Sugarcane":        ("Primary crops",       "Sugarcane"),
    "Corn":             ("Primary crops",       "Corn"),
    "Soybean":          ("Primary crops",       "Soybean"),
    # Macaúba não aparece no diagrama, mas é a matéria-prima dominante do
    # biodiesel neste cenário (75,7 Mt em 2050). Entra como cultura primária.
    "Macauba":          ("Primary crops",       "Macauba"),
    "SugarcaneStraw":   ("Herbaceous residues", "Sugarcane straw"),
    "CornStover":       ("Herbaceous residues", "Corn stover"),
    "RiceStraw":        ("Herbaceous residues", "Rice straw"),
    "Biomass_wood":     ("Woody biomass",       "Plantation forestry"),
    "Forestry_residue": ("Woody biomass",       "Forestry residues"),
    # 'Residue' é o nó AGREGADO que recebe as três palhas depois do
    # BiomassTransformation. Quem consome Residue não sabe de qual palha veio.
    # Class_2 renomeado a pedido do David (09/09/2026): "Aggregated residue"
    # -> "Herbaceous aggregated residue".
    "Residue":          ("Herbaceous residues", "Herbaceous aggregated residue"),
    # entradas que não são biomassa
    "Ethanol":          ("NA",                 "Ethanol (secondary feedstock)"),
    "CO2":              ("NA",                 "Atmospheric CO2"),
}

# família do resource_id -> (Class_3 conversão, Class_4 vetor energético)
CONVERSAO = {
    "BECCS_sugarcane_ethanol":          ("1G ethanol",                 "Ethanol"),
    # usinas de cana já existentes: mesma rota, mesmo rótulo — as duas linhas
    # se somam sozinhas porque a var_19 agrega pela tupla de classes
    # (pedido da equipe, 11/09/2026).
    "BECCS_sugarcane_ethanol_existing": ("1G ethanol",              "Ethanol"),
    "BECCS_sugarcane_ethanol_CCS":      ("1G ethanol with CCS",        "Ethanol"),
    "BECCS_corn_ethanol":               ("1G ethanol",                 "Ethanol"),
    "BECCS_corn_ethanol_existing":      ("1G ethanol",                 "Ethanol"),
    "BECCS_corn_ethanol_CCS":           ("1G ethanol with CCS",        "Ethanol"),
    "BECCS_1G2G_sugarcane_ethanol":     ("1G2G ethanol",               "Ethanol"),
    "BECCS_1G2G_sugarcane_ethanol_CCS": ("1G2G ethanol with CCS",      "Ethanol"),
    "BECCS_Lignocellulosic_ethanol":    ("2G ethanol",                 "Ethanol"),
    "BECCS_Lignocellulosic_ethanol_CCS":("2G ethanol with CCS",        "Ethanol"),
    "Macauba_FAME":                     ("FAME",                       "Biodiesel (FAME)"),
    "Soybean_Biodiesel_large":          ("FAME",                       "Biodiesel (FAME)"),
    "Soybean_Biodiesel_large_existing": ("FAME",                       "Biodiesel (FAME)"),
    "HEFA_macauba":                     ("HEFA",                       "Synthetic Diesel"),
    "HEFA_soybean":                     ("HEFA",                       "Synthetic Diesel"),
    "BR_ATJ_ethanol":                   ("Ethanol-to-jet",             "Synthetic Jet (SAF)"),
    "BR_ATJ_Diesel":                    ("Ethanol-to-jet",             "Synthetic Diesel"),
    "biomass_wood_thermal_plant":       ("Biomass power",              "Electricity"),
    "biomass_wood_thermal_plant_CCS":   ("Biomass power with CCS",     "Electricity"),
    "biomass_thermal_plant":            ("Biomass power",              "Electricity"),
    "biomass_thermal_plant_CCS":        ("Biomass power with CCS",     "Electricity"),
    "greendiesel_wood_FT":              ("Gasification FT",            "Synthetic Diesel"),
    "greendiesel_residue_FT":           ("Gasification FT",            "Synthetic Diesel"),
    "gasoline_wood_FT":                 ("Gasification FT",            "Synthetic Gasoline"),
    "gasoline_residue_FT":              ("Gasification FT",            "Synthetic Gasoline"),
    "wood_H2":                          ("Gasification H2",            "Hydrogen"),
    "wood_H2_CCS":                      ("Gasification H2 with CCS",   "Hydrogen"),
    "residue_H2":                       ("Gasification H2",            "Hydrogen"),
    "residue_H2_CCS":                   ("Gasification H2 with CCS",   "Hydrogen"),
    "biogasif_sng":                     ("Gasification SNG",           "Methane"),
    "biogasif_sng_ccs":                 ("Gasification SNG with CCS",  "Methane"),
    "BECCS_charcoal":                   ("Charcoal kiln",              "Charcoal"),
    "BECCS_residue_charcoal":           ("Charcoal kiln",              "Charcoal"),
}

# ativos sem família útil no resource_id
POR_TIPO = {
    "BiomassTransformation": ("Residue collection", "NA"),
    "ElectricDAC":           ("Direct air capture", "NA"),
}

# ARESTA PRINCIPAL DE CADA ATIVO, em ordem de prioridade.
#
# A captação de CO2 do MACRO é `co2_content do ativo x fluxo da aresta
# PRINCIPAL` — um co2_content por ativo (1,650 tCO2/t no etanol de milho,
# 1,558 na cana, 1,613 no FAME, 1,833 na carvoaria), aplicado a uma aresta só.
# Conferido nas 28 famílias de ativo com remoção, exato na terceira casa.
#
# O `coinput_edge` NÃO ENTRA. Três rotas queimam lenha de floresta plantada
# como co-insumo de processo — etanol de milho (21,2 Mt de lenha sobre 66,6 Mt
# de milho em 2025), FAME de soja e FAME de macaúba — e essa lenha não gera
# captação nenhuma no modelo. Ratear a captação entre a matéria-prima e o
# co-insumo, como esta variável fazia antes (correção incorporada de outra
# rodada, 02/09/2026), criava um crédito que o modelo não dá: em 2025 movia
# 30 Mt de Primary crops para Woody biomass.
PRINCIPAL = ("biomass_edge", "origin_edge", "ethanol_edge")

# mantido para quem quiser inspecionar o consumo total de biomassa por ativo
ENTRADAS = PRINCIPAL + ("coinput_edge",)


def familia(resource_id) -> str:
    return re.sub(r"^BR_[A-Z]{2}_", "", str(resource_id))


def conversao(resource_id, resource_type):
    f = familia(resource_id)
    return CONVERSAO.get(f) or POR_TIPO.get(str(resource_type)) or (f, "NA")
