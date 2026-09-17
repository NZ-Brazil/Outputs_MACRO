"""id 18 — Emissions and removals : EMISSÕES.

Fonte: flows_annual/flows_annual_results_period_<p>.csv, commodity CO2.
Emissão = fluxo POSITIVO (entrando em co2_emitted_BR).

MUDANÇA DE CONVENÇÃO (16/09/2026): a combustão de biomassa SAI desta variável.
Antes, a id 18 seguia a convenção MACRO de ciclo cheio (ver _emissoes.py) e
incluía tanto a emissão direta dos ativos de biomassa quanto a queima
downstream dos combustíveis renováveis — o que exigia ler a id 18 sempre junto
da id 19 (remoção) para não superestimar o líquido. Times de fora do NZB que
liam só a id 18 (ex.: Tasso, David, Felipe, Sergio) interpretavam isso como
dupla contagem.

Agora a id 18 já sai filtrada: qualquer linha cuja Classe 4 esteja em
E.BIOGENICO_CLASS4 é descartada — mesmo conjunto que _emissoes.py usa para
marcar biogênico, então cobre automaticamente qualquer ativo BECCS/biomassa
novo que entrar em CONVERSAO, sem precisar manter uma lista solta aqui.
Fica de fora tanto a emissão direta no ativo de conversão (ex.: Bioelectricity)
quanto a queima do combustível já pronto no uso final (ex.: Ethanol,
Renewable diesel, Sustainable aviation fuel), incluindo Hydrogen e Synthetic
methane, que também são biogênicos e ficavam de fora de uma primeira versão
manual deste filtro.

O bloco exógeno (Class_4 = "Exogenous emissions...") e toda emissão fóssil
continuam entrando normalmente — só a combustão de origem biomássica sai.

A id 19 (remoção) e a id 73 (CO2 armazenado) não foram alteradas por esta
mudança; ver a nota de leitura da id 18/19 para a discussão de por que não se
soma id 19 com id 73.
"""
from pathlib import Path
from .comum import PERIODS, fluxos, row
from . import _emissoes as E
from ._notas import NOTAS
from ._resumos import RESUMOS

ID    = 18
NOME  = E.NOME
COL2  = E.COL2
VALOR_COL2 = "Emissions"

NOTA = NOTAS[18]
RESUMO = RESUMOS[18]


def gerar(root: Path, **kw):
    reg = {}
    for p, year in PERIODS.items():
        d = fluxos(root, p)
        origem = E.origens_combustivel(d)
        co2 = d[(d.commodity == "CO2") & (d.value > 0)]
        for r in co2.itertuples():
            k = E.classificar(r.resource_type, r.resource_id,
                              origem.get(r.resource_id))
            if k[3] in E.BIOGENICO_CLASS4:
                continue  # combustão de biomassa: sai da id 18 (16/09/2026)
            reg.setdefault(k, {}).setdefault(year, 0.0)
            reg[k][year] += float(r.value)

    out = []
    for k in sorted(reg):
        c1, c2, c3, c4, c5 = k
        for year in PERIODS.values():
            out.append(row(E.GRUPO, VALOR_COL2, c1=c1, c2=c2, c3=c3, c4=c4, c5=c5,
                           unit=E.UNIDADE, territory="BR", year=year,
                           value=round(reg[k].get(year, 0.0) * E.FATOR, 5)))
    return out
