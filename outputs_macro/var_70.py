# -*- coding: utf-8 -*-
"""id 70 — Transmission lines (capacidade, não km).

Fonte: results_period_<p>/results_period_<p>/capacity.csv,
       variable == 'capacity', commodity == 'Electricity',
       resource_type TransmissionLink{Electricity} e
       OneWayTransmissionLink{Electricity}.

A PLANILHA DA PLATAFORMA PEDE km. Não dá: o input traz a nota "cost values are
placeholders, distance for record-purpose only" e o investment_cost é idêntico
nos 31 corredores, de 136 a 1.807 km — a distância não entra na otimização e
somar km dos corredores em operação daria uma série que não descreve nada.

A CAPACIDADE, sim, é resultado: o modelo decide quanto expandir cada corredor.
Por isso esta variável reporta MW de capacidade de transmissão, em GW.

    ano    capacidade    da qual nova no período
    2025      152,8            57,5
    2030      166,4            13,6
    2035      198,8            32,4
    2040      205,6             6,8
    2045      228,1            22,4
    2050      252,0            24,0     (GW)

Nada se aposenta em nenhum período.

RESSALVA DO ESTOQUE INICIAL: a mesma nota do input diz "SOME existing capacity
values are placeholders", e é visível quais. Os 26 corredores que ligam um
subsistema a um estado (e os dois interestaduais AC–RO e RO–MT) têm
existing_capacity de exatamente 1.000 MW cada — 26 dos 95,3 GW de 2025, ou 27%.
Os demais são plausíveis: Itaipu–SE 10.000, Belo Monte–SE 8.000, SE–S 11.450 e
S–SE 8.000, NE–SE 9.911, e as três pernas do hub IMP com 5.700, 6.089 e 9.107.
Em 2050 o peso do placeholder cai para 10% do estoque, porque o resto é
expansão otimizada.

O NÓ 'IMP' NÃO É UM SUBSISTEMA: é um nó de trânsito por onde N e NE despacham
para o SE (16,1 e 12,2 TWh entram, 27,4 TWh saem para o SE em 2050). Os
corredores N–IMP, NE–IMP e SE–IMP juntos são a interligação Norte/Nordeste–
Sudeste; lidos isoladamente não têm equivalente na rede real.

SUDESTE–SUL APARECE DUAS VEZES, uma por sentido (11.464 e 8.003 MW em 2050), porque o
modelo usa dois OneWayTransmissionLink para a mesma interligação física. O
total nacional soma os dois, que é o certo para 'capacidade de transporte
instalada' e errado para 'quantos corredores existem'.
"""
from pathlib import Path
import re
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, capacidade, row

NOTA   = NOTAS[70]
RESUMO = RESUMOS[70]

ID    = 70
NOME  = "Transmission lines"
# Corredor migra para Class_2 (era Class_3). Depois da reorganização de
# 11/09/2026 o nome do corredor JÁ é escrito em Class_2 pelo próprio gerar(); a
# migração espacial aponta para o mesmo slot, e por isso só reescreve o valor
# que já está lá — Class_3 fica "NA", como pedido. Ver comum.padronizar_territorio.
CLASS_ESPACIAL = 2
COL2  = "Variable name"
GRUPO = "Energy supply and use"    # era "Power" (pedido da equipe, 11/09/2026)
UNIDADE = "GW"
FATOR   = 1e-3          # o modelo grava MW

TIPOS = {"TransmissionLink{Electricity}", "OneWayTransmissionLink{Electricity}"}

# Nós que não são estado: subsistemas do SIN e nós de trânsito. O nome por
# extenso é obrigatório, não é enfeite: 'SE' é ao mesmo tempo o subsistema
# Sudeste/Centro-Oeste e a sigla de Sergipe, e NE_to_SE_transmission (Nordeste
# -> Sudeste, 31,2 GW em 2050) colidia com NE_to_BR_SE_transmission (Nordeste
# -> Sergipe, 1,0 GW) num rótulo só.
PROXY = {
    "N":   "Norte",
    "NE":  "Nordeste",
    "SE":  "Sudeste",          # inclui o Centro-Oeste, como no ONS
    "S":   "Sul",
    "IMP": "IMP",              # nó de trânsito, não é região — ver a nota
    "ITA": "Itaipu",
    "BM":  "Belo Monte",
}

INTER   = "Interregional"
SUB_UF  = "Subsystem to state"
INTER_UF = "Interstate"


def _pontas(rid: str):
    """(('NE', False), ('BA', True), False) para NE_to_BR_BA_transmission.

    O segundo campo de cada ponta diz se ela é ESTADO, e vem do prefixo BR_ do
    próprio id — não da sigla. Testar a sigla contra a lista de subsistemas não
    funciona: 'SE' é Sudeste e é Sergipe, e só o prefixo separa os dois.
    """
    s = re.sub(r"_transmission(_oneway)?$", "", str(rid))
    umsentido = str(rid).endswith("_oneway")
    a, _, b = s.partition("_to_")
    pega = lambda x: (x[3:], True) if x.startswith("BR_") else (x, False)
    return pega(a), pega(b), umsentido


def _rotulo(rid: str):
    (a, a_uf), (b, b_uf), umsentido = _pontas(rid)
    seta = "→" if umsentido else "–"      # → para um sentido, – para dois
    if not a_uf and not b_uf:
        tipo = INTER
    elif a_uf and b_uf:
        tipo = INTER_UF
    else:
        tipo = SUB_UF
    nome = lambda x, uf: x if uf else PROXY.get(x, x)
    return f"{nome(a, a_uf)}{seta}{nome(b, b_uf)}", tipo


def gerar(root: Path, **kw):
    reg = {}
    for p, year in PERIODS.items():
        d = capacidade(root, p)
        d = d[(d.variable == "capacity") & (d.commodity == "Electricity")
              & d.resource_type.isin(TIPOS)]
        for rid, v in d.groupby("resource_id")["value"].sum().items():
            corredor, tipo = _rotulo(rid)
            # SEM LINHA NACIONAL: o corredor migra para a Class_3 e o
            # Territory de todo mundo vira BR, então uma linha nacional junto
            # seria indistinguível das partes e dobraria a soma. Os 35
            # corredores somam o total do país.
            k = (tipo, corredor)
            reg.setdefault(k, {}).setdefault(year, 0.0)
            reg[k][year] += float(v) * FATOR

    ordem = {"NA": 0, INTER: 1, SUB_UF: 2, INTER_UF: 3}
    out = []
    for k in sorted(reg, key=lambda x: (ordem[x[0]], x[1])):
        tipo, terr = k
        for year in PERIODS.values():
            # Revisão do David (09/09/2026): Class_1 vira o tipo de corredor
            # (era Class_5), Class_2 vira o nome do corredor (era Class_3), e
            # Class_5 em si vira "NA".
            out.append(row(GRUPO, NOME, c1=tipo, c2=terr,
                           c3="NA", c4="NA", c5="NA",  # classes reorganizadas a pedido da equipe (11/09/2026)
                           unit=UNIDADE, territory=terr, year=year,
                           value=round(reg[k].get(year, 0.0), 5)))
    return out
