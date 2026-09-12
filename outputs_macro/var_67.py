"""id 67 — Solar, wind and battery capacity additions.

Mesmo arquivo da 66, com variable == 'new_capacity' e só os três tipos que a
variável nomeia.

ADIÇÃO BRUTA: new_capacity não desconta retired_capacity. No horizonte só pesa
em 2050 (eólica onshore aposenta 1,72 GW, exatamente o que foi construído em
2025) e em 2035 (bateria, 0,26 GW).

MEDIA_ANUAL=False -> adição do quinquênio (nenhuma conta feita), unidade GW.
MEDIA_ANUAL=True  -> divide por PERIOD_LENGTH, unidade GW/year. A variável se
chama "average annual" na planilha da plataforma, mas dividir contradiz a
resolução temporal declarada de 5 anos — decisão pendente com a equipe.
"""
from pathlib import Path
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import uf_de_zona, PERIODS, PERIOD_LENGTH, capacidade, row
from ._eletrico import C2, C3, classificar

NOTA  = NOTAS[67]
RESUMO  = RESUMOS[67]

ID    = 67
NOME  = "Solar, wind and battery average annual capacity additions"
COL2  = "Variable name"
GRUPO = "Energy supply and use"    # era "Power" (pedido da equipe, 11/09/2026)
FATOR = 1e-3
SUPORTA_UF = True

MEDIA_ANUAL = False
TIPOS = ["VRE{Generic}", "Battery"]


def gerar(root: Path, por_uf: bool = False, **kw):
    reg = {}
    for p, year in PERIODS.items():
        d = capacidade(root, p)
        d = d[(d.variable == "new_capacity") & (d.commodity == "Electricity")
              & d.resource_type.isin(TIPOS)
              & (d.component_type != "Storage{Electricity}")]
        for r in d.itertuples():
            c4, c5 = classificar(r.resource_type, r.resource_id)
            terr = uf_de_zona(r.zone) if por_uf else "BR"
            k = (c4, c5, terr)
            reg.setdefault(k, {}).setdefault(year, 0.0)
            reg[k][year] += float(r.value)

    div = PERIOD_LENGTH if MEDIA_ANUAL else 1
    unidade = "GW/year" if MEDIA_ANUAL else "GW"
    out = []
    for c4, c5, terr in sorted(reg):
        for year in PERIODS.values():
            out.append(row(GRUPO, NOME, c1=c4, c2=c5, c3=C3, c4="NA", c5="NA",  # classes reorganizadas a pedido da equipe (11/09/2026)
                           unit=unidade, territory=terr, year=year,
                           value=round(reg[(c4, c5, terr)].get(year, 0.0) * FATOR / div, 5)))
    return out
