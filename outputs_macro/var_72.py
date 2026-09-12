# -*- coding: utf-8 -*-
"""id 72 — Fossil fuel prices.

Fonte: system/fuel_prices_<ano>.csv — INPUT do modelo, não resultado. É um preço
exógeno, premissa de cenário, não um preço de equilíbrio calculado.

O arquivo tem 2016 linhas (uma por timestep), mas o preço é constante dentro de
cada período em todas as colunas — então basta a primeira linha.

O URÂNIO SAIU (correção incorporada de outra rodada, 02/09/2026). Ele está no
input (uranium_price_BR) mas urânio não é combustível fóssil, e o nome da
variável enumera os cinco que ela quer: gasolina, diesel, querosene, gás
natural e carvão. Se um dia for preciso reportá-lo, é só devolver a linha aqui.
"""
from pathlib import Path
import pandas as pd
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, inputs_dir, row

NOTA  = NOTAS[72]
RESUMO  = RESUMOS[72]

ID    = 72
NOME  = "Fossil fuel prices"
COL2  = "Variable name"
GRUPO = "Energy supply and use"    # era "Fossil fuels industry" (11/09/2026)
UNIDADE = "US$/boe"
# 1 MWh = 0,6061 boe  =>  preço em US$/boe = preço em US$/MWh / 0,6061
BOE_POR_MWH = 0.6061

# coluna do arquivo -> Class_2 (o combustível é a categoria desta variável;
# as demais classes ficam N/A porque o SEEG não tem um galho para preços)
COMBUSTIVEL = {
    "natgas_price_BR":          "Natural gas",
    "coal_price_BR":            "Coal (domestic)",
    "coal_price_imported":      "Coal (imported)",
    "gasoline_fossil_price_BR": "Gasoline (fossil)",
    "diesel_fossil_price_BR":   "Diesel (fossil)",
    "jetfuel_fossil_price_BR":  "Jet fuel (fossil)",
}


def gerar(root: Path, inputs: Path | None = None, **kw):
    base = inputs or (inputs_dir(root) / "system")
    serie = {}
    for p, year in PERIODS.items():
        d = pd.read_csv(base / f"fuel_prices_{year}.csv")
        linha = d.drop(columns=["Time_Index"]).iloc[0]
        for col, valor in linha.items():
            serie.setdefault(col, {})[year] = float(valor)

    out = []
    for col in COMBUSTIVEL:
        if col not in serie:
            continue
        for year in PERIODS.values():
            # Class_1 vira o combustível (era Class_2), Class_2 vira "NA"
            # (revisão do David, 09/09/2026).
            out.append(row(GRUPO, NOME, c1=COMBUSTIVEL[col], c2="NA",
                           c3="NA", c4="NA", c5="NA",
                           unit=UNIDADE, territory="BR", year=year,
                           value=round(serie[col].get(year, 0.0) / BOE_POR_MWH, 5)))
    return out
