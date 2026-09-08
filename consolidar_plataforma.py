#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Consolida os CSVs de plataforma/ em dois arquivos CSV.

    2plat_macro_outputs.csv      todas as variáveis prontas, EXCETO 18 e 19
                                  (Emissions and removals), numa tabela só,
                                  alinhadas pelo cabeçalho de 11 colunas.
    2plat_macro_emissions.csv    18 e 19 juntas (mesmas 11 colunas, mesmo
                                  nome de coluna — as duas já usam
                                  "Emissions_or_removals" na origem), MENOS as
                                  linhas do bloco exógeno de indústria (ver
                                  EXCLUIR_DA_EMISSOES abaixo) — pedido do
                                  usuário em 02/09/2026, essas emissões não
                                  devem ir para a planilha da plataforma.

Uso:
    python consolidar_plataforma.py --plataforma plataforma

FORMATO DO CSV (pedido do usuário, 02/09/2026): UTF-8, separador decimal "."
e separador de coluna ",". É o default do pandas (to_csv sem sep/decimal
explícitos já grava assim); os parâmetros abaixo estão explícitos só para
deixar registrado que a escolha foi deliberada, não incidental.

NOTA SOBRE O CABEÇALHO: a coluna 2 muda de nome por variável — "Emissions_or_
removals" nas ids 18 e 19, "Variable name" nas outras 15 (ver comum.COLS, que
usa "COL2" como marcador de posição para isso). Como agora 18 e 19 vão juntas
para o arquivo de emissões e todas as outras variáveis já usam "Variable name"
na origem, cada arquivo consolidado tem UM nome de coluna nativo — não precisa
mais renomear nada para alinhar.

INDÚSTRIA FORA DA PLANILHA DE EMISSÕES: a id 18 inclui um bloco exógeno (tudo
que o MACRO não modela — hoje só a aresta "Industry_to_Sink", constante em
todos os períodos) marcado com Class_4 = "Exogenous emissions (not modelled in
MACRO)". Esse bloco continua no CSV da própria variável (18_emissions_and_
removals.csv) e no outputs_MACRO.xlsx — a exclusão vale só para a planilha
2plat_macro_emissions, que é o que o usuário pediu.
"""
import argparse
import re
from pathlib import Path

import pandas as pd

EMISSOES_IDS = {18, 19}
CLASS4_EXCLUIR_EMISSOES = "Exogenous emissions (not modelled in MACRO)"


def _achar_csvs(pasta: Path) -> dict[int, Path]:
    """{id: caminho} para todo arquivo <id>_<nome>.csv em pasta."""
    out = {}
    for p in sorted(pasta.glob("*.csv")):
        m = re.match(r"^(\d+)_", p.name)
        if m:
            out[int(m.group(1))] = p
    return out


def _ler(caminho: Path) -> pd.DataFrame:
    """Lê um CSV de plataforma/ sem deixar o pandas confundir os marcadores de
    texto 'NA' e 'N/A' (ver LEIA-PRIMEIRO.txt) com valor ausente."""
    df = pd.read_csv(caminho, keep_default_na=False, na_values=[])
    if len(df.columns) != 11:
        raise ValueError(f"{caminho.name}: esperava 11 colunas, achei {len(df.columns)}")
    return df


def _gravar(df: pd.DataFrame, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False, sep=",", decimal=".", encoding="utf-8")
    print(f"    {destino}  ({len(df):,} linhas)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plataforma", default=Path("plataforma"), type=Path,
                     help="pasta com os CSVs <id>_<nome>.csv (default: ./plataforma)")
    a = ap.parse_args()

    csvs = _achar_csvs(a.plataforma)
    for vid in EMISSOES_IDS:
        if vid not in csvs:
            print(f"aviso: não achei o CSV da variável {vid} em {a.plataforma}")

    # --- 2plat_macro_outputs.csv: tudo, exceto 18 e 19 ----------------------
    partes = [_ler(caminho) for vid, caminho in sorted(csvs.items())
              if vid not in EMISSOES_IDS]
    if not partes:
        raise SystemExit(f"nenhum CSV de variável fora de {EMISSOES_IDS} "
                          f"encontrado em {a.plataforma}")
    todos = pd.concat(partes, ignore_index=True)
    _gravar(todos, a.plataforma / "2plat_macro_outputs.csv")

    # --- 2plat_macro_emissions.csv: 18 + 19, sem o bloco de indústria -------
    partes_emissoes = [_ler(csvs[vid]) for vid in sorted(EMISSOES_IDS) if vid in csvs]
    if partes_emissoes:
        emissoes = pd.concat(partes_emissoes, ignore_index=True)
        antes = len(emissoes)
        emissoes = emissoes[emissoes["Class_4"] != CLASS4_EXCLUIR_EMISSOES]
        removidas = antes - len(emissoes)
        if removidas:
            print(f"    (removidas {removidas} linhas de indústria — "
                  f"Class_4 = '{CLASS4_EXCLUIR_EMISSOES}')")
        _gravar(emissoes, a.plataforma / "2plat_macro_emissions.csv")


if __name__ == "__main__":
    main()
