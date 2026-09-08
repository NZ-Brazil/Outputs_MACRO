"""Convenções do caso e utilidades compartilhadas por todas as variáveis."""
from pathlib import Path
import csv
import re
import pandas as pd

# --- do settings.json do caso ------------------------------------------------
START_YEAR    = 2025      # settings.json traz StartYear = null; fixado aqui
PERIOD_LENGTH = 5         # case_settings.PeriodLengths
N_PERIODS     = 6
DISCOUNT_RATE = 0.045     # case_settings.DiscountRate

PERIODS = {p: START_YEAR + PERIOD_LENGTH * (p - 1) for p in range(1, N_PERIODS + 1)}

# --- formato da plataforma ---------------------------------------------------
# COL2 é um marcador: o nome real da coluna 2 muda por variável
#   emissões (18, 19) -> "Emissions_or_removals"
#   demais            -> "Variable name"
COLS = ["Variable_group", "COL2", "Class_1", "Class_2", "Class_3", "Class_4",
        "Class_5", "Unit", "Territory", "Year", "Value"]

# --- duas convenções de pasta: o arquivo já entregue e a rodada viva -----------
#
# O outputs_macro nasceu apontado para um arquivo arquivado (results_001_original_run,
# extraído de um zip que duplicava o nome do projeto): ali --root já era a própria
# pasta de resultados, com results_period_N/results_period_N/ aninhado e os inputs em
# MacroEnergy.jl-NZB_S0/MacroEnergy.jl-NZB_S0/S0/. Desde 01/09/2026 o pipeline também
# roda direto sobre o projeto MacroEnergy.jl vivo (integrado ao run_full_pipeline.py):
# ali --root é a pasta do projeto (contém results_001/, system/, assets/),
# results_period_N não é duplicado, e o annual_flows fica em
# results_001/annual_aggregation/, não em flows_annual/.
#
# As funções abaixo tentam a forma viva primeiro e caem para a antiga se não
# acharem — não precisa dizer qual é qual na linha de comando.
RESULTS_RUN = "results_001"          # nome da subpasta da rodada, dentro de --root
_INPUTS_REL_ANTIGA = Path("MacroEnergy.jl-NZB_S0/MacroEnergy.jl-NZB_S0/S0")


def _pasta_resultados(root: Path) -> Path:
    """root pode já ser a pasta de resultados (arquivo antigo) ou a pasta do
    projeto, com a rodada numa subpasta RESULTS_RUN (projeto vivo)."""
    com_subpasta = root / RESULTS_RUN
    return com_subpasta if com_subpasta.is_dir() else root


def inputs_dir(root: Path) -> Path:
    """Onde estão system/ e assets/ (inputs do modelo: preços, dutos etc.).

    Na rodada viva ficam direto em root/; no arquivo antigo, aninhados em
    _INPUTS_REL_ANTIGA.
    """
    return root if (root / "system").is_dir() else root / _INPUTS_REL_ANTIGA


def row(group, col2, unit, territory, year, value,
        c1="NA", c2="NA", c3="NA", c4="NA", c5="NA"):
    """Uma linha do formato longo. 'NA' = não se aplica; 'N/A' = não existe no SEEG."""
    return dict(zip(COLS, [group, col2, c1, c2, c3, c4, c5, unit, territory, year, value]))


def period_dir(root: Path, p: int) -> Path:
    """Pasta de resultados do período p.

    O arquivo antigo grava a pasta do período aninhada nela mesma
    (results_period_p/results_period_p/); a rodada viva não duplica.
    """
    base = _pasta_resultados(root) / f"results_period_{p}"
    aninhada = base / f"results_period_{p}"
    return aninhada if aninhada.is_dir() else base


def custos_por_tipo(root: Path, p: int) -> dict:
    """costs_by_type.csv como {(type, category): value}.

    NUNCA endereçar esse arquivo por número de linha: o conjunto de tecnologias
    muda de período para período (96 linhas no período 1, 108 no 6).
    """
    df = pd.read_csv(period_dir(root, p) / "costs_by_type.csv")
    return {(r.type, r.category): float(r.value) for r in df.itertuples()}


def fluxos(root: Path, p: int) -> pd.DataFrame:
    """flows_annual do período, com uma coluna 'edge' (nome da aresta do ativo).

    Aceita annual_aggregation/ (nome do run_full_pipeline.py, rodada viva) e
    flows_annual/ (nome do arquivo antigo).
    """
    nome = f"flows_annual_results_period_{p}.csv"
    caminho = _pasta_resultados(root) / "annual_aggregation" / nome
    if not caminho.is_file():
        caminho = root / "flows_annual" / nome
    d = pd.read_csv(caminho)
    d["edge"] = [str(c).replace(str(r), "").lstrip("_")
                 for c, r in zip(d.component_id, d.resource_id)]
    return d


def capacidade(root: Path, p: int) -> pd.DataFrame:
    d = pd.read_csv(period_dir(root, p) / "capacity.csv")
    d["edge"] = [str(c).replace(str(r), "").lstrip("_")
                 for c, r in zip(d.component_id, d.resource_id)]
    return d


def capex_periodo(root: Path, p: int) -> float:
    """Soma da coluna value de capex.csv do período p — capex bruto do
    período (todas as commodities e tecnologias juntas, sem desconto e sem
    amortização). Não confundir com a categoria 'Investment' de
    costs_by_type.csv (usada nas ids 24 e 26), que é o custo de investimento
    como o modelo o computa no objetivo — descontado ao ano-base."""
    df = pd.read_csv(period_dir(root, p) / "capex.csv")
    return float(df["value"].sum())


# SEEG usa "Não Alocado" para o que não cai num estado; seguimos a mesma grafia.
NAO_ALOCADO = "Não Alocado"

# --- Territory: só BR ou UF (correção incorporada de outra rodada, 02/09/2026) --
# A aba '2plat standard csv files' define Territory como <BR or UF>, e a
# 2plat_all.xlsx tem exatamente 28 valores distintos (BR + 27 UFs). O MACRO
# produz recortes espaciais que NÃO são UF: bacia hidrográfica (ids 55, 66, 68),
# corredor de transmissão (id 70), bacia sedimentar (ids 73, 74) e 'Não
# Alocado' (id 65).
#
# REGRA: o recorte não-UF migra para a Class que o módulo declarar em
# CLASS_ESPACIAL e o Territory da linha vira BR. Módulo sem CLASS_ESPACIAL: a
# linha sai do entregável — a linha nacional já contém o valor dela.
UF_VALIDAS = frozenset(
    "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR "
    "SC SP SE TO".split())


def padronizar_territorio(rows, class_espacial=None):
    """Territory ∈ {BR, UF}. -> (linhas, nº de linhas descartadas)"""
    out, descartadas = [], 0
    for r in rows:
        t = str(r["Territory"])
        if t == "BR" or t in UF_VALIDAS:
            out.append(r)
            continue
        if class_espacial is None:
            descartadas += 1
            continue
        r = dict(r)
        r[f"Class_{class_espacial}"] = t
        r["Territory"] = "BR"
        out.append(r)
    return out, descartadas


def uf_de(resource_id) -> str:
    """UF a partir do resource_id (BR_SP_...). Ativos nacionais viram Não Alocado."""
    m = re.match(r"^BR_([A-Z]{2})_", str(resource_id))
    return m.group(1) if m else NAO_ALOCADO


# As hidrelétricas do modelo não têm UF: a zona delas é a BACIA HIDROGRÁFICA.
# Várias cruzam divisas estaduais, então a discretização espacial delas é por
# bacia mesmo, e não por estado. O rótulo é só o nome da bacia — Paraná e São
# Francisco também nomeiam bacias SEDIMENTARES nas ids 73 e 74, mas as duas
# famílias se distinguem pelo Variable_group e pela Class_2 (Electricity
# generation aqui, Carbon storage lá). Estados nunca colidem: são siglas de
# duas letras.
BACIA_HIDRO = {
    "Amazonas": "Amazonas", "Doce": "Doce", "Grande": "Grande",
    "Iguacu": "Iguaçu", "Jacui_capivari": "Jacuí-Capivari",
    "Jequitinhonha": "Jequitinhonha", "Paraiba_do_sul": "Paraíba do Sul",
    "Parana": "Paraná", "Paranaiba": "Paranaíba",
    "Paranapanema": "Paranapanema", "Parnaiba": "Parnaíba",
    "Sao_francisco": "São Francisco", "Tiete": "Tietê",
    "Tocantins": "Tocantins", "Uruguai": "Uruguai",
}


def eh_bacia(nome) -> bool:
    """True se o rótulo é uma bacia hidrográfica (já no nome de exibição)."""
    return str(nome) in set(BACIA_HIDRO.values())


def bacia(nome) -> str | None:
    """'Sao_francisco' -> 'São Francisco'. None se não for bacia."""
    n = BACIA_HIDRO.get(str(nome))
    return n


def bacia_de_id(resource_id) -> str | None:
    """'Sao_francisco_hydro_res_existing' -> 'São Francisco'."""
    m = re.match(r"^(.+?)_hydro_(res|ror)", str(resource_id))
    return bacia(m.group(1)) if m else None


def uf_de_zona(zone) -> str:
    """Território a partir da coluna zone do capacity.csv.

    'BR_SP' e 'BR_BR_SP' -> 'SP'. As térmicas genéricas de expansão vêm com a
    zona duplicada ('BR_BR_SP') e ficam todas em São Paulo — é assim no modelo,
    conferido pelo nó de destino da geração.
    Zona de bacia -> nome da bacia. Qualquer outra coisa -> Não Alocado.
    """
    z = str(zone)
    b = bacia(z)
    if b:
        return b
    m = re.search(r"_([A-Z]{2})$", z)
    return m.group(1) if m else NAO_ALOCADO


def uf_de_no(no) -> str:
    """UF a partir de um nó elétrico (elec_BR_SP)."""
    m = re.match(r"^elec_BR_([A-Z]{2})$", str(no))
    return m.group(1) if m else NAO_ALOCADO


def eh_no(n) -> bool:
    """Vertice é nó (e não transform/storage)."""
    n = str(n)
    return not (n.endswith("_transforms") or n.endswith("_storage"))


def saldo_nos(root: Path, p: int):
    """Saldo líquido de cada nó, em módulo de saída.

    saldo > 0  -> o nó é FONTE líquida (sai mais do que entra): oferta primária.
    saldo < 0  -> o nó é SUMIDOURO líquido: demanda final.

    É assim que se lê oferta e demanda neste modelo: não há linha de 'supply' no
    flows.csv, só arestas de ativos. O que um nó de recurso entrega ao sistema
    aparece como a soma das arestas que puxam dele.

    CUIDADO COM O SINAL: o arquivo mistura duas convenções.
      - Aresta de ativo (uma ponta é _transforms/_storage): value é a
        contribuição ao nó — positivo entra, negativo o ativo puxa.
      - Linha de transmissão (as duas pontas são nós): value é direcional, sai
        de node_in e entra em node_out; contribui -value na origem e +value no
        destino.
    Tratar as duas igual inverte o sinal de todo nó ligado por transmissão —
    natgas_fossil_BR, por exemplo, aparece como sumidouro em vez de fonte.
    """
    d = fluxos(root, p)
    ambos = d.node_in.map(eh_no) & d.node_out.map(eh_no)

    # Aresta de ativo (só uma ponta é nó): value já é a contribuição AO nó,
    # positiva quando entra, negativa quando o ativo puxa.
    a = d[~ambos]
    contrib = [
        a[a.node_out.map(eh_no)].groupby("node_out")["value"].sum(),
        a[a.node_in.map(eh_no)].groupby("node_in")["value"].sum(),
    ]
    # Linha de transmissão (as duas pontas são nós): value é DIRECIONAL, sai de
    # node_in e entra em node_out. Contribui -value na origem, +value no destino.
    t = d[ambos]
    contrib += [
        t.groupby("node_out")["value"].sum(),
        -t.groupby("node_in")["value"].sum(),
    ]

    total = None
    for c in contrib:
        total = c if total is None else total.add(c, fill_value=0)
    return -total.fillna(0)      # saída líquida = menos a contribuição líquida


def annuity_factor(p: int) -> float:
    """Soma dos fatores de desconto dos anos do período (convenção fim de ano).

    Fora de uso por decisão do projeto: os valores vão como o Macro grava, isto
    é, valor presente do quinquênio descontado ao ano-base. Conferido contra
    undiscounted_costs.csv com erro de 0,0000% nos seis períodos.
    """
    y0 = PERIOD_LENGTH * (p - 1)
    return sum((1 + DISCOUNT_RATE) ** -y for y in range(y0 + 1, y0 + PERIOD_LENGTH + 1))


def escrever(rows, col2_nome: str, destino: Path) -> None:
    header = [c if c != "COL2" else col2_nome for c in COLS]
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([r[c] for c in COLS])
