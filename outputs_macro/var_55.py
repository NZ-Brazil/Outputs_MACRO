# -*- coding: utf-8 -*-
"""id 55 — Primary energy supply by source, agregada como o BEN agrega.

Fonte: flows_annual/flows_annual_results_period_<p>.csv

Não existe linha de 'supply' no flows.csv, só arestas de ativos. A oferta
primária vem do SALDO LÍQUIDO dos nós de recurso (ver comum.saldo_nos). Solar,
eólica e fio d'água não têm nó de recurso: a energia primária delas é a própria
geração.

CLASSES — reorganizadas a pedido da equipe em 15/09/2026. A FONTE DESCEU PARA A
CLASS_3 e a CLASS_2 passou a dizer PARA ONDE a energia primária vai:

    Class_1 = Renewable / Non-renewable
    Class_2 = destino/família  (Refinery, Thermal power, Thermal power and H2
              production, Hydraulic, Wind onshore, Wind offshore, Solar
              rooftop, Solar utility-scale, Bioenergy)
    Class_3 = a fonte        (Crude oil, Natural gas, Mineral coal, Uranium,
              Hydraulic, Wind, Solar, e as sete matérias-primas de biomassa)
    Class_4 = bacia hidrográfica, só na hidráulica (ver CLASS_ESPACIAL)
    Class_5 = N/A

O QUE ISSO MUDOU EM RELAÇÃO AO BEN. Até 15/09 a Class_2 era a fonte na
nomenclatura do BEN, e as sete biomassas se distribuíam em três categorias
dele — 'Sugarcane biomass', 'Firewood and charcoal' e 'Other renewables'.
Essas três categorias NÃO SAEM MAIS: agora as sete entram como 'Bioenergy' na
Class_2, com a matéria-prima na Class_3. Quem precisar da leitura BEN reagrupa
a partir da Class_3, que é mais fina do que as categorias do BEN. Nenhum valor
muda; a soma da variável é a mesma.

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

NOTA   = NOTAS[55]
RESUMO = RESUMOS[55]

ID    = 55
NOME  = "Primary energy supply by source"
# Bacia migra para a Class_4 (era Class_3 até 15/09/2026, quando a Class_3
# passou a guardar a fonte e a hidráulica repetiu 'Hydraulic' nela). Ver
# comum.padronizar_territorio.
CLASS_ESPACIAL = 4
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


# padrão do nó -> (Class_1, Class_2 destino, Class_3 fonte, unidade, fator,
#                  ESPACIAL)
#
# ESPACIAL diz se a fonte tem nó por estado. As que não têm saem SÓ na linha
# nacional — não existe linha estadual delas, nem 'Não Alocado'. É o caso dos
# fósseis e do urânio: no modelo eles são um ativo único do país. Ver a nota.
#
# O DESTINO DA CLASS_2 NOS NÃO-RENOVÁVEIS foi ditado pela equipe (15/09/2026) e
# é uma descrição do uso, não um resultado do modelo: petróleo vai para o
# refino, gás natural para termelétrica e produção de H2, carvão e urânio só
# para termelétrica. Se o modelo passar a dar outro uso a uma dessas fontes,
# ESTES RÓTULOS NÃO ACOMPANHAM SOZINHOS — têm que ser revistos aqui.
BIOENERGIA = "Bioenergy"
FONTES = [
    # diesel, gasolina e querosene NÃO entram aqui: são derivados, não energia
    # primária. Viram uma linha só de Crude oil, ver PETROLEO logo abaixo.
    (r"natgas_fossil_BR$",   NREN, "Thermal power and H2 production", "Natural gas",  "GWh", 1e-3, False),
    # nacional e importado somados: o BEN não separa na matriz e a plataforma
    # não pediu a origem. Os nós continuam dois no modelo.
    (r"coal_BR$",            NREN, "Thermal power", "Mineral coal", "GWh", 1e-3, False),
    (r"coal_imported$",      NREN, "Thermal power", "Mineral coal", "GWh", 1e-3, False),
    (r"uranium_BR$",         NREN, "Thermal power", "Uranium",      "GWh", 1e-3, False),
    (r"sugarcane_BR(_[A-Z]{2})?$",        REN, BIOENERGIA, "Sugarcane",           "Mt", 1e-6, True),
    # a palha de cana NÃO entra. O nó sugarcanestraw_BR tem saldo ZERO por
    # construção: a palha chega nele pela aresta de coproduto do colhedor, que
    # é passa-a-frente (entram 585,95 Mt de cana em 2050, saem as mesmas 585,95
    # mais 28,13 de palha). Pelo método do saldo ela não aparece de qualquer
    # jeito; contá-la exigiria ler o coproduct_edge. Decisão da equipe: fora.
    (r"biomass_wood_BR(_[A-Z]{2})?$",     REN, BIOENERGIA, "Plantation forestry", "Mt", 1e-6, True),
    (r"forestry_residue_BR(_[A-Z]{2})?$", REN, BIOENERGIA, "Forestry residues",   "Mt", 1e-6, True),
    (r"corn_BR(_[A-Z]{2})?$",             REN, BIOENERGIA, "Corn",                "Mt", 1e-6, True),
    (r"cornstover_BR(_[A-Z]{2})?$",       REN, BIOENERGIA, "Corn stover",         "Mt", 1e-6, True),
    (r"ricestraw_BR(_[A-Z]{2})?$",        REN, BIOENERGIA, "Rice straw",          "Mt", 1e-6, True),
    (r"macauba_BR(_[A-Z]{2})?$",          REN, BIOENERGIA, "Macauba",             "Mt", 1e-6, True),
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
C3_PETROLEO = "Crude oil"
C2_PETROLEO = "Refinery"

SUPORTA_UF = True

_UF_NO = re.compile(r"_BR_([A-Z]{2})$")

# ---------------------------------------------------------------------------
# EÓLICA E SOLAR — nomenclatura PRÓPRIA da id 55, de propósito.
#
# A equipe pediu (15/09/2026) 'Wind offshore' na Class_2 e 'Wind' na Class_3;
# 'Solar rooftop' e 'Solar utility-scale' na Class_2 e 'Solar' na Class_3. As
# ids 66, 67 e 68 usam _eletrico.vre(), que escreve 'Solar photovoltaic' +
# 'Rooftop'. São convenções DIFERENTES para a mesma usina, e é assim que a
# equipe quer: aqui é matriz de oferta primária, lá é parque gerador. Por isso
# este mapa é local e não chama _eletrico — mexer lá não pode mudar isto aqui,
# nem o contrário.
VRE = {
    "Solar":         ("Solar utility-scale", "Solar"),
    "rooftop_pv":    ("Solar rooftop",       "Solar"),
    "Wind_Onshore":  ("Wind onshore",        "Wind"),
    "Wind_Offshore": ("Wind offshore",       "Wind"),
}


def _vre(fam: str):
    """(Class_2, Class_3) a partir da família do resource_id. None se não bate."""
    for prefixo, par in VRE.items():
        if fam.startswith(prefixo):
            return par
    return None


# Ordem de saída, pela Class_3 (a fonte). A biomassa segue a ordem que a equipe
# escreveu em 15/09/2026. Fonte fora desta lista vai para o fim, e gerar()
# avisa no terminal.
ORDEM = ["Crude oil", "Natural gas", "Mineral coal", "Uranium",
         "Hydraulic", "Wind", "Solar",
         "Sugarcane", "Forestry residues", "Plantation forestry",
         "Corn", "Corn stover", "Macauba", "Rice straw"]


def _ordem(c3):
    return ORDEM.index(c3) if c3 in ORDEM else len(ORDEM)


def gerar(root: Path, por_uf: bool = False, **kw):
    reg, sem_rotulo = {}, set()

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
            por((NREN, C2_PETROLEO, C3_PETROLEO, "GWh", "BR"), year, bruto * 1e-3)

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
                # 'Hydraulic' REPETIDO na Class_2 e na Class_3 (equipe,
                # 15/09/2026): a Class_3 é a fonte, e a fonte é a própria
                # hidráulica. A bacia sai daqui na Class_4, pela
                # CLASS_ESPACIAL — não a escreva aqui.
                por((REN, "Hydraulic", "Hydraulic", "GWh", b), year, val * 1e-3)
            ror = d[(d.resource_type == "MustRun") & (d.value > 0)]
            for r in ror.itertuples():
                b = bacia_de_id(r.resource_id)
                por((REN, "Hydraulic", "Hydraulic", "GWh", b), year,
                    float(r.value) * 1e-3)

        # solar e eólica: energia primária = geração (conteúdo físico, como o BEN)
        v = d[(d.resource_type == "VRE{Generic}") & (d.value > 0)]
        for r in v.itertuples():
            rid = str(r.resource_id)
            fam = re.sub(r"^BR_[A-Z]{2}_", "", rid)
            par = _vre(fam)
            if par is None:
                sem_rotulo.add(fam)
                # sem rótulo: a família crua vai para as duas classes, para o
                # valor não sumir, e o aviso abaixo denuncia.
                par = (fam, fam)
            c2, c3 = par
            terr = "BR"
            if por_uf:
                m = re.match(r"^BR_([A-Z]{2})_", rid)
                if not m:
                    continue
                terr = m.group(1)
            por((REN, c2, c3, "GWh", terr), year, float(r.value) * 1e-3)

    if sem_rotulo:
        print(f"      [55] AVISO: {len(sem_rotulo)} família(s) de solar/eólica "
              f"fora do mapa VRE — o nome cru do ativo vai sair nas Class_2 e "
              f"Class_3: " + ", ".join(sorted(sem_rotulo)))

    out = []
    # ordena pela FONTE (Class_3), depois pelo destino (Class_2) e pelo
    # território. Era pela Class_2 até 15/09/2026, quando a fonte mudou de coluna.
    for k in sorted(reg, key=lambda x: (_ordem(x[2]), x[1], x[4])):
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
