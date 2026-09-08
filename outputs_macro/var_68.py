"""id 68 — Power generation by type.

Fonte: flows_annual/flows_annual_results_period_<p>.csv

Geração = fluxo POSITIVO de Electricity entrando num nó elétrico (node_out
começa com 'elec_'), de ativo que não seja linha de transmissão.

Esse filtro resolve sozinho os três casos que a Tab8 trata à mão:
 - HydroRes tem discharge_edge (geração), inflow_edge (negativo, é água) e
   spill_edge (positivo, 21,6 TWh em 2050, mas vai para hydro_source_*, é
   vertimento). Só o discharge tem nó elétrico de destino.
 - transmissão move energia já gerada; contá-la duplicaria 795 TWh em 2050.
 - consumo (eletrólise, DAC, carga de bateria) é negativo e cai fora.

Bateria entra como 'Discharge' seguindo a Tab8 ("including batteries"), mas é
devolução de estoque: a carga consumiu 22,3 TWh para devolver 19,7 em 2050.
Somar essa linha num total de geração conta a mesma energia duas vezes.
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import uf_de_no, bacia_de_id, PERIODS, fluxos, row
from ._eletrico import C2, C3, EXCLUIR_TRANSMISSAO, classificar

NOTA  = NOTAS[68]
RESUMO  = RESUMOS[68]

ID    = 68
NOME  = "Power generation by type"
COL2  = "Variable name"
GRUPO = "Power"
CLASS_ESPACIAL = 3   # bacia migra para Class_3; ver comum.padronizar_territorio
UNIDADE = "GWh"
FATOR   = 1e-3          # o modelo grava MWh
SUPORTA_UF = True


def gerar(root: Path, por_uf: bool = False, **kw):
    reg = {}
    for p, year in PERIODS.items():
        d = fluxos(root, p)
        d = d[(d.commodity == "Electricity") & (d.value > 0)
              & d.node_out.astype(str).str.startswith("elec_")
              & ~d.resource_type.isin(EXCLUIR_TRANSMISSAO)]
        for r in d.itertuples():
            c4, c5 = classificar(r.resource_type, r.resource_id,
                                 battery_label="Discharge")
            # Usina de BACIA sai uma vez só, no passe nacional (correção
            # incorporada de outra rodada, 02/09/2026).
            b = bacia_de_id(r.resource_id)
            if b:
                if por_uf:
                    continue
                terr = b
            else:
                terr = uf_de_no(r.node_out) if por_uf else "BR"
            k = (c4, c5, terr)
            reg.setdefault(k, {}).setdefault(year, 0.0)
            reg[k][year] += float(r.value)

    out = []
    for c4, c5, terr in sorted(reg):
        for year in PERIODS.values():
            out.append(row(GRUPO, NOME, c1="Energy", c2=C2, c3=C3, c4=c4, c5=c5,
                           unit=UNIDADE, territory=terr, year=year,
                           value=round(reg[(c4, c5, terr)].get(year, 0.0) * FATOR, 5)))
    return out
