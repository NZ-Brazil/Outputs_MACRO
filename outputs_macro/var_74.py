"""id 74 — CO2 transport (km de duto), por bacia sedimentar.

A distância vem do input (assets_<ano>/co2_pipeline.csv); o resultado diz quais
dutos operam. Aqui a distância É usada no custo de investimento
(0/100/200/300/900 km -> 0/158.223/307.999/448.767/1.164.992 US$/MW), então é
dado operante — diferente da transmissão elétrica, cujo input traz a nota
"distance for record-purpose only".

SEM LIMIAR DE FLUXO (correção incorporada de outra rodada, 02/09/2026). A
versão anterior só contava o duto com fluxo anual acima de 0,1 Mt, e a série
publicada saía inteiramente determinada por esse corte — 0 km em 2025 e 2030
com o limiar de 0,1 Mt, 9.500 km constantes sem limiar, e valores
intermediários para qualquer outro valor. O corte não vinha do modelo nem da
plataforma, era escolha nossa. Agora conta todo duto em operação (fluxo > 0)
com distância declarada: dá 9.500 km em todos os períodos, que é o resultado
do modelo — ele dá capacidade à rede inteira já no período 1 e não a expande.

Territory = UF e a bacia na Class_3 (correção incorporada de outra rodada,
02/09/2026; antes a bacia ocupava o Territory e a UF era descartada).

Alternativa se a plataforma quiser algo que varie de fato: Mt.km transportado
(75 / 99 / 16.972 / 29.001 / 49.105 / 74.224).
"""
from pathlib import Path
import pandas as pd
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, inputs_dir, fluxos, row
from ._co2 import GRUPO, C2, de_duto

NOTA  = NOTAS[74]
RESUMO  = RESUMOS[74]

ID    = 74
NOME  = "CO2 transport"
COL2  = "Variable name"
UNIDADE = "km"

LIMIAR = 0.0            # toneladas/ano — sem corte (ver nota)


def gerar(root: Path, inputs: Path | None = None, **kw):
    base = inputs or (inputs_dir(root) / "assets")
    reg = {}
    for p, year in PERIODS.items():
        src = pd.read_csv(base / f"assets_{year}" / "co2_pipeline.csv")
        dist = dict(zip(src["id"], src["edges--transmission_edge--distance"]))
        d = fluxos(root, p)
        d = d[(d.resource_type == "OneWayTransmissionLink{CO2Captured}") & (d.value > 0)]
        for rid, v in d.groupby("resource_id")["value"].sum().items():
            km = float(dist.get(rid, 0.0))
            if v <= LIMIAR or km <= 0:
                continue
            uf, bacia = de_duto(rid)
            reg.setdefault((uf, bacia), {}).setdefault(year, 0.0)
            reg[(uf, bacia)][year] += km

    # Territory = UF e bacia na Class_3, como na id 73. Sem linha nacional:
    # somar km de dutos de bacias diferentes não descreve uma rede única.
    out = []
    for uf, bacia in sorted(reg, key=lambda x: (x[1], x[0])):
        for year in PERIODS.values():
            out.append(row(GRUPO, NOME, c1="Energy", c2=C2, c3=bacia,
                           c4="N/A", c5="Pipeline",
                           unit=UNIDADE, territory=uf, year=year,
                           value=round(reg[(uf, bacia)].get(year, 0.0), 5)))
    return out
