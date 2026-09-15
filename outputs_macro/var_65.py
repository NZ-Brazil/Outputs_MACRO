# -*- coding: utf-8 -*-
"""id 65 — Biofuels, synthesized fuels and hydrogen production by technology.

Fonte: flows_annual/flows_annual_results_period_<p>.csv

A Tab8 sugere filtrar por commodity ('ethanol', 'biodiesel', 'green_diesel'...),
mas essas commodities NÃO EXISTEM no modelo: diesel renovável, biodiesel e HVO
são todos commodity 'Diesel'; SNG é 'NaturalGas'. Quem identifica o produto é o
NÓ DE DESTINO, que o modelo já separa do fóssil (renewable_diesel_BR vs
diesel_BR, natgas_nonfossil_BR vs natgas_BR).

CLASSES seguem o padrão da planilha ethanol_flows: produto, matéria-prima e
tecnologia como dimensões separadas, com CCS embutido no nome da tecnologia.
    Class_1 = produto      Class_2 = matéria-prima      Class_3 = tecnologia
    Class_4 = Class_5 = NA
Isso substitui a sub-categoria do SEEG que estava na Class_3, que só existia
para dois dos oito produtos (ver nota). As três dimensões ficaram nas Class_3,
4 e 5 até 15/09/2026, quando a equipe pediu para subi-las duas posições.

Produção BRUTA: não desconta reuso interno (etanol -> ATJ, H2 -> sintéticos e
termelétrica).
"""
from pathlib import Path
import re
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, fluxos, eh_no, row, uf_de

NOTA   = NOTAS[65]
RESUMO = RESUMOS[65]

ID    = 65
NOME  = "Biofuels, synthesized fuels and hydrogen production by technology"
COL2  = "Variable name"
# Revisão do David (09/09/2026): Variable_group vira "Energy supply and use"
# (era "Non-fossil end-use fuels (including biofuels)"); o valor antigo passou a
# sair na Class_1. Em 15/09/2026 a equipe subiu as três dimensões duas posições
# e esse rótulo fixo DEIXOU DE SAIR — fica aqui só como registro do que havia
# antes, para quem for comparar com uma planilha velha.
GRUPO_ANTIGO = "Non-fossil end-use fuels (including biofuels)"   # não sai mais
GRUPO = "Energy supply and use"
UNIDADE = "GWh"
FATOR   = 1e-3          # o modelo grava MWh
SUPORTA_UF = True

ATIVOS = ["BECCSEthanolv2", "BECCSDieselv2", "BECCSATJ", "BECCSCharcoal",
          "BECCSHydrogen", "FischerTropsch", "HEFA", "SyntheticLiquidFuels",
          "SyntheticNaturalGas", "BioGasifSNG", "Electrolyzer",
          "ThermalHydrogen{NaturalGas}", "ThermalHydrogenCCS{NaturalGas}"]

# nó de destino -> Class_3 produto
PRODUTO = {
    "ethanol":            "Hydrous ethanol",
    "charcoal":           "Charcoal",
    "biodiesel":          "Biodiesel",
    "renewable_diesel":   "Renewable diesel",
    "jetfuel_SAF":        "Sustainable aviation fuel",
    "gasoline_renewable": "Renewable gasoline",
    "natgas_nonfossil":   "Biomethane",
    "h2":                 "Hydrogen",
}

# família do resource_id -> (Class_4 matéria-prima, Class_5 tecnologia)
ROTA = {
    # etanol — 1G / 1G2G / 2G, como na planilha ethanol_flows
    "BECCS_sugarcane_ethanol":          ("Sugarcane",       "1G"),
    "BECCS_sugarcane_ethanol_existing": ("Sugarcane",       "1G"),
    "BECCS_sugarcane_ethanol_CCS":      ("Sugarcane",       "1G with CCS"),
    "BECCS_1G2G_sugarcane_ethanol":     ("Sugarcane",       "1G2G"),
    "BECCS_1G2G_sugarcane_ethanol_CCS": ("Sugarcane",       "1G2G with CCS"),
    "BECCS_corn_ethanol":               ("Corn",            "1G"),
    "BECCS_corn_ethanol_existing":      ("Corn",            "1G"),
    "BECCS_corn_ethanol_CCS":           ("Corn",            "1G with CCS"),
    "BECCS_Lignocellulosic_ethanol":    ("Lignocellulosic", "2G"),
    "BECCS_Lignocellulosic_ethanol_CCS":("Lignocellulosic", "2G with CCS"),
    # biodiesel
    "Macauba_FAME":                     ("Macauba",         "FAME"),
    "Soybean_Biodiesel_large":          ("Soybean",         "FAME"),
    "Soybean_Biodiesel_large_existing": ("Soybean",         "FAME (existing)"),
    # carvão vegetal
    "BECCS_charcoal":                   ("Wood",            "Carbonization"),
    "BECCS_residue_charcoal":           ("Residue",         "Carbonization"),
    # hidrogênio
    "residue_H2":                       ("Residue",         "Gasification"),
    "residue_H2_CCS":                   ("Residue",         "Gasification with CCS"),
    "wood_H2":                          ("Wood",            "Gasification"),
    "wood_H2_CCS":                      ("Wood",            "Gasification with CCS"),
    "Electrolyzer":                     ("Electricity",     "Electrolysis"),
    "ThermalHydrogen{NaturalGas}":      ("Natural gas",     "Steam methane reforming"),
    "ThermalHydrogenCCS{NaturalGas}":   ("Natural gas",     "Steam methane reforming with CCS"),
    # rotas avançadas
    "BR_ATJ_ethanol":                   ("Ethanol",         "Alcohol-to-jet"),
    "BR_ATJ_Diesel":                    ("Ethanol",         "Alcohol-to-jet"),
    "HEFA_macauba":                     ("Macauba",         "HEFA"),
    "HEFA_soybean":                     ("Soybean",         "HEFA"),
    "greendiesel_wood_FT":              ("Wood",            "Fischer-Tropsch"),
    "greendiesel_residue_FT":           ("Residue",         "Fischer-Tropsch"),
    "gasoline_wood_FT":                 ("Wood",            "Fischer-Tropsch"),
    "gasoline_residue_FT":              ("Residue",         "Fischer-Tropsch"),
    "Synthetic_FT":                     ("CO2 and hydrogen","Fischer-Tropsch (e-fuel)"),
    "Synthetic_natgas":                 ("CO2 and hydrogen","Methanation (e-fuel)"),
    "biogasif_sng":                     ("Residue",         "Gasification"),
    "biogasif_sng_ccs":                 ("Residue",         "Gasification with CCS"),
}


def _produto(node_out):
    n = re.sub(r"_BR(_[A-Z]{2})?$", "", str(node_out))
    return PRODUTO.get(n)


def gerar(root: Path, por_uf: bool = False, **kw):
    reg = {}
    for p, year in PERIODS.items():
        d = fluxos(root, p)
        d = d[d.resource_type.isin(ATIVOS) & (d.value > 0) & d.node_out.map(eh_no)]
        for r in d.itertuples():
            prod = _produto(r.node_out)
            if prod is None:
                continue
            fam = re.sub(r"^BR_[A-Z]{2}_", "", str(r.resource_id))
            c4, c5 = ROTA.get(fam) or ROTA.get(r.resource_type) or ("NA", fam)
            terr = uf_de(r.resource_id) if por_uf else "BR"
            k = (prod, c4, c5, terr)
            reg.setdefault(k, {}).setdefault(year, 0.0)
            reg[k][year] += float(r.value)

    ordem = list(PRODUTO.values())
    out = []
    for k in sorted(reg, key=lambda x: (ordem.index(x[0]), x[1], x[2], x[3])):
        prod, materia, tecnologia, terr = k
        for year in PERIODS.values():
            # AS TRÊS DIMENSÕES SUBIRAM DUAS POSIÇÕES (pedido da equipe,
            # 15/09/2026): produto na Class_1, matéria-prima na Class_2,
            # tecnologia na Class_3, e Class_4/Class_5 em "NA". Antes eram
            # Class_3/4/5, com GRUPO_ANTIGO na Class_1 e "Fuel production" na
            # Class_2 — os dois rótulos fixos saem da saída, porque o
            # Variable_group já diz "Energy supply and use" e a variável já se
            # chama "...production by technology". Nenhum valor muda; o que
            # muda é em que coluna cada dimensão chega ao dashboard.
            out.append(row(GRUPO, NOME, c1=prod, c2=materia, c3=tecnologia,
                           c4="NA", c5="NA",
                           unit=UNIDADE, territory=terr, year=year,
                           value=round(reg[k].get(year, 0.0) * FATOR, 5)))
    return out
