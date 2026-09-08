"""id 18 — Emissions and removals : EMISSÕES.

Fonte: flows_annual/flows_annual_results_period_<p>.csv, commodity CO2.
Emissão = fluxo POSITIVO (entrando em co2_emitted_BR).

Convenção MACRO (ver _emissoes.py). Inclui, portanto, a combustão de biomassa,
que o SEEG não contaria.
"""
from pathlib import Path
from .comum import PERIODS, fluxos, row
from . import _emissoes as E
from ._notas import NOTAS
from ._resumos import RESUMOS

ID    = 18
NOME  = E.NOME
COL2  = E.COL2
VALOR_COL2 = "Emissions"

NOTA = NOTAS[18]
RESUMO = RESUMOS[18]


def gerar(root: Path, **kw):
    reg = {}
    for p, year in PERIODS.items():
        d = fluxos(root, p)
        origem = E.origens_combustivel(d)
        co2 = d[(d.commodity == "CO2") & (d.value > 0)]
        for r in co2.itertuples():
            k = E.classificar(r.resource_type, r.resource_id,
                              origem.get(r.resource_id))
            reg.setdefault(k, {}).setdefault(year, 0.0)
            reg[k][year] += float(r.value)

    out = []
    for k in sorted(reg):
        c1, c2, c3, c4, c5 = k
        for year in PERIODS.values():
            out.append(row(E.GRUPO, VALOR_COL2, c1=c1, c2=c2, c3=c3, c4=c4, c5=c5,
                           unit=E.UNIDADE, territory="BR", year=year,
                           value=round(reg[k].get(year, 0.0) * E.FATOR, 5)))
    return out
