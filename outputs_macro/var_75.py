# -*- coding: utf-8 -*-
"""id 75 — Capex.

Fonte: results_period_<p>/results_period_<p>/capex.csv

Acrescentada em 02/09/2026, a pedido do usuário. Duas linhas de leitura na
mesma variável, distinguidas pela Class_2 ("CAPEX" x "Total Investment
Cost"):

CAPEX (uma linha por ano, 2025-2050): soma da coluna value de capex.csv do
período — capex BRUTO do período, todas as commodities e tecnologias
somadas juntas, sem desconto e sem amortização. Não é o mesmo número que a
categoria "Investment" de costs_by_type.csv (usada nas ids 24 e 26): aquela
é o custo de investimento como o modelo o computa no objetivo, descontado ao
ano-base — os dois valores não batem (conferido com os dados reais do
usuário: no período 1, capex.csv soma ~33,5 bi contra ~49,0 bi da categoria
Investment de costs_by_type.csv).

Total Investment Cost (uma linha só, ano 2025): soma do CAPEX de TODOS os
seis períodos — não é uma série por ano, é um valor agregado único. Por
pedido explícito do usuário, essa linha só existe no ano de 2025 (as outras
linhas de ano para essa Class_2 não são geradas) — não confundir com a linha
de CAPEX de 2025, que é uma Class_2 diferente e traz só o capex daquele
período.
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, capex_periodo, row

NOTA   = NOTAS[75]
RESUMO = RESUMOS[75]

ID    = 75
NOME  = "Capex"
COL2  = "Variable name"
GRUPO = "Economy"
UNIDADE = "US$"


def gerar(root: Path, **kw):
    capex_por_ano = {year: capex_periodo(root, p) for p, year in PERIODS.items()}

    out = [row(GRUPO, NOME, c1="Energy", c2="CAPEX",
               unit=UNIDADE, territory="BR", year=year,
               value=round(v, 5))
           for year, v in capex_por_ano.items()]

    total = sum(capex_por_ano.values())
    out.append(row(GRUPO, NOME, c1="Energy", c2="Total Investment Cost",
                   unit=UNIDADE, territory="BR", year=2025,
                   value=round(total, 5)))
    return out
