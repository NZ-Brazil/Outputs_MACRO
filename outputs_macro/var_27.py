# -*- coding: utf-8 -*-
"""id 27 — Demand side energy capital.

Fonte: results_period_<p>/results_period_<p>/costs_by_type.csv

Receita definida pela equipe: o custo de SUPRIMENTO dos quatro nós de
combustível fóssil de uso final —

    Node{NaturalGas}                 gás natural
    Node{MacroEnergy.Gasoline}       gasolina
    Node{MacroEnergy.JetFuel_Fossil} querosene de aviação fóssil
    Node{MacroEnergy.Diesel}         diesel

O que entra é a categoria 'Supply' desses nós, o valor que o modelo paga para
trazer o combustível ao sistema. A categoria 'NonServedDemand' dos mesmos nós
existe mas é desprezível (3,23 M US$ em 2025 e entre 0,13 e 1,19 nos demais
períodos — não zera) e fica de fora, porque é penalidade de não atendimento e
não custo de combustível.

VALOR DESCONTADO, como o da id 24: é o presente do quinquênio no ano-base, a
4,5% ao ano. Não anualizado.

RELAÇÃO COM A id 24: a 24 subtrai do total justamente os Supply de gasolina,
diesel e querosene fóssil — os mesmos três desta variável. O gás natural NÃO é
subtraído lá, então a 24 e a 27 não são complementares: o Supply de gás
natural aparece nas duas. NUNCA SOMAR AS DUAS.

O NOME DA VARIÁVEL NÃO DESCREVE O QUE ESTÁ AQUI. 'Demand side energy capital'
é, na planilha da plataforma, o estoque de capital de uso final — veículos,
motores, equipamentos —, e a fonte prevista para isso é o Energy Pathways, não
o MACRO. O que esta receita entrega é DESPESA COM COMBUSTÍVEL FÓSSIL, um fluxo
operacional anual, não um estoque de capital.

ENTREGA POR PORTADOR, DE PROPÓSITO. Este arquivo é insumo para a equipe de uso
final, que faz a distribuição por setor e a passagem para capital de uso final.
A abertura em diesel, gasolina, querosene e gás natural é a chave que ela usa;
o MACRO não separa transportes de indústria por conta própria.
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, custos_por_tipo, row

NOTA   = NOTAS[27]
RESUMO = RESUMOS[27]

ID    = 27
NOME  = "Demand side energy capital"
COL2  = "Variable name"
GRUPO = "Energy supply and use"    # era "Economy" (revisão do David, 09/09/2026)
UNIDADE = "US$"

# type do costs_by_type -> Class_4 (portador), na mesma nomenclatura da id 56
NOS = [
    ("Node{MacroEnergy.Diesel}",         "Diesel"),
    ("Node{MacroEnergy.Gasoline}",       "Gasoline"),
    ("Node{MacroEnergy.JetFuel_Fossil}", "Jet fuel"),
    ("Node{NaturalGas}",                 "Natural gas"),
]

CATEGORIA = "Supply"

TOTAL = "Total"


def gerar(root: Path, **kw):
    reg = {}
    for p, year in PERIODS.items():
        g = custos_por_tipo(root, p)
        soma = 0.0
        for tipo, c4 in NOS:
            v = g.get((tipo, CATEGORIA), 0.0)
            reg.setdefault(c4, {})[year] = v
            soma += v
        reg.setdefault(TOTAL, {})[year] = soma

    out = []
    for c4 in [TOTAL] + [c for _, c in NOS]:
        for year in PERIODS.values():
            # Class_1, Class_2 e Class_3 repetem o nome da variável
            # (pedido da equipe, 12/09/2026 — antes eram "Energy", "NA" e o
            # nome). Class_4 continua com o combustível.
            out.append(row(GRUPO, NOME, c1=NOME, c2=NOME, c3=NOME,
                           c4=c4, c5="NA",
                           unit=UNIDADE, territory="BR", year=year,
                           value=round(reg[c4].get(year, 0.0), 5)))
    return out
