"""id 24 — Total energy system cost.

Fonte: results_period_<p>/results_period_<p>/costs_by_type.csv

Receita acordada: Investment + FixedOM + VariableOM + Supply
                  - Supply de gasolina, diesel e querosene fóssil.
Equivale a: Total - NonServedDemand - os três Supply fósseis.

Sem anualizar: o valor é o presente do quinquênio, descontado ao ano-base.
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, custos_por_tipo, row

NOTA  = NOTAS[24]
RESUMO  = RESUMOS[24]

ID    = 24
NOME  = "Total energy system cost"
COL2  = "Variable name"
GRUPO = "Energy supply and use"    # era "Economy" (revisão do David, 09/09/2026)
UNIDADE = "US$"

SUPRIMENTO_FOSSIL = ["Node{MacroEnergy.Gasoline}",
                     "Node{MacroEnergy.Diesel}",
                     "Node{MacroEnergy.JetFuel_Fossil}"]


def gerar(root: Path, **kw):
    out = []
    for p, year in PERIODS.items():
        g = custos_por_tipo(root, p)
        v = sum(g.get(("Total", c), 0.0)
                for c in ("Investment", "FixedOM", "VariableOM", "Supply"))
        v -= sum(g.get((t, "Supply"), 0.0) for t in SUPRIMENTO_FOSSIL)
        out.append(row(GRUPO, NOME, c1="NA", unit=UNIDADE, territory="BR",
                       year=year, value=round(v, 5)))
    return out
