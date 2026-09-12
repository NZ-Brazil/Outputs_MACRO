# -*- coding: utf-8 -*-
"""id 55 — Primary energy supply by source, agregada como o BEN agrega.

Fonte: flows_annual/flows_annual_results_period_<p>.csv

Não existe linha de 'supply' no flows.csv, só arestas de ativos. A oferta
primária vem do SALDO LÍQUIDO dos nós de recurso (ver comum.saldo_nos). Solar,
eólica e fio d'água não têm nó de recurso: a energia primária delas é a própria
geração.

CLASSES seguem a matriz energética do BEN, não o SEEG:
    Class_1 = Renewable / Non-renewable
    Class_2 = fonte do BEN (Crude oil, Natural gas, Mineral coal, Uranium,
              Hydraulic, Wind, Solar, Sugarcane biomass, Firewood and
              charcoal, Other renewables)
    Class_3 = detalhe do MACRO dentro da fonte
    Class_4, Class_5 = N/A

SOJA FICA DE FORA: no BEN o óleo de soja é fonte SECUNDÁRIA, não primária.

UNIDADES: as commodities de biomassa do modelo estão em toneladas, não em MWh,
e são convertidas por poder calorífico (CONVERTER_BIOMASSA = True). A variável
sai inteira em GWh — pôr CONVERTER_BIOMASSA = False devolve a biomassa em Mt e
a matriz deixa de fechar numa unidade só.
"""
from pathlib import Path
import re
from ._notas import NOTAS
from ._resumos import RESUMOS
from .comum import PERIODS, fluxos, saldo_nos, row, bacia, bacia_de_id
from ._eletrico import vre

NOTA   = NOTAS[55]
RESUMO = RESUMOS[55]

ID    = 55
NOME  = "Primary energy supply by source"
CLASS_ESPACIAL = 3   # bacia migra para Class_3; ver comum.padronizar_territorio
COL2  = "Variable name"
GRUPO = "Energy supply and use"

REN, NREN = "Renewable", "Non-renewable"

# ---------------------------------------------------------------------------
# PODER CALORÍFICO das matérias-primas, em kcal/kg.
#
# Necessário porque as commodities de biomassa do modelo estão em TONELADAS e
# as demais fontes em MWh. Sem isto a variável não fecha como matriz energética.
#
# CONVERSÃO: MWh/t = kcal/kg / 860   (1 kWh = 860 kcal, o mesmo coeficiente que
# o BEN usa para eletricidade, 0,086 tep/MWh).
#
# BASE: o projeto usa PCS. Trocar para "PCI" devolve a base inferior.
#
# ATENÇÃO — O LADO FÓSSIL DO MACRO ESTÁ EM PCI. Os emission_rate dos ativos de
# uso final reproduzem o fator de emissão dos combustíveis na base INFERIOR, com
# desvio de 0,3% a 1,4%; na base superior o desvio seria de 5,5% a 9,4%:
#
#     combustível   tCO2/MWh em PCI   em PCS   emission_rate do modelo
#     Diesel              0,268        0,250          0,271
#     Gasolina            0,256        0,239          0,257
#     Querosene           0,264        0,247          0,260
#     Gás natural         0,206        0,186          0,204
#
# Ou seja: converter a biomassa em PCS e deixar o fóssil como está mistura duas
# bases na mesma matriz, e a biomassa fica cerca de 10% mais pesada do que
# ficaria na base do resto da variável. Ponto para resolver com a equipe.
BASE = "PCS"

# PCI: só a cana vem do BEN (colmo integral, base úmida; o mesmo anexo traz
# caldo a 620 e melaço a 1.930). Os demais são de literatura, a confirmar
# contra o Anexo VIII do BEN.
PCI_KCAL_KG = {
    "Sugarcane":           1060,
    "Plantation forestry": 3100,
    "Forestry residues":   3100,
    "Corn":                3800,
    "Corn stover":         3500,
    "Rice straw":          3300,
    "Macauba":             3500,
}

# PCS derivado do PCI pela relação usual, PCS = PCI + 600 x (9H + W), com H a
# fração de hidrogênio e W a de umidade, ambas na base úmida. Hidrogênio de 6%
# na matéria seca para todas as biomassas; umidade por matéria-prima abaixo.
# SÃO VALORES DERIVADOS, não medidos — substituir pela tabela da equipe.
UMIDADE = {"Sugarcane": 0.70, "Plantation forestry": 0.25, "Forestry residues": 0.25,
           "Corn": 0.14, "Corn stover": 0.15, "Rice straw": 0.12, "Macauba": 0.25}
H_SECO = 0.06
LATENTE = 600.0        # kcal por kg de água


def pcs_kcal_kg(rotulo):
    pci = PCI_KCAL_KG.get(rotulo)
    if pci is None:
        return None
    w = UMIDADE.get(rotulo, 0.0)
    h = H_SECO * (1 - w)
    return pci + LATENTE * (9 * h + w)


KCAL_POR_MWH = 860_000.0

# True  -> biomassa convertida para GWh; a matriz fecha numa só unidade.
# False -> biomassa em Mt, como o modelo grava.
CONVERTER_BIOMASSA = True


def pci_mwh_t(rotulo):
    """MWh por tonelada, na base escolhida em BASE."""
    v = pcs_kcal_kg(rotulo) if BASE == "PCS" else PCI_KCAL_KG.get(rotulo)
    return None if v is None else v * 1000.0 / KCAL_POR_MWH


# padrão do nó -> (Class_1, Class_2 fonte BEN, Class_3 detalhe, unidade, fator,
#                  ESPACIAL)
#
# ESPACIAL diz se a fonte tem nó por estado. As que não têm saem SÓ na linha
# nacional — não existe linha estadual delas, nem 'Não Alocado'. É o caso dos
# fósseis e do urânio: no modelo eles são um ativo único do país. Ver a nota.
FONTES = [
    # diesel, gasolina e querosene NÃO entram aqui: são derivados, não energia
    # primária. Viram uma linha só de Crude oil, ver PETROLEO logo abaixo.
    (r"natgas_fossil_BR$",   NREN, "Natural gas",  "NA",      "GWh", 1e-3, False),
    # nacional e importado somados: o BEN não separa na matriz e a plataforma
    # não pediu a origem. Os nós continuam dois no modelo.
    (r"coal_BR$",            NREN, "Mineral coal", "NA",      "GWh", 1e-3, False),
    (r"coal_imported$",      NREN, "Mineral coal", "NA",      "GWh", 1e-3, False),
    (r"uranium_BR$",         NREN, "Uranium",      "NA",      "GWh", 1e-3, False),
    (r"sugarcane_BR(_[A-Z]{2})?$",        REN, "Sugarcane biomass",     "Sugarcane",           "Mt", 1e-6, True),
    # a palha de cana NÃO entra. O nó sugarcanestraw_BR tem saldo ZERO por
    # construção: a palha chega nele pela aresta de coproduto do colhedor, que
    # é passa-a-frente (entram 585,95 Mt de cana em 2050, saem as mesmas 585,95
    # mais 28,13 de palha). Pelo método do saldo ela não aparece de qualquer
    # jeito; contá-la exigiria ler o coproduct_edge. Decisão da equipe: fora.
    (r"biomass_wood_BR(_[A-Z]{2})?$",     REN, "Firewood and charcoal", "Plantation forestry", "Mt", 1e-6, True),
    (r"forestry_residue_BR(_[A-Z]{2})?$", REN, "Firewood and charcoal", "Forestry residues",   "Mt", 1e-6, True),
    (r"corn_BR(_[A-Z]{2})?$",             REN, "Other renewables",      "Corn",                "Mt", 1e-6, True),
    (r"cornstover_BR(_[A-Z]{2})?$",       REN, "Other renewables",      "Corn stover",         "Mt", 1e-6, True),
    (r"ricestraw_BR(_[A-Z]{2})?$",        REN, "Other renewables",      "Rice straw",          "Mt", 1e-6, True),
    (r"macauba_BR(_[A-Z]{2})?$",          REN, "Other renewables",      "Macauba",             "Mt", 1e-6, True),
    # soybean_BR fica FORA: fonte secundária no BEN (40,81 Mt em 2025, quase
    # zero depois, quando a macaúba assume o biodiesel).
]

# ---------------------------------------------------------------------------
# PETRÓLEO BRUTO A PARTIR DOS DERIVADOS
#
# O MACRO não tem refinaria: ele entrega diesel, gasolina e querosene fósseis
# prontos. Energia primária, porém, é PETRÓLEO BRUTO — é assim que o BEN monta
# a matriz. A conversão usa os rendimentos médios do parque de refino
# brasileiro, calculados a partir do BEN 2026, ano-base 2025.
#
# CADA DIVISÃO DEVOLVE O BARRIL INTEIRO, não uma fatia dele: o rendimento é
# "quanto deste produto sai de um barril". Rodar 1.000 TWh de petróleo dá 400
# de diesel, 231 de gasolina e 48 de querosene; dividir cada um pelo seu
# rendimento devolve 1.000 três vezes. SOMAR TRIPLICARIA, sempre exatamente 3x.
#
# A regra é o MÁXIMO: o petróleo processado é o que o derivado mais exigente
# obriga a rodar, e esse mesmo barril já entrega os outros dois, com sobra. É a
# mesma regra da id 71 (Oil production), que chama esse derivado de
# driving_derivative — e é sempre o diesel, nos seis períodos.
#
# A sobra não é artefato: em 2050 o barril que atende os 596,1 TWh de diesel
# entrega 344,3 TWh de gasolina contra 52,6 demandados. É a posição real do
# Brasil, longo em gasolina e curto em diesel.
PETROLEO = {
    r"diesel_fossil_BR$":   ("Diesel",   0.400),
    r"gasoline_fossil_BR$": ("Gasoline", 0.231),
    r"jetfuel_fossil_BR$":  ("Jet fuel", 0.048),
}
C2_PETROLEO = "Crude oil"

SUPORTA_UF = True

_UF_NO = re.compile(r"_BR_([A-Z]{2})$")

ORDEM = ["Crude oil", "Natural gas", "Mineral coal", "Uranium",
         "Hydraulic", "Wind", "Solar", "Sugarcane biomass",
         "Firewood and charcoal", "Other renewables"]


def gerar(root: Path, por_uf: bool = False, **kw):
    reg = {}

    def por(k, year, valor):
        reg.setdefault(k, {}).setdefault(year, 0.0)
        reg[k][year] += valor

    for p, year in PERIODS.items():
        s = saldo_nos(root, p)
        for pat, c1, c2, c3, un, fator, espacial in FONTES:
            if por_uf and not espacial:
                continue                        # fonte nacional: só a linha BR
            for no, val in s.items():
                if not re.match(pat, str(no)):
                    continue
                terr = "BR"
                if por_uf:
                    m = _UF_NO.search(str(no))
                    if not m:
                        continue                # nó sem UF, já está no nacional
                    terr = m.group(1)
                por((c1, c2, c3, un, terr), year, val * fator)

        # PETRÓLEO BRUTO: o maior dos três, não a soma. Ver PETROLEO acima.
        if not por_uf:                      # não há nó de petróleo por estado
            bruto = max((sum(val for no, val in s.items() if re.match(pat, str(no)))
                         / rend)
                        for pat, (_rot, rend) in PETROLEO.items())
            por((NREN, C2_PETROLEO, "NA", "GWh", "BR"), year, bruto * 1e-3)

        d = fluxos(root, p)

        # HIDRÁULICA POR BACIA, NÃO POR ESTADO. As usinas do modelo não têm UF:
        # a unidade espacial delas é a bacia hidrográfica, e várias cruzam
        # divisas. Reservatório (nó hydro_source_<bacia>, já líquido de
        # vertimento) e fio d'água (geração do MustRun) somados numa linha só.
        # SAI UMA VEZ SÓ, no passe nacional (correção incorporada de outra
        # rodada, 02/09/2026). A bacia vira Class_3 e o Territory vira BR na
        # padronização; uma linha nacional junto seria indistinguível das
        # bacias e dobraria a soma. As bacias somam o total.
        if not por_uf:
            for no, val in s.items():
                if not str(no).startswith("hydro_source_"):
                    continue
                b = bacia(str(no)[len("hydro_source_"):])
                por((REN, "Hydraulic", "NA", "GWh", b), year, val * 1e-3)
            ror = d[(d.resource_type == "MustRun") & (d.value > 0)]
            for r in ror.itertuples():
                b = bacia_de_id(r.resource_id)
                por((REN, "Hydraulic", "NA", "GWh", b), year, float(r.value) * 1e-3)

        # solar e eólica: energia primária = geração (conteúdo físico, como o BEN)
        v = d[(d.resource_type == "VRE{Generic}") & (d.value > 0)]
        for r in v.itertuples():
            rid = str(r.resource_id)
            fonte, det = vre(re.sub(r"^BR_[A-Z]{2}_", "", rid))
            c2 = "Solar" if fonte.startswith("Solar") else "Wind"
            terr = "BR"
            if por_uf:
                m = re.match(r"^BR_([A-Z]{2})_", rid)
                if not m:
                    continue
                terr = m.group(1)
            por((REN, c2, det, "GWh", terr), year, float(r.value) * 1e-3)

    out = []
    for k in sorted(reg, key=lambda x: (ORDEM.index(x[1]), x[2], x[4])):
        c1, c2, c3, un, terr = k
        pci = pci_mwh_t(c3) if (un == "Mt" and CONVERTER_BIOMASSA) else None
        for year in PERIODS.values():
            v = reg[k].get(year, 0.0)
            if pci is not None:                 # Mt -> GWh
                v, un_out = v * 1e6 * pci * 1e-3, "GWh"
            else:
                un_out = un
            out.append(row(GRUPO, NOME, c1=c1, c2=c2, c3=c3, c4="NA", c5="NA",
                           unit=un_out, territory=terr, year=year,
                           value=round(v, 5)))
    return out
