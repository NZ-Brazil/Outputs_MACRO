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
# Bacia na Class_3, sobrescrevendo o rótulo fixo "Electricity generation
# (public service)" só nas linhas de hidrelétrica; Class_4 e Class_5 ficam
# "NA". Pedido explícito da equipe em 12/09/2026, depois de olhar a saída: em
# 11/09 eu tinha movido para Class_4 justamente para preservar o rótulo, mas a
# equipe prefere a bacia na Class_3. ATENÇÃO: a id 68 (Power generation by
# type) trata as MESMAS hidrelétricas e continua com a bacia na Class_4 — a
# equipe conferiu e manteve. Ver comum.padronizar_territorio.
CLASS_ESPACIAL = 3
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
