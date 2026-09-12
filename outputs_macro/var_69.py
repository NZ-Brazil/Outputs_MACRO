# -*- coding: utf-8 -*-
"""id 69 — Renewable power area by type (wind and solar).

Fonte: results_period_<p>/results_period_<p>/capacity.csv (mesmo filtro da 66)
       + densidades de potência EXÓGENAS, definidas abaixo.

area (km2) = capacidade instalada (MW) / densidade (MW/km2)
area (Mha) = area (km2) / 10.000

As densidades NÃO estão no input do modelo — são premissa fornecida pela
equipe. Editar aqui é o único lugar que muda o resultado desta variável.
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, capacidade, row
from ._eletrico import C2, C3, classificar

NOTA  = NOTAS[69]
RESUMO  = RESUMOS[69]

ID    = 69
NOME  = "Renewable power area by type"
COL2  = "Variable name"
GRUPO = "Energy supply and use"    # era "Power" (pedido da equipe, 11/09/2026)
UNIDADE = "Mha"

# Ligado em 02/09/2026 (correção incorporada de outra rodada). A UF sai direto
# da zona do capacity.csv. O nacional e as UFs saem no mesmo arquivo: somar
# Value sem filtrar Territory dobra o resultado.
SUPORTA_UF = True

# (Class_4, Class_5) -> densidade de potência em MW/km2
DENSIDADE = {
    ("Solar photovoltaic", "Utility-scale"): 33.0,
    ("Wind", "Onshore"):                      5.3,
    ("Wind", "Offshore"):                     5.3,   # área marítima, ver nota
}

# Rooftop não ocupa solo: fica de fora por definição, não por falta de dado.
EXCLUIR = {("Solar photovoltaic", "Rooftop")}

KM2_POR_MHA = 10_000.0


def gerar(root: Path, por_uf: bool = False, **kw):
    reg = {}
    for p, year in PERIODS.items():
        d = capacidade(root, p)
        d = d[(d.variable == "capacity") & (d.commodity == "Electricity")
              & (d.resource_type == "VRE{Generic}")]
        for r in d.itertuples():
            c4, c5 = classificar(r.resource_type, r.resource_id)
            if (c4, c5) in EXCLUIR or (c4, c5) not in DENSIDADE:
                continue
            terr = str(r.zone).replace("BR_", "") if por_uf else "BR"
            k = (c4, c5, terr)
            reg.setdefault(k, {}).setdefault(year, 0.0)
            reg[k][year] += float(r.value) / DENSIDADE[(c4, c5)] / KM2_POR_MHA

    out = []
    for c4, c5, terr in sorted(reg):
        for year in PERIODS.values():
            out.append(row(GRUPO, NOME, c1=c4, c2=c5, c3=C3, c4="NA", c5="NA",  # classes reorganizadas a pedido da equipe (11/09/2026)
                           unit=UNIDADE, territory=terr, year=year,
                           value=round(reg[(c4, c5, terr)].get(year, 0.0), 6)))
    return out
