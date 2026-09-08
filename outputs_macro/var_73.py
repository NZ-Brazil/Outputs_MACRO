"""id 73 — CO2 storage: taxa anual de injeção, por UF e por bacia.

Fonte: flows_annual/flows_annual_results_period_<p>.csv

Os nós de transporte carregam UF e bacia no nome (co2_transported_BR_MS_Parana).
A injeção puxa desses nós (co2_captured_edge, valor negativo) e empurra para o
reservatório. Uso a aresta de entrada, que dá UF e bacia de uma vez.

RECORTE: Territory = UF e a bacia na Class_3 (correção incorporada de outra
rodada, 02/09/2026; antes a bacia ocupava o Territory e a UF era descartada).
Somar por Class_3 devolve o total da bacia. Há também a linha nacional
(Territory = BR, Class_3 = N/A) somando tudo.

RESSALVA: em 2050, 494 dos 516 Mt vêm do etanol de cana, então esta variável
herda inteiro o problema do co2_content da cana (base seca x base úmida).
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, fluxos, row
from ._co2 import GRUPO, C2, de_no

NOTA  = NOTAS[73]
RESUMO  = RESUMOS[73]

ID    = 73
NOME  = "CO2 storage"
COL2  = "Variable name"
UNIDADE = "MtCO2/year"
FATOR   = 1e-6          # fluxos em toneladas


def gerar(root: Path, **kw):
    reg, nacional = {}, {}            # reg[(uf, bacia)][ano]
    for p, year in PERIODS.items():
        d = fluxos(root, p)
        d = d[(d.resource_type == "CO2Injection") & (d.commodity == "CO2Captured")
              & (d.value < 0)]
        for r in d.itertuples():
            uf, bacia = de_no(r.node_in)
            if bacia is None:
                continue
            reg.setdefault((uf, bacia), {}).setdefault(year, 0.0)
            reg[(uf, bacia)][year] += -float(r.value)
            nacional[year] = nacional.get(year, 0.0) - float(r.value)

    def linhas(terr, bacia, serie):
        return [row(GRUPO, NOME, c1="Energy", c2=C2, c3=bacia, c4="N/A", c5="N/A",
                    unit=UNIDADE, territory=terr, year=year,
                    value=round(serie.get(year, 0.0) * FATOR, 5))
                for year in PERIODS.values()]

    out = linhas("BR", "N/A", nacional)                 # total nacional
    for uf, bacia in sorted(reg, key=lambda x: (x[1], x[0])):
        out += linhas(uf, bacia, reg[(uf, bacia)])
    return out
