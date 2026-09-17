# -*- coding: utf-8 -*-
"""id 19 — Emissions and removals : REMOVAL BY CCS ONLY, por matéria-prima.

Fonte: flows_annual/flows_annual_results_period_<p>.csv, commodity CO2Captured.
Remoção = fluxo POSITIVO na própria aresta de captura do ativo que captura
(o ativo entrega ao nó a jusante), restrito aos resource_type em
E.CONVERSAO (BECCS/biomassa + ElectricDAC).

MUDANÇA DE CONVENÇÃO (16/09/2026): até aqui esta variável era a absorção
BRUTA de carbono pela biomassa — `co2_content`, commodity CO2, fluxo negativo
saindo de co2_emitted_BR. Ela virou o CO2 efetivamente CAPTURADO e enviado
para armazenamento — commodity CO2Captured — e o nome mudou de "Removals"
para "Removal by CCS only" para deixar isso explícito. Rota sem CCS (ex.:
"Biomass power" sem "with CCS" no nome) não captura nada e sai desta
variável com valor zero, o que é esperado.

POR QUE A MUDANÇA: a id 18 (var_18.py) parou de contar a combustão de
biomassa como emissão em 16/09/2026. Sem esta mudança correspondente, o
"líquido" (id 18 + id 19) passaria a subtrair a absorção bruta inteira da
biomassa — inclusive a parte que volta para a atmosfera na queima — em vez
de só o carbono que de fato saiu do ciclo. Ver a nota de leitura da id 18
para o histórico do mal-entendido que motivou as duas mudanças.

CCS FÓSSIL FICA DE FORA, E É AUTOMÁTICO: os únicos resource_type com uma
aresta de commodity CO2Captured são os ativos em E.CONVERSAO e os ativos de
CCS fóssil (ThermalPowerCCS, ThermalHydrogenCCS — em E.FOSSIL_ASSET, não em
E.CONVERSAO). Filtrar por `resource_type in E.CONVERSAO` já exclui a captura
fóssil sem precisar subtrair nada à parte depois. Isso é necessário porque a
id 18 já reporta a emissão desses ativos LÍQUIDA do que foi capturado (o
emission_rate deles já é pós-captura); somar a captura fóssil aqui de novo
dobraria a conta, só que do lado fóssil.

NaturalGasDAC também tem aresta CO2Captured (mistura CO2 atmosférico com CO2
da própria queima de gás que ele consome), mas não está em E.CONVERSAO nem
em E.FOSSIL_ASSET hoje — fica de fora desta variável e da id 18 até alguém
decidir como separar as duas partes da captura dele.

CLASSES: o SEEG é uma taxonomia de EMISSÃO e não tem galho para remoção, então
esta variável usa a estrutura do diagrama de rotas da equipe:

    Class_1 = família da matéria-prima   Primary crops / Herbaceous residues /
                                         Woody biomass
    Class_2 = matéria-prima              Sugarcane, Corn, Soybean, Sugarcane
                                         straw, Corn stover, Rice straw,
                                         Forestry residues, Plantation forestry
    Class_3 = rota de conversão          Sugarcane ethanol, Biomass power,
                                         Gasification H2, Charcoal kiln...
    Class_4 = vetor energético           Ethanol, Electricity, Hydrogen...
    Class_5 = gás

COMO A REMOÇÃO É LIGADA À MATÉRIA-PRIMA: o CO2 capturado é registrado no
ATIVO de conversão, não na biomassa, e o MACRO o calcula como `capture_rate
do ativo x fluxo da aresta PRINCIPAL` — mesma estrutura de aresta única que o
co2_content usava antes, só que com o coeficiente de captura. Então cada
remoção vai inteira para a commodity dessa aresta; não há o que ratear.

A aresta principal é o biomass_edge, ou o origin_edge nos ativos de coleta de
palha (cornstover_trans, ricestraw_trans, sugarcanestraw_trans), ou o
ethanol_edge no ATJ. O DAC não tem nenhuma das três e entra como CO2
atmosférico.

O `coinput_edge` FICA DE FORA, e essa é a correção em relação à versão
anterior, que rateava a captação pela massa de todas as entradas (correção
incorporada de outra rodada, 02/09/2026). Três rotas queimam lenha de floresta
plantada como co-insumo de processo — etanol de milho (21,2 Mt de lenha sobre
66,6 Mt de milho em 2025, 24%), FAME de soja (5,7%) e FAME de macaúba (6,5%) —
e o modelo não registra captação nenhuma sobre essa lenha. O rateio antigo
criava um crédito inexistente: em 2025 movia 30 Mt de Primary crops para Woody
biomass.
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, fluxos, row
from . import _emissoes as E
from ._biomassa import FEEDSTOCK, PRINCIPAL, conversao

NOTA   = NOTAS[19]
RESUMO = RESUMOS[19]

ID    = 19
NOME  = E.NOME
COL2  = E.COL2
VALOR_COL2 = "Removal by CCS only"


def gerar(root: Path, **kw):
    reg = {}
    for p, year in PERIODS.items():
        d = fluxos(root, p)
        # commodity CO2Captured, fluxo positivo (ativo entrega ao nó a
        # jusante), restrito a E.CONVERSAO: exclui CCS fóssil automaticamente
        # (ver docstring do módulo).
        rem = d[(d.commodity == "CO2Captured") & (d.value > 0)
                & d.resource_type.isin(E.CONVERSAO)]

        # matéria-prima de cada ativo = commodity da sua aresta principal.
        # Percorre PRINCIPAL de trás para frente para que a primeira da lista
        # (biomass_edge) sobrescreva as demais e ganhe a prioridade.
        ent = d[d.edge.isin(PRINCIPAL) & (d.value < 0)]
        principal = {}
        for aresta in reversed(PRINCIPAL):
            g = ent[ent.edge == aresta]
            for rid, sub in g.groupby("resource_id"):
                # value é negativo na entrada: idxmin devolve a de maior fluxo
                principal[rid] = sub.groupby("commodity").value.sum().idxmin()

        for r in rem.itertuples():
            c3, c4 = conversao(r.resource_id, r.resource_type)
            com = principal.get(r.resource_id, "CO2")   # sem entrada: DAC
            familia, c2 = FEEDSTOCK.get(com, ("NA", str(com)))
            k = (familia, c2, c3, c4)
            reg.setdefault(k, {}).setdefault(year, 0.0)
            reg[k][year] += float(r.value)  # já positivo (capturado, não conteúdo)

    # Class_1 sempre "Energy" (revisão do David, 09/09/2026, como no resto da
    # plataforma) — a família de matéria-prima (Primary crops/Herbaceous
    # residues/Woody biomass) some da Class_1, mas segue orientando a ordem
    # de saída das linhas.
    ordem = {"Primary crops": 0, "Herbaceous residues": 1, "Woody biomass": 2, "NA": 3}
    out = []
    for k in sorted(reg, key=lambda x: (ordem.get(x[0], 9), x[1], x[2], x[3])):
        familia, c2, c3, c4 = k
        for year in PERIODS.values():
            out.append(row(E.GRUPO, VALOR_COL2, c1="Energy", c2=c2, c3=c3, c4=c4,
                           c5=E.GAS,
                           unit=E.UNIDADE, territory="BR", year=year,
                           value=round(-reg[k].get(year, 0.0) * E.FATOR, 5)))
    return out
