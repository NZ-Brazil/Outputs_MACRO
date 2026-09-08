#!/usr/bin/env python3
"""Gera os CSVs da plataforma a partir dos resultados do MACRO.

    python montar.py --root . --out plataforma
    python montar.py --root . --out plataforma --vars 18 19
    python montar.py --root . --out plataforma --xlsx     # tudo num workbook
"""
import argparse
from pathlib import Path
import outputs_macro as om
from outputs_macro.comum import escrever, padronizar_territorio, COLS

# id 71 (Oil production): além do CSV normal em plataforma/, uma tabela de
# detalhe do cenário C (petróleo bruto + diesel/gasolina/jet fuel, mil tep e
# Mb/d) vai para results_001/flow_analysis/oil_production_scenarios.csv do
# projeto MacroEnergy.jl vivo — só faz sentido na convenção viva, onde --root
# é a pasta do projeto e essa pasta existe. Nome do arquivo e formato (csv, não
# mais xlsx) alterados a pedido do usuário em 02/09/2026; a tabela só é
# criada/atualizada quando o cenário C está escolhido — ver
# outputs_macro/var_71.py:tabela_flow_analysis().
NOME_CSV_FLOW_ANALYSIS_71 = "oil_production_scenarios.csv"


def juntar_notas(notas):
    """Um bloco por texto distinto, separado por uma régua. Notas compartilhadas
    por mais de uma variável (18 e 19) aparecem uma vez só."""
    vistos, blocos = {}, []
    for vid, texto in notas:
        t = texto.strip()
        if t in vistos:
            continue
        vistos[t] = vid
        blocos.append("-" * 72 + "\n" + t)
    return blocos


def slug(m):
    s = m.NOME.lower().replace(" ", "_").replace(",", "").replace("/", "-")
    return f"{m.ID}_{s[:58]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path,
                    help="pasta com results_period_*, flows_annual/ e os inputs")
    ap.add_argument("--out", default=Path("plataforma"), type=Path)
    ap.add_argument("--vars", nargs="*", type=int, default=sorted(om.VARS))
    ap.add_argument("--so-nacional", action="store_true",
                    help="omite as linhas por UF (por padrão saem junto das nacionais)")
    ap.add_argument("--xlsx", action="store_true",
                    help="também grava um workbook único com aba de Notas")
    a = ap.parse_args()

    produzidos, notas = [], [(-3, om.NOTAS_GERAIS[-3].strip()),
                             (-2, om.NOTAS_GERAIS[-2].strip())]
    for vid in a.vars:
        if vid not in om.VARS:
            print(f"[{vid}] pendente: {om.PENDENTES.get(vid, 'não implementada')}")
            continue
        m = om.VARS[vid]
        rows = m.gerar(a.root)
        if getattr(m, "SUPORTA_UF", False) and not a.so_nacional:
            rows += m.gerar(a.root, por_uf=True)
        # Territory só aceita BR ou UF. O recorte espacial que não é UF migra
        # para a Class declarada pelo módulo, ou sai. Ver comum.py.
        rows, fora = padronizar_territorio(rows, getattr(m, "CLASS_ESPACIAL", None))
        if fora:
            print(f"[{vid}] {fora} linhas com Territory fora de BR/UF descartadas")
        if not rows:
            # a id 71 não emite nada fora do cenário C do card 32
            print(f"[{vid}] sem linhas neste cenário — arquivo não gerado")
            continue
        destino = a.out / f"{slug(m)}.csv"
        escrever(rows, m.COL2, destino)
        produzidos.append((m, rows, destino))
        if vid == 71:
            fa = a.root / "results_001" / "flow_analysis"
            if fa.is_dir():
                tabela = m.tabela_flow_analysis(a.root)
                destino_fa = fa / NOME_CSV_FLOW_ANALYSIS_71
                if tabela is not None:
                    tabela.to_csv(destino_fa, index=False, sep=",", decimal=".",
                                  encoding="utf-8")
                    print(f"      cópia -> {destino_fa}")
                else:
                    print(f"      aviso: cenário C não escolhido — "
                          f"{destino_fa.name} não foi criado/atualizado")
            else:
                print(f"      aviso: {fa} não existe — {vid} não tem cópia em "
                      f"flow_analysis (só roda na convenção do projeto MacroEnergy.jl vivo)")
        if getattr(m, "NOTA", None):
            notas.append((vid, m.NOTA.strip()))
        if getattr(m, "SUPORTA_UF", False):
            notas.append((0, om.NOTAS_GERAIS[0].strip()))
        if vid in (19, 55, 65):
            notas.append((-1, om.NOTAS_GERAIS[-1].strip()))
        print(f"[{vid}] {len(rows):5} linhas -> {destino}")

    # --- descrições curtas: uma linha por variável, para o card --------------
    if produzidos:
        import csv as _csv
        p = a.out / "descricoes.csv"
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = _csv.writer(f)
            w.writerow(["id", "Variable_group", "Variable name", "Unit", "Descricao"])
            for m, rows, _ in produzidos:
                un = sorted({r["Unit"] for r in rows})
                grupo = rows[0]["Variable_group"] if rows else ""
                w.writerow([m.ID, grupo, m.NOME, " / ".join(un),
                            getattr(m, "RESUMO", "")])
        print(f"      descrições -> {p}")

    # --- notas: viajam junto com a saída ------------------------------------
    blocos = juntar_notas(notas)
    if blocos:
        p = a.out / "LEIA-ME.txt"
        p.write_text("NOTAS DE LEITURA — outputs do MACRO para a plataforma\n"
                     + "=" * 72 + "\n\n" + "\n\n".join(blocos)
                     + "\n\n" + "=" * 72 + "\n"
                     + "Editar em outputs_macro/_notas.py, não aqui: este arquivo é regerado.\n",
                     encoding="utf-8")
        print(f"      notas -> {p}")

    # --- workbook opcional --------------------------------------------------
    if a.xlsx and produzidos:
        import pandas as pd
        dest = a.out / "outputs_MACRO.xlsx"
        with pd.ExcelWriter(dest, engine="openpyxl") as xl:
            desc = pd.DataFrame(
                [{"id": m.ID,
                  "Variable_group": (rows[0]["Variable_group"] if rows else ""),
                  "Variable name": m.NOME,
                  "Unit": " / ".join(sorted({r["Unit"] for r in rows})),
                  "Descricao": getattr(m, "RESUMO", "")}
                 for m, rows, _ in produzidos])
            desc.to_excel(xl, sheet_name="Descrições", index=False)
            texto = "\n\n".join(juntar_notas(notas)) or "sem notas"
            pd.DataFrame({"Notas de leitura": texto.split("\n")}) \
              .to_excel(xl, sheet_name="Notas", index=False)
            for m, rows, _ in produzidos:
                cols = [c if c != "COL2" else m.COL2 for c in COLS]
                df = pd.DataFrame([[r[c] for c in COLS] for r in rows], columns=cols)
                df.to_excel(xl, sheet_name=f"{m.ID}", index=False)
        print(f"      workbook -> {dest}")


if __name__ == "__main__":
    main()
