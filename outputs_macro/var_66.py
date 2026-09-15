"""id 66 — Installed capacity by type.

Fonte: results_period_<p>/results_period_<p>/capacity.csv
Filtro: variable == 'capacity' e commodity == 'Electricity'.

'capacity' é ESTOQUE, não adição: conferido nos seis períodos que
capacity(t) = capacity(t-1) + new_capacity - retired_capacity, sem resíduo.
(existing_capacity só é gravado no período 1.)

Três armadilhas do arquivo:
 1. HydroRes aparece DUAS vezes com valor idêntico (discharge_edge e
    inflow_edge). Somar as duas dobra a hidrelétrica de reservatório.
 2. component_type 'Storage{Electricity}' é ENERGIA (GWh), não potência —
    bateria 39,7 GWh e reservatório 145.330 GWh. É outra variável.
 3. Linhas de transmissão têm capacidade em MW mas não são geração.

LACUNA CONHECIDA: a bioeletricidade não aparece aqui. No capacity.csv o
BECCSElectricity tem capacidade na biomass_edge, isto é, MW de biomassa de
ENTRADA, não MW elétricos — e o BECCSEthanolv2 coproduz eletricidade sem
capacidade associada. Na 68 essas duas rotas geram 172 e 35 TWh em 2050.
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import uf_de_zona, eh_bacia, PERIODS, capacidade, row
from ._eletrico import C2, C3, EXCLUIR_TRANSMISSAO, classificar

NOTA  = NOTAS[66]
RESUMO  = RESUMOS[66]

ID    = 66
NOME  = "Power installed capacity"    # era "Installed capacity by type" (revisão do David, 09/09/2026)
COL2  = "Variable name"
GRUPO = "Energy supply and use"    # era "Power" (pedido da equipe, 11/09/2026)
# Bacia na CLASS_4, preservando o rótulo fixo "Electricity generation (public
# service)" na Class_3. Formato pedido pela equipe em 15/09/2026:
#
#     Hydropower / Reservoir ou Run-of-river / Electricity generation
#     (public service) / <bacia> / NA
#
# HISTÓRICO, porque isto já foi e voltou: em 11/09 eu movi a bacia para a
# Class_4 justamente para não apagar o rótulo fixo; em 12/09 a equipe pediu de
# volta para a Class_3, o que apagava o rótulo só nas linhas de hidrelétrica; em
# 15/09 a equipe descreveu o formato acima, que é o de 11/09. Se alguém quiser a
# bacia na Class_3 de novo, o único lugar a mexer é esta constante — e o rótulo
# volta a ser sobrescrito.
#
# Com isto a 66 volta a concordar com a id 68 (Power generation by type), que
# trata as MESMAS hidrelétricas e nunca saiu da Class_4.
CLASS_ESPACIAL = 4
UNIDADE = "GW"
FATOR   = 1e-3          # o modelo grava MW
SUPORTA_UF = True


def gerar(root: Path, por_uf: bool = False, **kw):
    reg = {}
    for p, year in PERIODS.items():
        d = capacidade(root, p)
        d = d[(d.variable == "capacity") & (d.commodity == "Electricity")
              & ~d.resource_type.isin(EXCLUIR_TRANSMISSAO)
              & (d.component_type != "Storage{Electricity}")]        # armadilha 2
        for r in d.itertuples():
            if r.resource_type == "HydroRes" and r.edge != "discharge_edge":
                continue                                             # armadilha 1
            c4, c5 = classificar(r.resource_type, r.resource_id)
            z = uf_de_zona(r.zone)
            # Usina de BACIA sai uma vez só, no passe nacional (correção
            # incorporada de outra rodada, 02/09/2026): a bacia vira Class_3 e
            # o Territory vira BR na padronização, então uma linha nacional
            # junto dobraria a soma.
            if eh_bacia(z):
                if por_uf:
                    continue
                terr = z
            else:
                terr = z if por_uf else "BR"
            k = (c4, c5, terr)
            reg.setdefault(k, {}).setdefault(year, 0.0)
            reg[k][year] += float(r.value)

    out = []
    for c4, c5, terr in sorted(reg):
        for year in PERIODS.values():
            # Revisão do David (09/09/2026): Class_1 vira a tecnologia (era
            # Class_4), Class_2 vira o detalhe (era Class_5), e Class_5 em si
            # vira "NA". Class_4 continua igual (fica repetido com Class_1).
            out.append(row(GRUPO, NOME, c1=c4, c2=c5, c3=C3, c4="NA", c5="NA",  # classes reorganizadas a pedido da equipe (11/09/2026)
                           unit=UNIDADE, territory=terr, year=year,
                           value=round(reg[(c4, c5, terr)].get(year, 0.0) * FATOR, 5)))
    return out
