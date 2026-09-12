# -*- coding: utf-8 -*-
"""id 56 — Energy demand.

NOME: 'Energy demand' (correção incorporada de outra rodada, 02/09/2026; antes
'Energy end-use by energy carrier'). O recorte por portador continua sendo o
que a variável entrega.

Fonte: flows_annual/flows_annual_results_period_<p>.csv

COMBUSTÍVEIS: demanda final = saldo NEGATIVO dos nós de demanda (ver
comum.saldo_nos). Usar a fuel_demand_edge do GeneralFuelsEndUse não serve: o
diesel fóssil chega ao nó de demanda pelo UpstreamEmissions, não pelo
Downstream, e ficariam de fora 596 dos 596,3 TWh de 2050.

ELETRICIDADE: vem do saldo dos nós elec_BR_<UF>, que carrega as perdas de
transmissão alocadas na chegada.

"AND END USE" NÃO É POSSÍVEL. O MACRO agrega a demanda final num nó por
combustível — não há separação por setor de uso (transportes, indústria,
residencial, comercial). Por isso Class_2 vai como N/A e a variável entrega
apenas o recorte por portador.

AGRUPADA POR PORTADOR, uma linha por portador e por ano, Class_5 = N/A
(correção incorporada de outra rodada, 02/09/2026). Os nós de mandato
(biodiesel, jetfuel fóssil, SAF) entram somados ao portador correspondente —
o biodiesel obrigatório vira Diesel, os três nós de querosene viram Jet fuel —
porque a plataforma quer o portador e não o instrumento. Para recuperar a
abertura por instrumento basta devolver o terceiro campo da lista PORTADORES
abaixo; o efeito no total por portador é nenhum.

RECORTE POR ESTADO (correção incorporada de outra rodada, 02/09/2026). Dois
portadores têm nó estadual no modelo: eletricidade (elec_BR_<UF>) e hidrogênio
(h2_BR_<UF>), 27 nós cada. Os demais são um nó nacional único e saem só na
linha BR, como os fósseis da id 55. O arquivo traz o nacional E o estadual:
somar Value sem filtrar Territory dobra a eletricidade e o hidrogênio.
"""
from pathlib import Path
import re
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, saldo_nos, row

NOTA  = NOTAS[56]
RESUMO  = RESUMOS[56]

ID    = 56
NOME  = "Energy demand"
COL2  = "Variable name"
GRUPO = "Energy supply and use"
UNIDADE = "GWh"
FATOR   = 1e-3

# Rótulo que ocupa Class_1, Class_2 e Class_3 (pedido da equipe, 12/09/2026).
USO_FINAL = "Various energy end uses"

SUPORTA_UF = True

# Nó estadual: <portador>_BR_<UF>. Não vale testar só _<UF> no fim, porque
# charcoal_BR terminaria em 'BR' e viraria um estado.
_UF_NO = re.compile(r"_BR_([A-Z]{2})$")

# padrão do nó de demanda -> (Class_4 portador, tem nó por estado?)
#
# SÓ ELETRICIDADE E HIDROGÊNIO TÊM RECORTE ESPACIAL. Os dois têm 27 nós
# (elec_BR_<UF>, h2_BR_<UF>); os demais portadores são um nó nacional único no
# modelo e saem só na linha BR — mesma lógica da id 55 com os fósseis.
PORTADORES = [
    (r"diesel_demand_BR$",                 "Diesel",      False),
    (r"biodiesel_mandate_demand_BR$",      "Diesel",      False),
    (r"flexfuel_demand_BR$",               "Flexfuel",    False),
    (r"natgas_demand_BR$",                 "Natural gas", False),
    (r"ethanol_demand_BR$",                "Ethanol",     False),
    (r"charcoal_BR$",                      "Charcoal",    False),
    (r"gasoline_demand_BR$",               "Gasoline",    False),
    (r"jetfuel_fossil_mandate_demand_BR$", "Jet fuel",    False),
    (r"jetfuel_flex_demand_BR$",           "Jet fuel",    False),
    (r"jetfuel_SAF_mandate_demand_BR$",    "Jet fuel",    False),
    (r"h2_BR(_[A-Z]{2})?$",                "Hydrogen",    True),
    (r"elec_BR_[A-Z]{2}$",                 "Electricity", True),
]


def gerar(root: Path, por_uf: bool = False, **kw):
    reg = {}
    for p, year in PERIODS.items():
        s = saldo_nos(root, p)
        for pat, c4, espacial in PORTADORES:
            if por_uf and not espacial:
                continue                    # portador nacional: só a linha BR
            for no, val in s.items():
                if not re.match(pat, str(no)):
                    continue
                terr = "BR"
                if por_uf:
                    m = _UF_NO.search(str(no))
                    if not m:
                        continue
                    terr = m.group(1)
                k = (c4, terr)
                reg.setdefault(k, {}).setdefault(year, 0.0)
                reg[k][year] += -val * FATOR   # saldo negativo = consumo

    out = []
    for c4, terr in sorted(reg):
        for year in PERIODS.values():
            # Class_1, Class_2 e Class_3 repetem "Various energy end uses"
            # (pedido da equipe, 12/09/2026 — antes eram "Energy", "NA" e o
            # rótulo). Class_4 continua com o combustível.
            out.append(row(GRUPO, NOME, c1=USO_FINAL, c2=USO_FINAL, c3=USO_FINAL,
                           c4=c4, c5="NA",
                           unit=UNIDADE, territory=terr, year=year,
                           value=round(reg[(c4, terr)].get(year, 0.0), 5)))
    return out
