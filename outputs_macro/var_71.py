# -*- coding: utf-8 -*-
"""id 71 — Oil production.

Fonte: flows_annual/flows_annual_results_period_<p>.csv + rendimentos de refino
       exógenos (cenário C) + trajetórias exógenas dadas pela equipe
       (cenários A e B, acrescentados em 02/09/2026).

O card 32 da plataforma oferece três cenários de produção de petróleo:

    A  Expansion            pico de 5,7 Mb/d em 2030, platô até 2050
    B  Current policies     pico de 5,3 em 2030, declínio de 4,5%/ano
    C  Domestic market only produção segue a demanda interna          -> MACRO

Até 02/09/2026 só o C saía daqui (A e B eram exógenos, reportados pelo
EnergyPathways). A equipe pediu para os três saírem juntos desta variável a
partir de agora — A e B como trajetórias fixas, dadas por eles, sem qualquer
relação com o resultado do MACRO. A CONTA E O GATE DO CENÁRIO C NÃO MUDARAM em
nada (pedido explícito da equipe, 02/09/2026): o bloco abaixo é bit-a-bit o
mesmo de antes, inclusive o texto da ressalva. A e B são um bloco novo,
adicionado ao lado, sempre emitido — não dependem de scenario_config.csv.
As três linhas de um mesmo ano se distinguem pela Class_3: C continua "N/A"
(como sempre foi), A e B saem como "Scenario A" / "Scenario B".

------------------------------------------------------------------------------
CENÁRIO C — A ROTA É POR VOLUME, NÃO POR CO2 (decisão de 02/09/2026, mantida
sem alteração nesta atualização)

Uma versão anterior deste cálculo derivava a necessidade de petróleo do CO2 das
linhas de refino. Isso dava 0,17 Mb/d em 2050 — implausível para um país que
queima 60 bilhões de litros de diesel por ano — porque a combustão dos líquidos
fósseis não existe no modelo (mesmo bypass descrito na nota da id 18: as duas
rotas paralelas). O CO2 de refino é só ~13 Mt e não descreve o volume refinado.

Derivar do VOLUME de combustível resolve sem depender de rodada nova: os
volumes estão certos no modelo (596,1 TWh de diesel em 2050), quebrada está só
a contabilidade de emissões. A diferença entre as duas rotas é de 13,5x.

    petróleo necessário = max sobre os três derivados de
                          (volume do derivado em mil tep / rendimento de refino)

O máximo, e não a soma: a refinaria precisa processar cru suficiente para
atender o derivado mais exigente. O diesel puxa em todos os períodos.

Confirmado de novo em 02/09/2026: ao verificar se o CO2 das linhas de refino
(Technology="Refinery" em co2_co2captured_technology_flows.xlsx) daria uma
rota alternativa para A/B, o resultado bateu de novo com os mesmos ~0,12-0,18
Mb/d já documentados aqui como implausíveis (os fatores de emissão de
combustão fornecidos são ~10x maiores que a emissão real de processo de
refino do modelo) — reforça a decisão de manter a rota por volume.

------------------------------------------------------------------------------
CENÁRIOS A E B — trajetórias exógenas, acrescentadas em 02/09/2026

Dadas pela equipe, independentes do MACRO: não usam `fluxos()`, não dependem
de scenario_config.csv, e por isso saem sempre, em qualquer opção do card 32
(ao contrário do C, que continua condicionado a `cenario_32(root) == "c"`).

  Âncora de 2025: 3,770 Mb/d (produção real média informada pela equipe,
  02/09/2026), igual para A, B e C — em C o valor de 2025 já era uma âncora
  parecida (ANCORA_2025_MIL_TEP, ~3,7627 Mb/d); os dois números não são
  idênticos porque vêm de fontes/momentos diferentes, e a instrução da equipe
  para A e B foi explicitamente usar 3,770.

  Cenário A — pico de 5,7 Mb/d em 2030; platô sustentado até 2050 na faixa
  5,5-6,3 Mb/d. Sem valor por período dentro do platô, uso a média do
  intervalo (5,9 Mb/d) para 2035, 2040, 2045 e 2050 — confirmado com a
  equipe (resposta: "use a média").

  Cenário B — pico de 5,3 Mb/d em 2030; depleção natural reduz a produção
  para 4,4 Mb/d em 2034; dali em diante, declínio geométrico de 4,5%/ano:

      valor(ano) = 4,4 * 0,955 ** (ano - 2034),  ano >= 2035

  (2034 não é um dos nossos períodos; a fórmula só entra a partir de 2035).
  Confere com o ponto dado pela equipe para 2060 (fórmula dá ~1,33 Mb/d
  contra 1,3 Mb/d declarado — a diferença é arredondamento).

  CONVERSÃO Mb/d -> boe/ano: Mb/d * 1e6 barris/milhão * 365 dias/ano. Não há
  um "dias/ano" oficial documentado para esta variável; 365 é a convenção
  mais simples e explícita (ver DIAS_POR_ANO abaixo) — escolha nossa, não
  dado da equipe. Conferida contra a âncora de 2025 do cenário C: 195.157,876
  mil tep / 0,1421 / 365 / 1e6 dá exatamente 3,7627 Mb/d, o número que a nota
  da variável já citava — os dois cálculos, feitos em momentos diferentes,
  batem, o que reforça que 365 é a convenção implícita certa.

------------------------------------------------------------------------------
TABELA DE DETALHE DO CENÁRIO C EM flow_analysis (acrescentada em 02/09/2026)

Além da linha de petróleo bruto de cima, results_001/flow_analysis/ recebe
(só quando o cenário C está escolhido — ver `tabela_flow_analysis()`) um CSV,
oil_production_scenarios.csv, com uma linha por ano e 10 colunas: year,
scenario (sempre "C" — só existe para C), oil_production_Mbd,
oil_production_mil_tep, e o mesmo par (mil_tep, Mbd) para diesel, gasolina e
jet fuel. "Produção" de cada derivado aqui é a leitura do próprio volume do
nó de demanda (o mesmo volume usado no cálculo do petróleo bruto, mas ANTES
de dividir pelo rendimento de refino) — não o petróleo equivalente que
aquele derivado exigiria sozinho. Isso vale também para 2025: a âncora real
(ANCORA_2025_MIL_TEP) substitui só o TOTAL de petróleo bruto desse ano (por
causa da exportação, ver acima); o volume de cada derivado em 2025 continua
vindo do modelo, não da âncora, porque a demanda doméstica de derivados não
tem o mesmo problema de exportação que o total de petróleo bruto tem. Todas
as colunas _Mbd usam a mesma conversão (mil tep -> boe -> Mb/d, ver acima).
"""
from pathlib import Path
import csv as _csv
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, fluxos, row

NOTA   = NOTAS[71]
RESUMO = RESUMOS[71]

ID    = 71
NOME  = "Oil production"
COL2  = "Variable name"
GRUPO = "Fossil fuels industry"
UNIDADE = "boe"

# nó de onde sai cada derivado fóssil de uso final
NOS = {
    "Diesel":   "diesel_fossil_BR",
    "Gasoline": "gasoline_fossil_BR",
    "Jet fuel": "jetfuel_fossil_BR",
}

# fração de 1.000 tep de cru realizada como cada derivado na refinaria.
# Premissa da equipe, não sai do modelo.
RENDIMENTO = {"Diesel": 0.400, "Gasoline": 0.231, "Jet fuel": 0.048}

TEP_POR_MWH = 8.598e-5 * 1000.0     # 1 kWh = 8,598e-5 tep
TEP_POR_BOE = 0.1421

# ÂNCORA DE 2025 DO CENÁRIO C: produção real informada pela equipe, em mil
# tep. Em 2025 o Brasil ainda exporta, então a produção real está acima do
# que o mercado interno exige; o cenário C só passa a valer a partir de 2030.
# Manter a âncora faz a série começar no real e cair, que é o que o cenário
# descreve. NÃO ALTERADA nesta atualização.
ANCORA_2025_MIL_TEP = 195157.876419


def cenario_32(root: Path) -> str | None:
    """Opção do card 32 no scenario_config.csv do caso. None se não houver."""
    for nome in ("scenario_config.csv", "../scenario_config.csv"):
        p = root / nome
        if not p.exists():
            continue
        with open(p, newline="", encoding="utf-8-sig") as f:
            for r in _csv.DictReader(f):
                if str(r.get("variable_id", "")).strip() == "32":
                    return (r.get("option_id") or "").strip().lower() or None
    return None


# --- cenários A e B: trajetórias exógenas, iguais em qualquer rodada -------
ANCORA_2025_MBD = 3.770     # Mb/d — âncora real de 2025, dada pela equipe p/ A e B
DIAS_POR_ANO    = 365       # convenção explícita p/ converter Mb/d em boe/ano (ver docstring)

TRAJETORIA_A_MBD = {
    2025: ANCORA_2025_MBD,
    2030: 5.7,
    2035: 5.9, 2040: 5.9, 2045: 5.9, 2050: 5.9,   # platô = média de 5,5-6,3
}


def _trajetoria_b_mbd() -> dict:
    valores = {2025: ANCORA_2025_MBD, 2030: 5.3}
    for year in (2035, 2040, 2045, 2050):
        valores[year] = 4.4 * (0.955 ** (year - 2034))   # declínio de 4,5%/ano desde 2034=4,4
    return valores


TRAJETORIA_B_MBD = _trajetoria_b_mbd()


def _linhas_cenario(nome_cenario: str, mbd_por_ano: dict) -> list:
    return [row(GRUPO, NOME, c1="Energy", c2="Oil production",
                c3=nome_cenario, c4="Crude oil", c5="N/A",
                unit=UNIDADE, territory="BR", year=year,
                value=round(mbd_por_ano[year] * 1e6 * DIAS_POR_ANO, 5))
            for year in PERIODS.values()]


def _calcular_cenario_c(root: Path) -> dict:
    """{ano: {"oil_mil_tep": ..., "vol_mil_tep": {"Diesel":..., "Gasoline":...,
    "Jet fuel":...}}}. `vol_mil_tep` é o volume do PRÓPRIO derivado (mil tep),
    antes de dividir pelo rendimento — reaproveitado tanto pela linha de
    petróleo bruto (gerar()) quanto pela tabela de detalhe
    (tabela_flow_analysis()), para as duas contas usarem exatamente os mesmos
    números lidos do modelo."""
    out = {}
    for p, year in PERIODS.items():
        d = fluxos(root, p)
        vol_mil_tep = {
            rot: abs(d[(d.node_in == no) & (d.value < 0)].value.sum()) * TEP_POR_MWH / 1e3
            for rot, no in NOS.items()
        }
        if year == 2025:
            oil_mil_tep = ANCORA_2025_MIL_TEP
        else:
            oil_mil_tep = max(vol_mil_tep[rot] / RENDIMENTO[rot] for rot in NOS)
        out[year] = {"oil_mil_tep": oil_mil_tep, "vol_mil_tep": vol_mil_tep}
    return out


def _mbd(mil_tep: float) -> float:
    """mil tep -> Mb/d (mesma conversão mil tep -> boe -> Mb/d dos cenários A/B)."""
    return mil_tep * 1e3 / TEP_POR_BOE / DIAS_POR_ANO / 1e6


def gerar(root: Path, cenario: str | None = None, **kw):
    out = []

    # --- cenário C: cálculo e gate idênticos aos de antes de 02/09/2026 ----
    opcao = (cenario or cenario_32(root) or "").lower()
    if opcao == "c":
        calc = _calcular_cenario_c(root)
        for year, d in calc.items():
            out.append(row(GRUPO, NOME, c1="Energy", c2="Oil production",
                           c3="N/A", c4="Crude oil", c5="N/A",
                           unit=UNIDADE, territory="BR", year=year,
                           value=round(d["oil_mil_tep"] * 1e3 / TEP_POR_BOE, 5)))

    # --- cenários A e B: sempre emitidos, não dependem do card 32 ----------
    out += _linhas_cenario("Scenario A", TRAJETORIA_A_MBD)
    out += _linhas_cenario("Scenario B", TRAJETORIA_B_MBD)

    return out


def tabela_flow_analysis(root: Path, cenario: str | None = None):
    """Tabela de detalhe do cenário C p/ results_001/flow_analysis/
    oil_production_scenarios.csv. Devolve None (arquivo não é criado nem
    sobrescrito) quando o cenário escolhido não é 'c' — mesmo gate do bloco
    principal. Ver a nota da variável para o detalhe de cada coluna."""
    opcao = (cenario or cenario_32(root) or "").lower()
    if opcao != "c":
        return None

    import pandas as pd
    calc = _calcular_cenario_c(root)
    linhas = []
    for year, d in calc.items():
        v = d["vol_mil_tep"]
        linhas.append({
            "year": year,
            "scenario": "C",
            "oil_production_Mbd": round(_mbd(d["oil_mil_tep"]), 4),
            "oil_production_mil_tep": round(d["oil_mil_tep"], 6),
            "diesel_production_mil_tep": round(v["Diesel"], 6),
            "diesel_production_Mbd": round(_mbd(v["Diesel"]), 4),
            "gasoline_production_mil_tep": round(v["Gasoline"], 6),
            "gasoline_production_Mbd": round(_mbd(v["Gasoline"]), 4),
            "jetfuel_production_mil_tep": round(v["Jet fuel"], 6),
            "jetfuel_production_Mbd": round(_mbd(v["Jet fuel"]), 4),
        })
    return pd.DataFrame(linhas, columns=[
        "year", "scenario", "oil_production_Mbd", "oil_production_mil_tep",
        "diesel_production_mil_tep", "diesel_production_Mbd",
        "gasoline_production_mil_tep", "gasoline_production_Mbd",
        "jetfuel_production_mil_tep", "jetfuel_production_Mbd",
    ])
