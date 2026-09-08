#!/usr/bin/env python3
"""Roda o pipeline inteiro, do zero: primeiro o run_full_pipeline.py (do projeto
MacroEnergy.jl), depois o montar.py (outputs_macro) sobre os mesmos resultados.

    python run_pipeline_completo.py --model-root "C:\\Users\\rache\\NZ-Brazil-MacroEnergy_default\\Default_scenario"

O run_full_pipeline.py mora dentro do projeto do modelo (--model-root) e é quem
gera as tabelas intermediárias — agregação de flows.csv.gz em annual_flows
(results_001/annual_aggregation/) e as 20 planilhas de tecnologia por commodity
(results_001/flow_analysis/). O outputs_macro roda em seguida, com --root
apontado para o MESMO --model-root: comum.py sabe achar o annual_flows e os
inputs (system/, assets/) dentro dele (ver a nota "duas convenções de pasta"
em outputs_macro/comum.py).

Opções:
    --skip-run-full-pipeline   pula a etapa 1 e só roda o montar.py (reaproveita
                                o annual_flows já existente em annual_aggregation/)
    --full-pipeline-args ...   argumentos extras passados ao run_full_pipeline.py
                                (ex.: --skip-aggregation, --only Diesel Coal)
    --montar-args ...          argumentos extras passados ao montar.py
                                (ex.: --xlsx, --vars 65 66, --so-nacional)

Cada argumento de lista (--full-pipeline-args / --montar-args) consome o resto
da linha de comando, então venha por último ou separe com "--":

    python run_pipeline_completo.py --model-root <pasta> \\
        --full-pipeline-args --skip-aggregation \\
        --montar-args --xlsx
"""
import argparse
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NOME_RUN_FULL_PIPELINE = "run_full_pipeline.py"   # procurado dentro de --model-root
MONTAR = AQUI / "montar.py"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model-root", required=True, type=Path,
                     help="pasta do projeto MacroEnergy.jl (onde estão "
                          "run_full_pipeline.py, results_001/, system/, assets/)")
    ap.add_argument("--out", default=AQUI / "plataforma", type=Path,
                     help="pasta de saída do montar.py (default: ./plataforma)")
    ap.add_argument("--skip-run-full-pipeline", action="store_true",
                     help="pula o run_full_pipeline.py e só roda o montar.py")
    ap.add_argument("--full-pipeline-args", nargs=argparse.REMAINDER, default=[],
                     help="resto da linha vira argumentos do run_full_pipeline.py")
    ap.add_argument("--montar-args", nargs=argparse.REMAINDER, default=[],
                     help="resto da linha vira argumentos do montar.py")
    a = ap.parse_args()

    if not MONTAR.exists():
        sys.exit(f"não encontrei montar.py ao lado deste script: {MONTAR}")

    if a.skip_run_full_pipeline:
        print("=== 1/2: run_full_pipeline.py PULADO (--skip-run-full-pipeline) ===")
    else:
        script = a.model_root / NOME_RUN_FULL_PIPELINE
        if not script.exists():
            sys.exit(f"não encontrei {NOME_RUN_FULL_PIPELINE} em --model-root: {script}")
        print(f"=== 1/2: {script} ===")
        print("    (agregação de flows.csv.gz -> annual_flows, depois as 20 "
              "planilhas de tecnologia por commodity)")
        subprocess.run([sys.executable, str(script), *a.full_pipeline_args], check=True)

    print(f"\n=== 2/2: {MONTAR} --root {a.model_root} ===")
    subprocess.run([sys.executable, str(MONTAR), "--root", str(a.model_root),
                     "--out", str(a.out), *a.montar_args], check=True)

    print("\n=== Pipeline completo. ===")


if __name__ == "__main__":
    main()
