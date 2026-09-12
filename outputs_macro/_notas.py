# -*- coding: utf-8 -*-
"""Notas de leitura de cada variável.

Viajam junto com a saída: montar.py escreve todas em plataforma/LEIA-ME.txt e
na aba "Notas" do workbook. Editar aqui, não nos módulos.

Cada texto responde a três perguntas: o que a variável mede exatamente, que
decisão foi tomada onde havia mais de uma leitura possível, e o que quem for
usar o número precisa saber para não interpretá-lo errado.
"""

NOTAS = {}


NOTAS[-3] = """LINHAS COM RECORTE ESPACIAL QUE NÃO É UF (correção incorporada de outra
rodada, 02/09/2026)

O padrão da plataforma define Territory como <BR ou UF>. O MACRO produz três
recortes espaciais que NÃO são UF, todos legítimos e todos impossíveis nessa
coluna:

    bacia hidrográfica       ids 55, 66, 68 — as hidrelétricas do modelo têm a
                             bacia como zona, não o estado, e várias cruzam
                             divisas: a discretização delas é por bacia mesmo
    corredor de transmissão  id 70
    bacia sedimentar         ids 73, 74
    'Não Alocado'            id 65

REGRA ADOTADA: o recorte que não é UF passa para a Class declarada em
CLASS_ESPACIAL no var_<id>.py e o Territory da linha vira BR, via
comum.padronizar_territorio. Onde as cinco Class já estavam ocupadas, a linha
sai do entregável — a linha nacional continua contando o valor dela.

Qual Class recebe o recorte mudou com a reorganização de classes pedida pela
equipe em 11/09/2026, porque ela ocupou slots que antes estavam livres:

    id 55                Class_3 (bacia). Não mudou: a id 55 não entrou na
                         reorganização e a Class_3 dela continua vazia.
    id 66                Class_3 (bacia), por pedido da equipe (12/09/2026).
                         A bacia sobrescreve o rótulo fixo 'Electricity
                         generation (public service)' nas linhas de
                         hidrelétrica; Class_4 e Class_5 ficam 'NA'.
    id 68                Class_4 (bacia) — era Class_3. Aqui a Class_3 guarda
                         o rótulo fixo e a bacia vai para o primeiro slot
                         livre. As duas variáveis tratam as MESMAS
                         hidrelétricas com convenções diferentes: a equipe
                         conferiu a saída em 12/09/2026 e manteve assim.
    id 70                Class_2 (corredor) — era Class_3. O nome do corredor
                         já é escrito em Class_2 pelo próprio gerar(), então a
                         migração aponta para o mesmo slot e só reescreve o
                         valor que já está lá; Class_3 fica 'NA'.
    ids 73, 74           sem CLASS_ESPACIAL: a bacia sedimentar é escrita
                         direto em Class_1 por gerar(), e o Territory dessas
                         linhas já é UF.
    id 65                sem coluna livre. As 12 linhas de 'Não Alocado'
                         saíram do recorte espacial — são os dois ativos
                         NACIONAIS da rota Alcohol-to-jet (BR_ATJ_ethanol e
                         BR_ATJ_Diesel), sem UF no resource_id. Nada se perde
                         no total: a linha BR continua contando os 20.160 GWh
                         somados nos seis períodos. Mas ATENÇÃO ao mapa — ver
                         a nota da id 65: em 2050 esses ativos são 99,3% de
                         todo o SAF do país, então a soma das UFs de SAF dá
                         quase zero enquanto a linha BR dá 5,2 TWh.

ONDE O RECORTE É BACIA OU CORREDOR, NÃO HÁ LINHA NACIONAL — as partes somam o
todo. Isso vale para a hidráulica das ids 55, 66 e 68 e para os corredores da
id 70: a bacia ou o corredor está na Class_3, o Territory é BR, e não existe
uma linha agregada junto. Somar tudo dá o número nacional certo.

    id 55  hidráulica: 15 linhas de bacia, 392.767 GWh em 2050
    id 66  hidráulica: 29 linhas de bacia por tipo (reservatório / fio d'água)
    id 68  idem
    id 70  35 corredores, 252,0 GW em 2050

CUIDADO: isto NÃO vale para o recorte por UF. As fontes com estado — cana,
solar, eólica, lenha nas ids 55, 65, 66, 67 e 68 — continuam trazendo a linha
nacional (Territory = BR) E as estaduais no mesmo arquivo, porque ali o
Territory distingue as duas. Aí sim, somar sem filtrar dobra.
"""

NOTAS[-2] = """RESSALVAS ACEITAS NESTA VERSÃO — leia antes de usar os números
=============================================================================

Tudo abaixo é conhecido e foi conscientemente aceito para esta rodada. Não são
erros por descobrir. A coluna 'destrava' diz o que precisa acontecer para o item
sair da lista. O detalhe de cada um está na nota da variável correspondente.

-----------------------------------------------------------------------------
A. AFETAM O VALOR PUBLICADO
-----------------------------------------------------------------------------

A1. Bypass de combustão dos líquidos fósseis                      id 18
    (revisto em 01/09/2026 — o mecanismo e os anos estavam descritos errado)

    Cada líquido fóssil chega à demanda final por DUAS ROTAS PARALELAS:
      contabilizada  nó <fuel>_fossil_BR -> GeneralFuelsEndUse, que tem
                     emission_rate e registra a queima;
      bypass         UpstreamEmissions{LiquidFuels} -> nó <fuel>_demand_BR.
                     Esse ativo só contabiliza o CO2 de refino; a queima do
                     volume que ele entrega não é registrada em lugar nenhum.

    O QUE PASSA POR CADA ROTA (TWh) E O QUE SE PERDE (Mt CO2):

                  diesel            gasolina          querosene     perdido
              conta   bypass    conta   bypass    conta  bypass      total
      2025    188,4    365,3    174,4     17,9     32,9    11,0      106,5
      2030      0,0    553,5    224,3     32,6     21,3    22,6      164,4
      2035      0,0    547,3    219,6     34,7     19,9    23,7      163,5
      2040      0,0    569,5    169,0     35,4     19,9    24,8      170,0
      2045      0,0    584,5     84,8     34,0     20,5    25,6      173,9
      2050      0,0    596,1     21,8     30,8     21,0    26,2      176,4

    NÃO É SÓ O DIESEL e NÃO COMEÇA EM 2030. O diesel migra inteiro para o
    bypass a partir de 2030, e é o grosso do buraco (161,7 dos 176,4 Mt de
    2050), mas gasolina e querosene mantêm as duas rotas em todos os períodos.
    Já em 2025 faltam 106,5 Mt — o ano-base também está subestimado.

    Efeito no líquido publicado:
      publicado   613,2  391,0  167,9  -54,1  -277,1  -499,8
      + bypass    719,8  555,3  331,4  115,9  -103,2  -323,4

    ISSO NÃO É ERRO DE RELATO: a id 18 reproduz o flows.csv na terceira casa. O
    volume não emite dentro do modelo, e o cap de emissões foi otimizado sobre
    a mesma base subestimada — então a trajetória inteira está deslocada, não
    só o número publicado.
    Destrava: correção no modelo.

A2. co2_content da cana em base seca                       ids 19, 73, 65
    A cana tem rendimento (0,55 MWh/t) e preço (19 US$/t) em base ÚMIDA, mas
    co2_content de 1,558 tCO2/t, que é base SECA — a cana úmida carrega ~0,5.
    Fator de cerca de 3 dentro da mesma commodity.
    Efeito: a id 73 reporta 516 Mt estocados em 2050; corrigido, ~270 Mt. A id
    19 e a escolha de tecnologia da id 65 herdam o mesmo desvio.
    Destrava: definir a base da commodity e corrigir o co2_content.

A3. Carbono biogênico sem destino                             ids 18, 19
    O balanço da biomassa não fecha: entra mais como absorção do que sai como
    emissão ou estoque. Resíduo de 7,1 Mt em 2025 e 339,6 Mt em 2050. Não há
    restrição de fechamento sobre o carbono biogênico no modelo.

    ONDE ISSO SE CONCENTRA (2050, Mt, revisão de 01/09/2026):

        ativo                   absorve   emite   captura   sobra
        BECCSEthanolv2            916,8     7,0     493,9   415,9
        BiomassTransformation      47,5     0,0       0,0    47,5
        BECCSDieselv2             122,1    97,3       0,0    24,8
        BECCSCharcoal              27,6    12,0       0,0    15,6
        BECCSATJ                    1,8     0,0       0,0     1,8
        BECCSElectricity          230,8   251,5      19,4   -40,2
                                                    soma     465,4

    A soma de 465,4 menos os 125,7 Mt queimados no uso final dá os 339,6 do
    resíduo. Não é um desequilíbrio difuso: é UM ativo. O BECCS de etanol
    responde por 341 dos 339,6 Mt — 586 Mt de cana entram carregando 916,8 Mt
    de CO2 e saem como 7,0 liberados na conversão, 493,9 capturados e 322 TWh
    de etanol, que ao queimar dão 74,8 Mt (a id 18 registra 74,5). Faltam 341.

    O CASO INVERSO, no BECCS de eletricidade: ele EMITE 251,5 e captura 19,4 a
    partir de uma biomassa que carregava 230,8 — libera 40,2 Mt de carbono que
    nunca absorveu. Os dois problemas têm a mesma origem, parâmetros
    inconsistentes dentro do mesmo ativo, e sinais opostos.

    Efeito: boa parte dos -499,8 Mt de 2050 vem daí.
    Destrava: restrição de fechamento no modelo, e revisão do co2_content x
    emission_rate ativo por ativo (ver A2).

A4. Emissões exógenas congeladas                                  id 18
    O bloco 'Exogenous emissions' fica em 284,4 Mt/ano nos seis períodos. O
    input system/CO2_Emissions.csv previa 284,4 (2025) a 355,9 Mt (2050), mas o
    modelo míope só lê existing_capacity no período 1.
    Efeito: faltam ~71 Mt/ano em 2050.
    Destrava: correção no modelo.

A5. Laço de gás natural em 2025                               ids 18, 55
    O UpstreamEmissions{NaturalGas} tem as duas arestas no mesmo nó natgas_BR e
    circula 3.662 TWh em 2025, gerando 164,8 Mt de CO2 espúrios. Em 2050 o laço
    é de 0,03 TWh.
    Efeito: o upstream fóssil da id 18 sai de 172,7 Mt em 2025 para 12,1 em
    2030 — o degrau não é real.
    Destrava: correção no modelo.

A6. Colunas trocadas no fuel_prices_2030.csv                      id 72
    coal_price_BR vai de 13,90 para 83,39 e volta para 13,22 US$/MWh; o valor de
    2030 é exatamente o preço do querosene, e o do carvão importado é o do gás.
    Efeito: a geração a carvão cai para 10,50 TWh em 2030 e volta a 13,68 em
    2035 — o vale existe por causa do preço, não da economia do cenário.

    CONFIRMADO POR TESTE INDEPENDENTE em 02/09/2026, comparando o caso com as
    trajetórias do card 24 do integrador (data/card24_prices.py). O caso não
    reproduz nenhuma das três opções — é outra safra de números —, mas cada
    combustível guarda uma RAZÃO CONSTANTE com a opção A ao longo dos seis
    períodos, o que mostra que é rescalonamento e não erro:

        gás natural 1,000 (bate exato) · querosene 1,028 · carvão nacional 1,278
        carvão importado 0,885 · diesel 0,858 · gasolina 0,846 · urânio 0,546

    A razão só quebra em quatro células, e três delas são as que esta ressalva
    já apontava:

        2030 carvão nacional    7,861 no lugar de 1,278
        2030 carvão importado   1,769 no lugar de 0,885
        2030 querosene          1,137 no lugar de 1,028
        2025 carvão importado   0,609 no lugar de 0,885   <- NÃO estava na lista

    O QUE ISSO MUDA NA PRÁTICA: numa rodada da plataforma o card 24 reescreve
    fuel_prices_*.csv inteiro para a opção que o usuário escolher, então as
    células trocadas somem sozinhas. O problema é desta rodada: os resultados
    publicados foram otimizados com elas. O vale do carvão em 2030 é artefato.
    Destrava: rodada nova com o card 24 aplicado.

A7. Base calorífica misturada                                     id 55
    A biomassa é convertida em PCS; o lado fóssil do modelo está em PCI,
    conferido pelos emission_rate (desvio de 0,3% a 1,4% contra PCI, 5,5% a
    9,4% contra PCS).
    Efeito, medido na matriz de 2050 (revisão de 01/09/2026): a biomassa passa
    de 2.126,3 TWh em PCS para 1.660,2 em PCI, 21,9% menor, e a matriz inteira
    de 4.864,6 para 4.398,5 TWh — 466,1 TWh, ou 9,6% da oferta primária. Não é
    um ajuste marginal: a escolha da base move quase um décimo da variável.
    A razão PCS/PCI por matéria-prima mostra por que a cana domina o efeito —
    a 70% de umidade o termo de calor latente pesa mais que o próprio PCI:

        cana 1,488 · lenha e resíduo florestal 1,127 · macaúba 1,112 ·
        palha de arroz 1,108 · palha de milho 1,104 · milho 1,095

    DECIDIDO EM 01/09/2026: fica em PCS mesmo com o desvio. A correção sai na
    próxima rodada do modelo, não na montagem do output.
    Destrava: uma linha — BASE = "PCI" aqui, ou emission_rate em PCS.

A8. Duplas contagens de captação                                  id 19
    Rotas menores que consomem Residue registram captação de novo sobre carbono
    já capturado no BiomassTransformation (3,12 Mt em 2050); e o
    ethanol-to-jet, que consome ETANOL e não biomassa, registra 1,76 Mt de
    captação com emissão zero.
    Efeito: 4,9 Mt em 2050 de remoção sem lastro.
    Destrava: correção no modelo.

A9. Macaúba anterior à correção                            ids 19, 55, 65
    Já foi alterada no MACRO; estes resultados são anteriores. Responde por
    180,1 dos 180,2 TWh de biodiesel de 2050.
    Destrava: rodada nova.

A11. Fio d'água: disponibilidade implausível por bacia    ids 55, 66, 68
    O availability_hydro_ror_<ano>.csv traz fator de capacidade médio de 1,6%
    para o Amazonas e 93,5% para o Paraná. Nenhum dos dois é plausível: a bacia
    Amazonas tem 22,7 GW de fio d'água (Belo Monte, Jirau, Santo Antônio) e
    gera 3,1 TWh em 2050, enquanto o Paraná gera 80,7 TWh com 10,2 GW.
    Efeito: o TOTAL NACIONAL de hidráulica está certo — 392,8 TWh em 2050,
    compatível com o Brasil — mas a DISTRIBUIÇÃO POR BACIA não está. O mapa de
    bacias da 52, da 64 e da 66 herda o problema.
    Destrava: revisar as séries de disponibilidade do fio d'água no input.

A10. Lenha de co-insumo sem captação                              id 19
    Três rotas queimam lenha de floresta plantada como co-insumo de processo —
    etanol de milho (21,2 Mt de lenha sobre 66,6 Mt de milho em 2025, 24%),
    FAME de soja (5,7%) e FAME de macaúba (6,5%) — e o modelo não registra
    captação nenhuma sobre ela: o co2_content do ativo multiplica só a aresta
    principal. A lenha é consumida, sai do nó de oferta e aparece na id 55, mas
    o carbono dela não entra na id 19.
    Efeito: não muda o total de remoções, que segue fechando com o cap. Muda
    quanto o modelo reconhece de absorção real: em 2025 são 23,7 Mt de lenha
    (21,2 + 2,5) com absorção não contabilizada.
    Destrava: correção no modelo, ou confirmação de que a lenha de co-insumo é
    deliberadamente tratada como neutra.

-----------------------------------------------------------------------------
B. NÃO AFETAM O VALOR, MAS MUDAM A LEITURA
-----------------------------------------------------------------------------

B1. Expansão de gás e nuclear toda em São Paulo               ids 66, 68
    O parque existente está por UF, mas a expansão tem um único candidato
    nacional por tecnologia, com end_vertex = elec_BR_SP. Os 30,9 GW novos de
    2050 nascem todos em SP. O total nacional está correto; o mapa estadual, não.
    ESCLARECIMENTO DA EQUIPE: é deliberado. O candidato de gás é um ATIVO ÚNICO
    DO PAÍS, ligado ao nó de SP apenas por ser o ponto de maior demanda — não
    é uma previsão de que as térmicas serão construídas em São Paulo. Ler o
    mapa estadual dessa expansão como localização é erro de leitura, não do
    modelo. Vale para a 64 e a 66; na 52 o gás não tem linha estadual nenhuma,
    justamente por ser nacional.

B2. Bioeletricidade sem capacidade elétrica                   ids 66, 68
    No capacity.csv o BECCSElectricity tem capacidade em MW de biomassa de
    ENTRADA. A id 68 mostra 172 TWh (14% da geração de 2050) sem parque
    correspondente na id 66.

B3. Hidrelétricas sem UF                                      ids 66, 68
    A zona delas no modelo é a bacia hidrográfica. Aparecem por bacia, não por
    estado — 100,6 GW e 392,8 TWh em 2050.

B4. Adição do quinquênio, não média anual                         id 67
    DECIDIDO EM 02/09/2026: fica o quinquênio. A resolução temporal de cinco em
    cinco anos foi convencionada para todos os outputs, e dividir por 5 criaria
    um número que não corresponde a nenhum período do modelo.

    Só que o nome da variável na aba é 'Solar, wind and battery AVERAGE ANNUAL
    capacity additions', então há um fator de 5 entre o rótulo do card e o
    número plotado. Em 2050 (GW):

        tecnologia            publicado   se fosse média anual
        Solar photovoltaic        27,24                  5,45
        Wind                      19,26                  3,85
        Battery storage            3,55                  0,71

    PARA A EQUIPE DA PLATAFORMA: ou o card muda de nome — 'capacity additions
    per 5-year period' — ou ele divide por 5 na exibição. Do nosso lado o número
    é a adição do quinquênio, e a flag MEDIA_ANUAL em var_67.py continua False.

B5. Custo com a cauda míope                                       id 24
    O DiscountedTotalCost inclui anuidades além da janela míope de cada período,
    então não reconcilia com o objective_value.csv. É valor presente do
    quinquênio, não custo anual.

B6. Recorte do sistema, não do país                               id 55
    A oferta interna do modelo é 182 Mtep em 2025 contra ~316 Mtep da OIE real.
    O MACRO não cobre usos não-energéticos nem toda a demanda industrial. As
    participações percentuais são internamente consistentes; os valores
    absolutos não são comparáveis linha a linha com o BEN.

B7. Inversão milho/cana em 2025                            ids 55, 65, 19
    184,4 TWh de etanol de milho contra 8,3 de cana, inverso do Brasil real. Na
    matriz da id 55 isso aparece como biomassa da cana em 1,3% contra 16,7% do
    BEN. Causas rastreadas: pedágio de CCT de 15 US$/t só no caminho da cana e
    preço do milho a 110 US$/t contra 180 a 220 de mercado.

B8. Salto soja para macaúba no biodiesel                          id 65
    O ativo Macauba_FAME não existe em assets_2025, e a soja existente tem
    can_retire = False até 2040 — paga O&M fixo em 12.660 MW parados em 2030 e
    2035, cerca de 192 M US$/ano.

B9. Sem separação por setor de uso final                      ids 18, 56
    O GeneralFuelsEndUse agrega a demanda num nó por combustível. Transportes,
    indústria, residencial e comercial não são distinguíveis; essas classes vão
    como N/A.

B10. PCI de literatura                                            id 55
    Só o da cana vem do BEN (1060 kcal/kg). Os outros seis são de literatura,
    a substituir pelo Anexo VIII do BEN ou pela tabela da equipe.

B11. Capacidade inicial de transmissão em placeholder            id 70
    27 dos 35 corredores partem de exatamente 1.000 MW, valor declarado como
    placeholder no próprio input (recontado em 01/09/2026; a nota dizia 26 de
    31). São 27,0 dos 95,3 GW de 2025 — 28% do estoque inicial — e 11% do de
    2050. A expansão sobre esse piso é otimizada e vale; o piso não.
    ACEITA pela equipe: publicar assim.

B13. O total soma SENTIDOS, não linhas físicas                    id 70
    A interligação Sul–Sudeste é representada no modelo como DOIS links de
    sentido único, com limites diferentes por direção: S→SE 8,00 GW e SE→S
    11,46 GW em 2050. A variável reporta os dois como corredores separados, e o
    total nacional soma as duas pontas — 19,47 GW para uma infraestrutura só.
    DECIDIDO EM 01/09/2026: somar os sentidos. O total de 2050 é 252,0 GW. O
    limite assimétrico por sentido é real e o ONS publica assim, então a
    variável mede capacidade de transferência POR SENTIDO, e é isso que o total
    agrega. Contando linhas físicas seriam 244,0 GW — não é o que publicamos.
    Os outros dois links de sentido único (Itaipu→Sudeste 10 GW, Belo
    Monte→Sudeste 8 GW) são escoamento de geração e não têm par.

B12. Duas variáveis trocam de unidade ou de escopo             ids 27, 70
    A 70 reporta GW de capacidade no lugar dos km que a planilha da plataforma
    pede, porque a distância no input é "for record-purpose only". A 27 entrega
    despesa com combustível fóssil POR PORTADOR, e não o estoque de capital de
    uso final que o nome do card designa — é insumo para a equipe de end-use,
    que faz a distribuição a partir daqui. Nos dois casos o rótulo do card
    precisa acompanhar; o número está certo dentro do que foi acordado.

-----------------------------------------------------------------------------
C. PENDÊNCIAS DE DEFINIÇÃO, NÃO DE DADO
-----------------------------------------------------------------------------

C1. id 18 — reestruturação para o card 32. Slot do EP identificado e formato
    mapeado; faltam a base da repartição, se refino tem linha própria e o
    tratamento dos anos intermediários. Aguarda planilha agregada da equipe.

C2. ids 56 e 57 — eletricidade medida em dois pontos. A 57 mede na barra de
    geração (1.221,0 TWh em 2050) e a 56 na chegada ao consumidor (1.206,7 TWh).
    A diferença de 14,3 TWh são perdas de transmissão menos round-trip de
    bateria. Não é erro, é convenção — mas a plataforma precisa decidir se
    mostra as duas lado a lado sem nota, porque o usuário vai comparar.
"""

NOTAS[-1] = """MACAÚBA — matéria-prima já corrigida no modelo (ids 19, 55, 65)

Os valores de macaúba desta rodada são ANTERIORES a uma correção que a equipe já
aplicou no MACRO. Não foram alterados aqui: quando a rodada nova chegar, eles
virão como o modelo os produzir. Mantidos como estão para que as ids 18 e 19
continuem fechando com o cap de emissões.

Nesta rodada a macaúba responde por praticamente todo o biodiesel de 2030 em
diante — 180,1 dos 180,2 TWh de 2050 na id 65, 114,1 Mt de remoção na id 19 e
75,7 Mt de oferta primária na id 55.

O que dava problema: o ativo Macauba_FAME não existe em assets_2025, só a partir
de assets_2030, e a curva de oferta traz 168,2 Mt/ano disponíveis integralmente
já no primeiro ano em que o ativo existe, constante até 2050, sem rampa — para
uma cultura pré-comercial cuja palmeira leva de 4 a 7 anos para produzir."""

NOTAS[0] = """LINHAS NACIONAIS E ESTADUAIS NO MESMO ARQUIVO (ids 55, 65, 66, 67, 68, 69)

Essas variáveis saem com o total nacional (Territory = BR) E a quebra espacial
no mesmo CSV — a 55 e a 69 tiveram o recorte por UF ligado em 02/09/2026, junto
com a correção que moveu bacia/corredor para a Class_3 (ver a nota de
Territory). Conferido: a soma das linhas espaciais bate com a linha BR em
todos os anos, com diferença menor que 0,001.

CONSEQUÊNCIA: somar a coluna Value sem filtrar Territory DOBRA o resultado.
Toda leitura precisa escolher: Territory == 'BR' para o nacional, ou
Territory != 'BR' para o recorte espacial.

A COLUNA TERRITORY TEM TRÊS TIPOS DE VALOR:

  Sigla de UF          AC, AL, ..., SP, TO — 27 unidades da federação.
  Nome de bacia        as 15 bacias hidrográficas do modelo (Paraná, Tocantins,
                       São Francisco...), agora na Class_3 e não no Territory
                       (ver a nota de Territory). As hidrelétricas não têm UF:
                       a zona delas no modelo é a bacia, e várias cruzam
                       divisas estaduais, então a discretização espacial delas
                       é por bacia mesmo. São 100,6 GW na id 66 e 392,8 TWh na
                       id 68 em 2050, e entram também na id 55. Já 'Paraná' e
                       'São Francisco' nomeiam TAMBÉM bacias sedimentares nas
                       ids 73 e 74: são coisas diferentes, distinguíveis pelo
                       Variable_group e pela Class_2 — Electricity generation
                       aqui, Carbon storage lá.
  'Não Alocado'        grafia do próprio SEEG. Só a id 65 tinha, e só para a
                       rota alcohol-to-jet (5,2 TWh de SAF em 2050), modelada
                       como um ativo único nacional sem UF — essas 12 linhas
                       saíram do recorte espacial na correção de Territory (a
                       linha BR continua contando o valor). Nas demais não há
                       nada em Não Alocado.

TODA A EXPANSÃO DE GÁS E DE NUCLEAR ENTRA EM SÃO PAULO — como o modelo foi
montado, não como resultado de otimização locacional. Fato estrutural, para
quem for ler o mapa estadual:

O parque EXISTENTE está discretizado por UF. São 26 ativos BR_<UF>_..._Existing,
cada um com can_expand = False e nó no seu estado, com a distribuição real de
2025: RJ 7,71 GW, MA 3,20, SE 1,59, AM 0,76, CE e PE 0,55, MT 0,53, PR 0,48 e
SP apenas 0,65 GW.

A EXPANSÃO, porém, tem um único candidato nacional por tecnologia —
BR_Combined_Cycle, BR_Simple_Cycle, BR_Combined_Cycle_CCS, BR_Nuclear_Modular e
BR_Nuclear_Large. Todos têm location = BR, mas end_vertex = elec_BR_SP (e o CCS
captura em co2_captured_BR_SP). Nenhum outro estado tem candidato com
can_expand = True.

Resultado: o parque existente encolhe de 18,2 GW (2025) para 6,7 GW (2050)
espalhado pelas UFs, enquanto os 30,9 GW de capacidade nova de 2050 nascem
todos em São Paulo. Na id 66 isso aparece como SP com 30,94 GW de gás e todos
os demais estados com zero de expansão; na id 68, como 36,1 dos 47,8 TWh
gerados a gás. Na id 55 o gás não tem linha estadual nenhuma, justamente por
ser um ativo nacional único.

O total nacional não é afetado — capacidade e geração de gás estão corretas
independentemente da localização. O que fica condicionado é o recorte estadual
dessas duas variáveis, e por tabela a necessidade de transmissão e o duto de
CO2, que são calculados a partir do nó de SP. O nuclear tem o mesmo desenho,
mas não foi construído neste cenário.

Em verificação com a equipe de modelagem se é simplificação deliberada — o que
seria coerente com um modelo que já usa hubs regionais — ou lacuna de
candidatos.

"""

NOTAS[24] = """id 24 — Total energy system cost

Fonte: results_period_<p>/results_period_<p>/costs.csv está no caminho aninhado
(pasta repetida dentro dela mesma) e o arquivo usado é o costs_by_type.csv.

Composição: Investment + FixedOM + VariableOM + Supply, menos o Supply de
gasolina, diesel e querosene fóssil. Equivale a Total menos NonServedDemand
menos os três Supply fósseis.

NÃO ANUALIZADO. O valor é o presente do quinquênio inteiro, descontado a 2025 a
4,5% a.a. Por isso a série cai de 231,2 para 117,5 bi US$ entre 2025 e 2050 —
boa parte da queda é desconto, não barateamento. A série anualizada (dividindo
pelo fator de anuidade do período) fica praticamente plana; a função
annuity_factor() está em comum.py, desligada, caso a plataforma peça.

O DiscountedTotalCost inclui as anuidades de investimentos que se estendem além
da janela míope de cada período. Ou seja, não é o valor que o solver minimizou.
Para um indicador de custo de sistema é defensável incluir, mas não reconcilia
com o objective_value.csv.
"""

NOTAS[26] = """id 26 — Energy supply investments by type

Mesma fonte da 24, filtrando category == 'Investment' e descartando a linha
agregada 'Total'. A soma por ano bate com Total,Investment nos seis períodos.

NUNCA endereçar o costs_by_type.csv por número de linha: o conjunto de
tecnologias muda de período para período (96 linhas no período 1, 108 no 6),
então a linha 103 de um período é outra coisa no seguinte.

Três decisões registradas:

1. Tipos ausentes num período entram com 0 para fechar as seis linhas de cada
   série (2025 tem 22 tipos, os demais 26).
2. OneWayTransmissionLink{NaturalGas} foi descartado: 0,0 nos seis períodos.
3. VRE{Generic} AGREGA solar, eólica e rooftop num tipo só, e é o maior item de
   investimento do horizonte (2,25 / 17,34 / 20,16 bi US$ em 2025/2030/2035).
   Se a plataforma precisar de solar e eólica separadas, esta variável tem que
   vir do capex.csv por ativo, não do costs_by_type.

Os nomes em Class_2 ainda são as strings do Julia (ThermalPowerCCS{NaturalGas},
OneWayTransmissionLink{CO2Captured}). O dicionário ROTULO em var_26.py está
vazio esperando a nomenclatura da plataforma.
"""

NOTAS[27] = """id 27 — Demand side energy capital

RECEITA: custo de suprimento ('Supply' no costs_by_type.csv) dos quatro nós de
combustível fóssil de uso final — Node{NaturalGas}, Node{MacroEnergy.Gasoline},
Node{MacroEnergy.JetFuel_Fossil} e Node{MacroEnergy.Diesel}.

    ano    diesel  gasolina  querosene   gás     total   (bilhões de US$)
    2025    154,4     42,1       17,1    32,9    246,5
    2030    100,9     35,0       11,7    25,7    173,3
    2035     69,5     23,3        8,4    19,8    120,9
    2040     50,3     12,6        6,2    16,9     86,0
    2045     36,0      4,9        4,7    13,5     59,0
    2050     25,5      1,5        3,5     8,6     39,0

A linha 'Total' vem junto no arquivo, com Class_4 = 'Total'. Somar Value sem
filtrar Class_4 dobra o resultado.

VALOR DESCONTADO, como o da id 24: presente do quinquênio no ano-base, a 4,5%
ao ano. Não anualizado.

A CATEGORIA 'NonServedDemand' DOS MESMOS NÓS FICA DE FORA. É penalidade de não
atendimento, não custo de combustível. Recontada em 01/09/2026: 3,23 M US$ em
2025 e depois 0,15 / 0,20 / 0,13 / 0,21 / 1,19 — NÃO é zero nos demais períodos,
como esta nota dizia. Continua desprezível (o maior valor é 0,002% do Supply de
diesel de 2025) e a decisão de deixar fora segue valendo.

NÃO É COMPLEMENTAR DA id 24, E ISSO É DE PROPÓSITO. A 24 subtrai do total os
Supply de gasolina, diesel e querosene fóssil — os mesmos três daqui — mas NÃO
o de gás natural, que a 27 inclui. NUNCA SOMAR AS DUAS: o Supply de gás natural
entra nas duas e seria contado em dobro (32,9 bi US$ em 2025, 14,2% da id 24;
8,6 bi em 2050, 7,3%).

A assimetria tem razão de ser, verificada em 01/09/2026. Gasolina, diesel e
querosene vão praticamente 100% para uso final, então deixar o custo deles na
24 colocaria despesa de demanda dentro do custo do sistema. O gás natural não:
em 2050, dos 246,2 TWh consumidos, 133,3 (54%) vão para uso final e 112,9 (46%)
para geração térmica e produção de hidrogênio — custo que é do sistema de
oferta e pertence à 24. Subtrair o gás inteiro de lá subestimaria o custo do
sistema em algo perto dessa metade.

Se um dia se quiser que as duas sejam complementares, o corte certo não é tirar
o gás inteiro da 24: é tirar só a parcela de uso final (54% em 2050), o que
exige uma separação que a receita atual não faz.

O NOME DA VARIÁVEL NÃO DESCREVE O QUE ESTÁ AQUI. 'Demand side energy capital'
é, na planilha da plataforma, o estoque de capital de uso final — veículos,
motores, equipamentos — e a fonte prevista é o Energy Pathways, não o MACRO. O
que esta receita entrega é DESPESA COM COMBUSTÍVEL FÓSSIL, um fluxo operacional
anual, não um estoque de capital. Os dois números não são substituíveis um pelo
outro e a diferença precisa ficar clara no card, senão a série vai ser lida
como investimento em equipamento de uso final.
"""

NOTAS[55] = """id 55 — Primary energy supply by source

AGREGAÇÃO COMO A MATRIZ ENERGÉTICA DO BEN, não como o SEEG:

    Class_1  Renewable / Non-renewable
    Class_2  fonte do BEN — Oil and oil products, Natural gas, Mineral coal,
             Uranium, Hydraulic, Wind, Solar, Sugarcane biomass, Firewood and
             charcoal, Other renewables
    Class_3  detalhe do MACRO dentro da fonte, ou N/A quando a fonte não se
             abre

RECORTE ESPACIAL (decidido em 01/09/2026): sai o nacional e o espacial no
mesmo arquivo, mas só as fontes que têm unidade espacial no modelo ganham
linha própria.

    biomassa                 UF, 27 estados (nós sugarcane_BR_SP e afins)
    solar e eólica           UF, pelo prefixo do resource_id
    hidráulica               BACIA, as 15 do modelo — as usinas não têm UF
    fósseis e urânio         SÓ NACIONAL, sem linha estadual

Não há 'Não Alocado' nesta variável, por decisão da equipe: o que é nacional
aparece só como BR. Diesel, gasolina, querosene, gás natural, carvão e urânio
são um ativo único do país no modelo. No caso do gás, a ligação ao nó de São
Paulo que aparece nas ids 66 e 68 é só o ponto de maior demanda, não uma
localização — aqui essa ambiguidade não existe porque não há linha estadual.

Conferido: a soma das linhas espaciais bate com a linha BR em todas as fontes
que têm recorte, diferença máxima de 3e-05 GWh.

TRÊS FONTES SEM ABERTURA na Class_3, por decisão da equipe: carvão mineral
(nacional e importado somados — o BEN não separa a origem na matriz e a
plataforma não pediu), hidráulica (reservatório e fio d'água somados) e gás
natural (só existe o fóssil no modelo, não há o que distinguir). Os nós
continuam separados no MACRO; o que mudou foi a apresentação.

Como é lida: não existe linha de 'supply' no flows.csv, só arestas de ativos. A
oferta primária vem do SALDO LÍQUIDO dos nós de recurso — o que sai de
sugarcane_BR_SP, natgas_fossil_BR, uranium_BR e assim por diante.

TRÊS CONVENÇÕES CONFERIDAS CONTRA O BEN:

1. HIDRÁULICA, EÓLICA E SOLAR usam CONTEÚDO FÍSICO — a energia primária é a
   própria geração. É o que o BEN faz hoje: a matriz de 2024 traz hidráulica em
   11,6% da OIE, o que a 0,086 tep/MWh (1 kWh = 860 kcal) reproduz a geração
   hidrelétrica do ano. A nota técnica COBEN-09 descreve um critério antigo de
   equivalente de substituição a 0,29 tep/MWh, 3,62 vezes maior, que não é o
   que a matriz publicada usa.

2. URÂNIO NÃO PRECISA DE CONVERSÃO. O BEN não tem fator tonelada de U3O8 -> tep:
   ele calcula a energia primária nuclear dividindo a geração elétrica por 33%,
   o rendimento térmico das centrais. O nó uranium_BR do MACRO já é energia
   TÉRMICA de entrada no reator, não urânio físico — conferido nos seis
   períodos, a razão entre geração nuclear e urânio ofertado é 32,5% constante
   (13,09/40,25 em 2025, 16,59/51,04 em 2050). Ou seja, o valor que já
   reportamos é a energia primária do urânio na convenção do BEN, com 1,5% de
   diferença para os 33% — coincidentemente a mesma perda que o BEN aplica na
   conversão de U3O8 para UO2.

3. SOJA FORA. No BEN o óleo de soja é fonte SECUNDÁRIA, não primária. A linha
   foi removida (eram 40,8 Mt em 2025 e 0,07 Mt em 2050).

PALHA DE CANA TAMBÉM FORA, por outro motivo: ela não tem nó de oferta própria no
modelo, é coproduto do BiomassTransformation_coprod a 0,048 t por tonelada de
cana. Contá-la junto com a cana duplicaria a mesma biomassa. Palha de milho e
palha de arroz, ao contrário, têm curva de oferta própria e entram em Other
renewables.

BIOMASSA CONVERTIDA PARA ENERGIA, EM PCS. As commodities de biomassa do modelo
estão em TONELADAS e as demais fontes em MWh. Para a variável fechar como matriz
energética a biomassa é convertida por um poder calorífico, na tabela do topo de
var_55.py. Conversão: MWh/t = kcal/kg / 860 (1 kWh = 860 kcal, o mesmo
coeficiente que o BEN usa para eletricidade).

    fonte                     PCI   umidade    PCS   MWh/t (PCS)
    Cana-de-açúcar           1060      70%    1577      1,834
    Lenha / floresta plant.  3100      25%    3493      4,062
    Resíduo florestal        3100      25%    3493      4,062
    Milho (grão)             3800      14%    4163      4,840
    Palha de milho           3500      15%    3865      4,495
    Palha de arroz           3300      12%    3657      4,252
    Macaúba (fruto)          3500      25%    3893      4,527

A base é PCS por decisão do projeto; BASE = "PCI" no código devolve a inferior.
O PCS é DERIVADO do PCI pela relação usual PCS = PCI + 600 x (9H + W), com 6% de
hidrogênio na matéria seca e a umidade da tabela. São valores calculados, não
medidos.

DE ONDE VÊM OS PCI: só o da cana é do BEN — 1060 kcal/kg para o colmo integral
em base úmida, no anexo de unidades do Balanço, que também traz caldo a 620 e
melaço a 1.930. Os outros seis são de literatura. O Anexo VIII completo não foi
possível abrir pelas ferramentas disponíveis. Substituir pela tabela da equipe.

ATENÇÃO — O LADO FÓSSIL DO MACRO ESTÁ EM PCI, NÃO EM PCS. Os emission_rate dos
ativos de uso final reproduzem o fator de emissão dos combustíveis na base
INFERIOR, com desvio de 0,3% a 1,4%; na base superior o desvio seria de 5,5% a
9,4%:

    combustível    tCO2/MWh em PCI   em PCS   emission_rate do modelo
    Diesel               0,268        0,250          0,271
    Gasolina             0,256        0,239          0,257
    Querosene            0,264        0,247          0,260
    Gás natural          0,206        0,186          0,204

Converter a biomassa em PCS e deixar o fóssil como o modelo o grava mistura duas
bases na mesma matriz: a biomassa fica cerca de 10% mais pesada do que ficaria
na base do resto da variável, e a cana 49% mais pesada (1,834 contra 1,233
MWh/t, por causa dos 70% de umidade).

DECISÃO TOMADA: a inconsistência foi ACEITA nesta versão e está no backlog de
melhorias da próxima. Não é um erro por descobrir — é uma escolha registrada.
A correção é uma linha: ou BASE = "PCI" aqui, e a biomassa volta para a base do
fóssil, ou os emission_rate do modelo passam para PCS.

A MATRIZ RESULTANTE, COMPARADA À DO BEN 2024:

                          modelo 2025    BEN 2024
    Petróleo e derivados      37,3%        34,0%
    Gás natural                9,4%         9,6%
    Carvão mineral             2,6%         4,5%
    Urânio                     1,9%         1,3%
    Hidráulica                17,8%        11,6%
    Eólica                     3,7%         2,9%
    Solar                      2,5%         2,2%
    Biomassa da cana           1,3%        16,7%   <-- ver abaixo
    Lenha e carvão vegetal     7,7%         8,5%
    Outras renováveis         15,7%         8,1%
    ---------------------------------------------
    renovável                 48,7%        50,0%

Sete das dez fontes ficam próximas e o total renovável fica a 1,3 ponto. A
BIOMASSA DA CANA é o desvio grande: 1,3% contra 16,7%. O modelo consome 15,3 Mt
de cana em 2025, contra as cerca de 600 Mt que o Brasil moe — é a mesma inversão
milho/cana descrita na nota da id 65, agora medida em participação na matriz. E
'Outras renováveis' aparece inflada (15,7% contra 8,1%) pelo mesmo motivo, do
outro lado: 66,6 Mt de milho em 2025.

A oferta interna total do modelo é 2.116 TWh em 2025, ou 182 Mtep, contra cerca
de 316 Mtep da OIE brasileira real. O MACRO não cobre usos não-energéticos nem
toda a demanda industrial, então a matriz aqui é de um recorte do sistema, não
do país inteiro — as participações são internamente consistentes, mas não
comparáveis linha a linha com o BEN em valor absoluto.

'Oil and oil products' são diesel, gasolina e querosene FÓSSEIS entrando no
sistema já refinados — o modelo não tem petróleo bruto como commodity, então
não há uma linha de petróleo primário. Para a plataforma isso significa que a
oferta primária de petróleo aparece desagregada em derivados, e não é
diretamente comparável ao 'Petróleo e derivados' do BEN.

O gás natural de 2025 (199,3 TWh) é a entrada real. Não confundir com os
3.662 TWh que aparecem circulando no UpstreamEmissions{NaturalGas} naquele ano:
esse ativo tem as duas arestas no mesmo nó natgas_BR e forma um laço fechado,
que a um emission_rate de 0,045 gera os 164,8 Mt de CO2 espúrios da id 18. Em
2050 o laço é de 0,03 TWh.

CUIDADO COM O SINAL AO REFAZER ESTA CONTA. O flows.csv mistura duas convenções:
numa aresta de ativo o value já é a contribuição ao nó (positivo entra, negativo
o ativo puxa), mas numa linha de transmissão, em que as duas pontas são nós, o
value é direcional — sai de node_in e entra em node_out. Tratar as duas igual
inverte o sinal de todo nó ligado por transmissão: o natgas_fossil_BR aparece
como sumidouro de 245,8 TWh em vez de fonte. A função comum.saldo_nos separa os
dois casos.
"""

NOTAS[56] = """id 56 — Energy demand

NOME: 'Energy demand', como na aba 'Platform outputs' (mudou em 01/09/2026;
antes 'Energy end-use by energy carrier'). O recorte por portador continua
sendo o que a variável entrega.

O QUE ESTA VARIÁVEL É: consumo final de energia por portador. Toda a energia
entregue ao consumidor, um portador por vez. A abertura da eletricidade entre
uso intermediário e final NÃO é mais publicada — era a antiga id 57, que saiu do
pacote em 02/09/2026 porque o número foi reatribuído à frota rodoviária do
Transport (ver a nota de numeração).

COMBUSTÍVEIS: demanda final = saldo NEGATIVO dos nós de demanda. Usar a
fuel_demand_edge do GeneralFuelsEndUse, como sugere a Tab8, não serve: o diesel
fóssil chega ao nó de demanda pelo UpstreamEmissions e não pelo Downstream, e
ficariam de fora 596 dos 596,3 TWh de 2050.

ELETRICIDADE: saldo dos nós elec_BR_<UF>. São 1.206,7 TWh em 2050, contra
1.192,6 TWh de demanda exógena no elec_demand_2050.csv — a diferença é o
round-trip da bateria, que o saldo do nó carrega. A medição é na CHEGADA ao
consumidor, já líquida das perdas de transmissão (17,9 TWh em 2050). Medida na
barra de geração daria 1.221,0 TWh; a geração total da id 68 é 1.244,0, e a
diferença para os 1.206,7 daqui são perdas mais o round-trip. As três
convenções são coerentes entre si e não devem ser comparadas linha a linha.

O CONSUMO INTERMEDIÁRIO JÁ VEM DESCONTADO nos demais portadores, porque o nó de
demanda é final por construção. O hidrogênio, por exemplo, aparece com 6,04 TWh
em 2050, que é a produção de 9,26 menos os 3,22 consumidos por sintéticos e
termelétrica. Para a eletricidade isso não vale — o valor do nó elétrico inclui
o que a eletrólise, o DAC e o BECCS consomem (3,25 TWh em 2050, 0,3% do total);
esse recorte deixou de ser publicado com a saída da antiga id 57.

NÃO HÁ CARVÃO MINERAL NESTA VARIÁVEL, E NÃO PODE HAVER. O modelo não tem nó de
demanda de carvão: `coal_BR` e `coal_imported` são fontes e alimentam só
termelétrica (54,6 TWh em 2025, 0,6 em 2050). No BEN, carvão e coque são consumo
FINAL relevante da indústria. Quem comparar esta variável com a tabela de
consumo final do BEN vai achar que falta carvão — ele está dentro do bloco
exógeno da id 18, não aqui. A mesma coisa vale para qualquer energético cujo uso
final o MACRO não modele.

O NÓ elec_proxy NÃO ENTRA, e é o quinto lugar por onde a eletricidade some. São
os hubs de subsistema (NE, SE, S, N e IMP), onde hidrelétrica e fio d'água
injetam e a transmissão leva para os nós estaduais. O saldo deles é negativo em
11,8 TWh em 2050 (NE 5,05, SE 4,87, IMP 0,91, S 0,65, N 0,32) — é perda de
transmissão no hub, não demanda, e por isso fica fora. Somando: da geração de
1.244,0 TWh chegam 1.206,7 TWh aos nós estaduais.

RECORTE POR ESTADO, ligado em 01/09/2026. A aba pede 'national, state' e dois
portadores têm nó estadual no modelo: ELETRICIDADE (elec_BR_<UF>) e HIDROGÊNIO
(h2_BR_<UF>), 27 nós cada. Os outros sete portadores são um nó nacional único —
diesel, gasolina, querosene, gás natural, etanol, flexfuel e carvão vegetal — e
continuam saindo só na linha BR, exatamente como os fósseis da id 55. O arquivo
traz o nacional E o estadual: somar Value sem filtrar Territory dobra a
eletricidade e o hidrogênio. Conferido: a soma das UFs bate com a linha BR com
diferença máxima de 3e-05 GWh.

Concentração em 2050 — eletricidade: SP 361,4 TWh, MG 130,2, RJ 99,8, PR 81,1,
RS 66,7. Hidrogênio: SP 2,88 TWh de 6,04, quase metade do país.

RESOLUÇÃO TEMPORAL: a aba pede 1-year para esta variável — é a ÚNICA do MACRO em
que ela pede anual, todas as outras são 5-year. O modelo é quinquenal e não tem
como entregar. Registrado para a equipe da plataforma decidir se interpola ou se
aceita a grade de cinco em cinco.

'AND END USE' NÃO ESTÁ DISPONÍVEL. O nome da variável na planilha da plataforma
pede o recorte por uso final, mas o MACRO agrega a demanda num nó por
combustível — não existe separação por setor (transportes, indústria,
residencial, comercial). Por isso Class_2 vai como N/A. É a mesma limitação que
aparece na id 18.

AGRUPADA POR PORTADOR. Uma linha por portador e por ano, Class_5 = N/A. Os nós
de mandato (biodiesel_mandate, jetfuel_fossil_mandate, jetfuel_SAF_mandate)
entram somados ao portador correspondente: o biodiesel obrigatório vira Diesel,
os três nós de querosene viram Jet fuel. São doze nós de demanda em nove
portadores. Para recuperar a abertura por instrumento basta devolver o terceiro
campo da lista PORTADORES em var_56.py — a informação continua no modelo.

Efeito no número: nenhum. O total por portador é o mesmo; o que sumiu foi a
linha separada de 'Biodiesel mandate' (180,2 TWh em 2050, agora dentro dos
776,5 de Diesel) e as três de querosene (21,0 + 26,2 + 5,2, agora 52,4 de Jet
fuel).
"""

NOTAS[65] = """id 65 — Biofuels, synthesized fuels and hydrogen production by technology

Regra de extração: a Tab8 sugere filtrar por commodity ('ethanol', 'biodiesel',
'green_diesel'...), mas essas commodities NÃO EXISTEM no modelo. Diesel
renovável, biodiesel e HVO são todos commodity 'Diesel'; SNG é 'NaturalGas'.
Quem identifica o produto é o nó de destino, que o modelo já separa do fóssil
(renewable_diesel_BR vs diesel_BR, natgas_nonfossil_BR vs natgas_BR).

ESTRUTURA DE CLASSES segue o padrão da planilha ethanol_flows, com produto,
matéria-prima e tecnologia como dimensões separadas:

    Class_3 = produto        Hydrous ethanol, Biodiesel, Charcoal, Hydrogen...
    Class_4 = matéria-prima  Sugarcane, Corn, Lignocellulosic, Macauba, Wood...
    Class_5 = tecnologia     1G, 1G2G, 2G, FAME, HEFA, Alcohol-to-jet,
                             Fischer-Tropsch, Gasification, Electrolysis...
                             com o CCS embutido no nome ('1G with CCS')

Isso substituiu a sub-categoria do SEEG que ocupava a Class_3 na versão
anterior. A troca vale a pena: a sub-categoria só existia para dois dos oito
produtos ('Produção de álcool' e 'Produção de carvão vegetal') e ia como N/A nos
outros seis, porque o SEEG reporta a EMISSÃO da produção desses combustíveis e
nunca a produção em si. A matéria-prima, ao contrário, existe para todos.

O CCS ficou dentro da tecnologia por falta de slot — as cinco classes já estão
todas ocupadas. Para filtrar por CCS, procurar 'with CCS' na Class_5.

Três ressalvas:

1. PRODUÇÃO BRUTA. O reuso interno não está descontado: etanol consumido pelo
   ATJ (7,6 TWh em 2050) e H2 consumido por sintéticos e termelétrica (3,2 TWh,
   dos quais 2,8 queimados para gerar eletricidade, que é uso elétrico e não
   combustível final). Se a plataforma somar as linhas para um total de
   combustíveis não-fósseis, precisa ser líquido.
2. HIDROGÊNIO DE GÁS NATURAL ENTRA. O SMR aparece com o nome completo na
   Class_5. É H2 fóssil dentro de uma variável chamada 'non-fossil': em 2025
   são 6,5 dos 7,5 TWh de hidrogênio, e ainda 5,9 de 6,6 em 2045.
3. Dois resultados esquisitos que a equipe de modelagem já está investigando e
   que se refletem aqui: em 2025 o etanol de MILHO (184,4 TWh) supera o de CANA
   (8,3 TWh), inverso do Brasil real; e o biodiesel salta de soja para macaúba
   integralmente entre 2025 e 2030, porque o ativo Macauba_FAME não existe em
   assets_2025 e a curva de oferta de macaúba dá 168 Mt/ano disponíveis já no
   primeiro ano, sem rampa.

A ROTA ALCOHOL-TO-JET NÃO TEM ESTADO, E ISSO ESVAZIA O MAPA DO SAF (achado de
01/09/2026). Os dois ativos da rota são NACIONAIS no modelo — BR_ATJ_ethanol e
BR_ATJ_Diesel, sem segmento de UF no resource_id — então aparecem só na linha
BR, como os fósseis da id 55. A produção deles, em GWh:

    ano             2025      2030      2035      2040      2045      2050
    BR_ATJ_ethanol   0,8   1.299,7   3.724,7   4.899,1   5.041,9   5.162,0
    BR_ATJ_Diesel   22,9       0,6       1,9       2,0       1,6       6,4

CONSEQUÊNCIA: em 2050 o ATJ é 5.162 dos 5.200 GWh de SAF do país, 99,3%. A linha
BR de Sustainable aviation fuel traz os 5,2 TWh, mas a SOMA DAS UFs desse
produto dá quase zero. Um mapa estadual de SAF sai praticamente vazio, e não é
erro de dado: é o modelo que não localiza essa planta. O mesmo vale, em escala
irrelevante, para o diesel renovável (6,4 de 200 GWh em 2050; em 2025 eram 22,9
de 26,7, quase tudo).

Para todos os outros produtos a soma das UFs bate com a linha BR na terceira
casa.
"""

NOTAS[66] = """id 66 — Power installed capacity (era "Installed capacity by type"; renomeada a pedido do David, 09/09/2026)

'capacity' é ESTOQUE, não adição: conferido nos seis períodos que
capacity(t) = capacity(t-1) + new_capacity - retired_capacity, sem resíduo.
(existing_capacity só é gravado no período 1, 187,64 GW.)

Três armadilhas do capacity.csv que o código trata:

1. HydroRes aparece DUAS vezes com valor idêntico (discharge_edge e
   inflow_edge). Somar as duas dobra a hidrelétrica de reservatório, de 41,3
   para 82,6 GW. Só o discharge entra.
2. component_type 'Storage{Electricity}' é ENERGIA (GWh), não potência —
   bateria 39,7 GWh e reservatório 145.330 GWh. Fica fora; é outra variável.
3. Linhas de transmissão têm capacidade em MW mas não são geração.

LACUNA CONHECIDA: NÃO HÁ BIOELETRICIDADE nesta variável. No capacity.csv o
BECCSElectricity tem capacidade na biomass_edge, isto é, MW de biomassa de
ENTRADA, não MW elétricos (23,45 GW de lenha + 3,70 de resíduo em 2050); e o
BECCSEthanolv2 coproduz eletricidade sem nenhuma capacidade associada. Na id 68
essas duas rotas geram 172 e 35 TWh em 2050 — 14% da matriz. Quem cruzar 66 com
68 vai ver 14% da geração sem parque instalado. Precisa de decisão antes de
publicar: deixar de fora (é o que está), entrar com a capacidade de entrada
rotulada como tal, ou derivar a elétrica pela eficiência.

Dois pontos que parecem bug e não são: a hidráulica fica constante em 100,6 GW
nos seis períodos (premissa de expansão só dentro do potencial inventariado); e
as classes de recurso (Solar_Class0..3, Wind_Onshore_Class0..3) foram agregadas
em utility-scale e onshore — dá para abrir se a plataforma quiser.

Referência de ordem de grandeza: 192,8 GW em 2025 contra ~200 GW reais.
"""

NOTAS[67] = """id 67 — Solar, wind and battery capacity additions

Mesma fonte da 66, com variable == 'new_capacity'.

UNIDADE: o valor é a adição do QUINQUÊNIO INTEIRO, em GW, sem nenhuma conta
feita. A variável se chama 'average annual additions' na planilha da
plataforma, e a Tab8 pede para interpolar para valores anuais, mas dividir por
5 contradiz a resolução temporal declarada de 5 anos — decisão pendente com a
equipe. A flag MEDIA_ANUAL em var_67.py faz a divisão e troca a unidade para
GW/year.

ADIÇÃO BRUTA: new_capacity não desconta retired_capacity. No horizonte só pesa
em 2050 (eólica onshore aposenta 1,72 GW, exatamente o que foi construído em
2025) e em 2035 (bateria, 0,26 GW). Fechamento conferido: estoque 2025 dos três
tipos 68,77 GW + adições 2030-2050 183,38 - aposentadorias 2,24 = 249,91 GW,
idêntico ao estoque de 2050 da id 66.

A eólica é serrilhada: 21,2 GW em 2035, 3,3 em 2040, 21,4 em 2045. É artefato
do myopic — cada período otimiza isolado e o modelo alterna entre solar e
eólica conforme o limite de transmissão da janela. Dividir por 5 suaviza a
escala, não o serrilhado.
"""

NOTAS[68] = """id 68 — Power generation by type

Geração = fluxo positivo de Electricity entrando num nó elétrico (node_out
começa com 'elec_'), de ativo que não seja linha de transmissão. Esse filtro
resolve sozinho os três casos que a Tab8 trata à mão:

- HydroRes tem discharge_edge (geração), inflow_edge (negativo, é água) e
  spill_edge (positivo, 21,6 TWh em 2050, mas vai para hydro_source_*, é
  vertimento). Só o discharge tem nó elétrico de destino.
- Transmissão move energia já gerada; contá-la duplicaria 795 TWh em 2050.
- Consumo (eletrólise, DAC, carga de bateria) é negativo e cai fora.

BATERIA NÃO É GERAÇÃO. Entra como Class_5 = 'Discharge' seguindo a Tab8
('including batteries'), mas é devolução de estoque: a carga consumiu 22,3 TWh
para devolver 19,7 em 2050. Somar essa linha num total de geração conta a mesma
energia duas vezes e infla ~1,6%. Totais: 1.244,0 TWh com bateria, 1.224,3 sem,
em 2050.

A fio d'água é 200,12 TWh nos seis períodos, sem uma casa decimal de diferença —
consequência de ser MustRun com capacidade fixa, não bug.

Referência de ordem de grandeza: 581 TWh em 2025 contra ~730 TWh reais do SIN
em 2024, com a maior parte da diferença na hidráulica (375,8 contra ~430).

Ver também a lacuna de bioeletricidade descrita na nota da id 66: ela aparece
aqui (172 TWh em 2050) e não aparece lá.
"""

NOTAS[69] = """id 69 — Renewable power area by type (wind and solar)

ESTA VARIÁVEL NÃO É RESULTADO DO MODELO. Ela é a capacidade instalada da id 66
dividida por uma densidade de potência que NÃO existe no input do MACRO. As
densidades são premissa fornecida pela equipe:

    solar utility-scale   33,0 MW/km2   (equivale a 3,0 ha/MW)
    eólica                 5,3 MW/km2   (equivale a 18,9 ha/MW)

São MW, não MWh — densidade de potência instalada por área, não de energia
gerada. Estão em DENSIDADE, no topo de var_69.py; mudar lá é o único jeito de
mudar esta variável.

ROOFTOP FICA DE FORA por definição, não por falta de dado: painel em telhado não
ocupa solo. São 7,1 GW constantes no horizonte, que apareceriam como 0,21 Mha
inexistentes se entrassem com a densidade de solo.

EÓLICA OFFSHORE usa a mesma densidade da onshore, mas a área é MARÍTIMA e não
terrestre. No cenário é irrelevante (0,01 GW em 2050, ou 19 ha), mas se a
plataforma somar tudo numa métrica de uso do solo, a linha precisa sair.

A DENSIDADE EÓLICA É DE ÁREA DE PROJETO, não de solo efetivamente ocupado. Os
5,3 MW/km2 correspondem ao polígono do parque inteiro, dentro do qual a base
das torres, as vias de acesso e as subestações ocupam tipicamente de 1% a 3%.
Lavoura e pastagem continuam dentro do polígono. Se a plataforma for usar esta
variável numa conta de competição por terra, ela superestima o conflito por uma
ordem de grandeza. A solar utility-scale é o oposto: os 33 MW/km2 são área
praticamente exclusiva.

ABERTURA POR ESTADO, ligada em 01/09/2026. A aba 'Platform outputs' pede
'state level map' para esta variável e a UF sai direto da zona do capacity.csv.
O arquivo traz o nacional (Territory = BR) E as 26 UFs — somar Value sem
filtrar Territory dobra o resultado. Conferido: a soma das UFs bate com a linha
BR com diferença máxima de 2e-06 Mha.

A ABERTURA MUDA A LEITURA DA VARIÁVEL. A eólica é extremamente concentrada: em
2050, o Rio Grande do Norte sozinho tem 1,319 das 2,120 Mha onshore do país,
62%; depois vêm Pernambuco com 0,307 e Bahia com 0,224. O número nacional
esconde isso. A solar utility-scale é bem mais distribuída — São Paulo lidera
com 0,101 das 0,335 Mha.

Ordem de grandeza para contexto: 2,46 Mha em 2050 são cerca de 0,9% da área
agropecuária brasileira. Para comparar dentro do próprio cenário, as 586 Mt de
cana da id 55 correspondem a algo entre 7 e 8 Mha a produtividades usuais — ou
seja, a expansão de solar e eólica pesa cerca de um terço do que pesa a cana
para o etanol, em área.
"""

NOTAS[70] = """id 70 — Transmission lines

REPORTA CAPACIDADE, NÃO km. A planilha da plataforma pede km, mas o input traz
a nota "cost values are placeholders, distance for record-purpose only" e o
investment_cost é idêntico nos 31 corredores, de 136 a 1.807 km — a distância
não entra na otimização. A capacidade, sim, é decisão do modelo.

    ano    capacidade    da qual nova no período
    2025      152,8            57,5
    2030      166,4            13,6
    2035      198,8            32,4
    2040      205,6             6,8
    2045      228,1            22,4
    2050      252,0            24,0     (GW)

Nada se aposenta em nenhum período. A unidade da variável muda de km para GW —
a plataforma precisa saber disso antes de rotular o eixo.

SUBSISTEMA POR EXTENSO, ESTADO POR SIGLA: 'Nordeste–Sudeste' é a interligação
entre os dois subsistemas (31,2 GW em 2050) e 'Nordeste–SE' é a perna que
alimenta Sergipe (1,0 GW). As duas existem, e os ids do modelo só se distinguem
pelo prefixo BR_ da ponta — testar a sigla juntava as duas num rótulo só.

SÓ OS CORREDORES, SEM LINHA NACIONAL (01/09/2026). O corredor vai na Class_3 —
antes era o Territory, que o padrão restringe a BR ou UF — e o Territory de
todos é BR. Como a linha nacional ficaria indistinguível das partes e dobraria
a soma, ela foi retirada: os 35 corredores somam o total do país (252,0 GW em
2050). O tipo de corredor continua na Class_5 (Interregional, Subsystem to
state, Interstate).

A UNIDADE DE CONTAGEM É O SENTIDO, NÃO A LINHA FÍSICA (decidido em
01/09/2026). Quatro dos 35 corredores são links de sentido único, e dois deles
são as duas pontas da MESMA interligação, com limites diferentes por sentido:
Sul→Sudeste 8,00 GW e Sudeste→Sul 11,46 GW em 2050. Os dois entram como
corredores separados e o total soma ambos — 19,47 GW nessa interligação, 252,0
GW no país. É a leitura correta para esta variável: o limite assimétrico é real
(o ONS publica limites de importação e exportação diferentes) e o que se está
medindo é capacidade de transferência por sentido. Quem quiser contar
infraestrutura física, e não sentido, precisa tomar o maior de cada par e chega
a 244,0 GW — não é o número publicado. Os outros dois links de sentido único,
Itaipu→Sudeste (10 GW) e Belo Monte→Sudeste (8 GW), são escoamento de geração e
não têm par.

RESSALVA DO ESTOQUE INICIAL: a nota do input diz "SOME existing capacity values
are placeholders", e dá para ver quais. Os 25 corredores subsistema–estado e os
dois interestaduais (AC–RO, RO–MT) têm existing_capacity de exatamente 1.000 MW
cada — 27 corredores, 27,0 dos 95,3 GW de 2025, ou 28% do estoque inicial. Os demais são
plausíveis: Itaipu–SE 10.000, Belo Monte–SE 8.000, SE–S 11.450 e S–SE 8.000,
NE–SE 9.911, e as três pernas do hub IMP com 5.700, 6.089 e 9.107 MW. Em 2050 o
placeholder cai para 10% do estoque, porque o resto é expansão otimizada — mas
os corredores de 1.000 MW seguem com o piso errado o horizonte inteiro.

'IMP' NÃO É UM SUBSISTEMA. É nó de trânsito: N e NE despacham para dentro dele
(16,1 e 12,2 TWh em 2050) e o SE puxa de lá (27,4 TWh). Os corredores N–IMP,
NE–IMP e SE–IMP juntos são a interligação Norte/Nordeste–Sudeste; lidos um a um
não têm equivalente na rede real e não devem virar linha de mapa.

SUDESTE–SUL APARECE DUAS VEZES, uma por sentido (11.464 e 8.003 MW em 2050), porque o
modelo usa dois OneWayTransmissionLink para a mesma interligação física. O
total nacional soma os dois — certo para 'capacidade de transporte instalada',
errado para 'quantos corredores existem'.
"""

NOTAS[71] = """id 71 — Oil production

O card 32 oferece três cenários de produção de petróleo. Até 02/09/2026 só o
C saía desta variável — em A (Expansion, PNE 2050) e B (Current policies, PDE
2034) a trajetória é exógena e quem reportava era o EnergyPathways. Em
02/09/2026 a equipe pediu para os três saírem juntos daqui, com A e B sempre
emitidos (independente da opção escolhida no card 32) e só o C condicionado
a ela. Revisão do David em 09/09/2026: isso estava errado — a variável deve
mostrar SÓ o cenário selecionado no scenario_config.csv, os três com o mesmo
gate. Desde então A, B e C são igualmente condicionais à opção do card 32; a
variável não emite nenhuma linha quando não há scenario_config.csv ou a
opção não é reconhecida. Cada cenário tem sua própria linha por ano,
distinguidos pela Class_3: C continua 'N/A' (como sempre foi), A e B saem
como 'Scenario A' / 'Scenario B'.

MAPA option_id -> cenário NÃO É ALFABÉTICO. O scenario_config.csv real do
caso traz variable_id 32, option_id 'a', option_label "Current policies" —
isto é, a opção 'a' corresponde ao que esta variável chama de "Scenario B",
não "Scenario A" como a ordem alfabética sugeriria. Cruzando com o gate 'c'
== Domestic market only que já existia (não mexido nesta revisão), o mapa
inferido e implementado é: 'b' -> Scenario A (Expansion), 'a' -> Scenario B
(Current policies), 'c' -> Scenario C (Domestic market only). O
scenario_config.csv só registra a opção ESCOLHIDA de cada variável (não a
lista completa de opções), então não há como confirmar 'b' -> Expansion
direto do arquivo — é inferência por eliminação. CONFERIR COM A EQUIPE/DAVID
se o card 32 for revisado.

CENÁRIO C — A ROTA É POR VOLUME, NÃO POR CO2 (mudou em 02/09/2026, mantida sem
alteração nesta atualização de A/B). A versão anterior do
cálculo derivava a necessidade de petróleo do CO2 das linhas de refino e dava
0,17 Mb/d em 2050 — implausível para um país que queima 60 bilhões de litros de
diesel por ano. A causa é a ressalva A1: a combustão dos líquidos fósseis não
existe no modelo, e o CO2 de refino sozinho (~13 Mt) não descreve o volume
refinado. Derivar do volume resolve sem rodada nova, porque os volumes estão
certos — quebrada está só a contabilidade de emissões. A diferença entre as
duas rotas é de 13,5 vezes:

    ano                 2025   2030   2035   2040   2045   2050   Mb/d
    rota antiga (CO2)   3,76*  0,17   0,17   0,17   0,18   0,18
    rota por volume     3,76*  2,29   2,27   2,36   2,42   2,47
    (* âncora real de 2025, não calculada)

Reconfirmado em 02/09/2026 ao avaliar se a mesma rota de CO2 serviria para A/B
com os fatores de emissão de combustão fornecidos pela equipe: o resultado
bateu de novo nos mesmos ~0,12-0,18 Mb/d, porque esses fatores são ~10x
maiores que a emissão real de processo de refino do modelo — reforça manter
a rota por volume em C.

RECEITA DE C: petróleo necessário = MÁXIMO, sobre diesel, gasolina e querosene,
de (volume do derivado em mil tep / rendimento de refino). O máximo e não a
soma: a refinaria precisa processar cru suficiente para atender o derivado
mais exigente. O diesel puxa em todos os períodos. Rendimentos, premissa da
equipe: diesel 0,400, gasolina 0,231, querosene 0,048. Conversões: 1 kWh =
8,598e-5 tep, 1 boe = 0,1421 tep.

ÂNCORA DE 2025 DE C: 195.157,876 mil tep (3,7627 Mb/d), produção real informada
pela equipe. Em 2025 o Brasil ainda exporta, então a produção real está acima
do que o mercado interno exige — a conta por volume daria 2,29 Mb/d. Manter a
âncora faz a série começar no real e cair para o nível doméstico em 2030, que
é o que o cenário descreve. Trocar por 2,29 é uma linha, se a equipe preferir
que a série seja doméstica desde o primeiro ponto.

CENÁRIOS A E B (acrescentados em 02/09/2026) — trajetórias fixas dadas pela
equipe, sem relação com o MACRO. Âncora de 2025: 3,770 Mb/d (valor dado pela
equipe para A/B; note que não é idêntico aos 3,7627 Mb/d da âncora de C —
vêm de fontes/momentos diferentes, cada um usado como a equipe pediu para o
seu cenário). Cenário A: pico de 5,7 Mb/d em 2030, platô 2035-2050 na média
do intervalo declarado (5,5-6,3 -> 5,9 Mb/d, confirmado com a equipe: "use a
média"). Cenário B: pico de 5,3 Mb/d em 2030, 4,4 Mb/d em 2034 (fora dos
nossos períodos, só usado como âncora da fórmula), declínio geométrico de
4,5%/ano dali em diante — valor(ano) = 4,4 × 0,955^(ano-2034); confere com o
ponto dado para 2060 (fórmula ~1,33 Mb/d vs. 1,3 Mb/d declarado). Conversão
Mb/d -> boe/ano: × 1e6 × 365 dias — convenção nossa, explícita no código
(DIAS_POR_ANO), não há valor oficial documentado para isso.

RESOLUÇÃO TEMPORAL: a aba pede 1-year e nós entregamos os seis pontos do
modelo, pela convenção de cinco em cinco anos do projeto. É a segunda variável
em que isso aparece, junto com a id 56.

TABELA DE DETALHE EM flow_analysis (acrescentada em 02/09/2026): além da
linha de petróleo bruto acima, results_001/flow_analysis/
oil_production_scenarios.csv traz, só quando o cenário C está escolhido,
uma linha por ano com 10 colunas: year, scenario (sempre 'C'),
oil_production_Mbd, oil_production_mil_tep, e o mesmo par (mil_tep, Mbd)
para diesel, gasolina e jet fuel. "Produção" de cada derivado é o próprio
volume do nó de demanda em mil tep (o mesmo número usado no cálculo do
petróleo bruto, mas ANTES de dividir pelo rendimento) — não o petróleo
equivalente que aquele derivado sozinho exigiria. Em 2025 só o TOTAL de
petróleo bruto usa a âncora real; o volume de cada derivado nesse ano vem do
modelo normalmente, porque a demanda doméstica de derivados não tem o
problema de exportação que afeta o total de petróleo bruto. Todas as colunas
_Mbd usam a mesma conversão mil tep -> boe -> Mb/d (÷0,1421, ÷365, ÷1e6) das
trajetórias de A e B. Sem o cenário C escolhido, o arquivo não é criado nem
sobrescrito — se já existir de uma rodada anterior, fica como estava.
"""

NOTAS[72] = """id 72 — Fossil fuel prices

Fonte: system/fuel_prices_<ano>.csv. Atenção: é INPUT do modelo, não resultado.
São premissas exógenas de cenário, não preços de equilíbrio calculados pelo
MACRO. O arquivo tem 2016 linhas, mas o preço é constante dentro de cada
período em todas as colunas.

UNIDADE: US$/boe. O modelo grava US$/MWh e a conversão usa 1 MWh = 0,6061 boe,
ou seja, o preço em US$/MWh é DIVIDIDO por 0,6061. Conferência de sanidade:
diesel a 59,67 US$/MWh vira 98,45 US$/boe, e equivale a US$ 0,59/L, contra cerca
de US$ 0,65/L de preço real de refinaria no Brasil.

CLASSES: o combustível está na Class_2, e Class_3 a Class_5 vão como N/A. O SEEG
não tem galho para preços, então não há hierarquia a seguir abaixo do
combustível.

DOIS VALORES SUSPEITOS EM 2030. As séries de carvão têm um degrau isolado em
2030 e voltam à tendência em 2035:

  coal_price_BR        22,93  -> 137,58  ->  21,81  21,28  20,76  20,23
  coal_price_imported  21,84  ->  61,92  ->  30,19  29,45  28,72  28,02

(em US$/MWh, antes da conversão: 13,90 -> 83,39 -> 13,22... e
 13,24 -> 37,53 -> 18,30...)

Os dois valores de 2030 são exatamente valores de OUTRAS colunas do próprio
arquivo: em US$/MWh, 83,39 é o preço do querosene fóssil em 2025 e 2030, e 37,53
é o preço do gás natural em 2025. Tem cara de deslocamento de coluna no
fuel_prices_2030.csv, não de premissa. O efeito é visível no resultado: a
geração a carvão cai para 10,50 TWh em 2030 e volta a 13,68 em 2035.

O URÂNIO SAIU DESTA VARIÁVEL (02/09/2026). Ele estava incluído por completude,
constante em 4,535 US$/MWh nos seis períodos, mas urânio não é combustível
fóssil e o nome da variável na aba 'Platform outputs' enumera exatamente os
cinco que ela quer: "Wholesale price of end use fossil fuels by fuel type
(gasoline, diesel, jet fuel, NG and coal)".

Vale registrar que o card 24 do integrador NÃO trata só de gasolina, diesel,
querosene e gás: ele escreve preço para oito colunas, incluindo os dois carvões,
o GNL e o próprio urânio (8,3 US$/MWh em todas as três opções). Ou seja, o
urânio continua no input e continua sendo reescrito pelo card a cada rodada —
o que mudou é só que a gente parou de reportá-lo aqui. Se a plataforma um dia
quiser esse preço, é variável própria; devolver a linha em var_72.py é uma
linha de código.

O CARVÃO CONTINUA, e em duas linhas — nacional e importado —, embora o nome da
variável diga 'coal' no singular. São dois nós distintos no modelo, com preços
diferentes (12,26 e 16,98 US$/MWh em 2050), e somá-los exigiria uma média
ponderada por volume que a plataforma não pediu.

O querosene fóssil fica em 137,58 US$/boe em 2025 E 2030, e só depois começa a
cair — vale confirmar se é premissa ou se é o mesmo problema de 2030.
"""

NOTAS[73] = """id 73 — CO2 storage: taxa anual de injeção, por UF e por bacia

O QUE ESTA VARIÁVEL MEDE. A cadeia do carbono capturado no modelo é:

    BECCS<algo> --co2_captured_edge--> co2_captured_BR_<UF>
      --OneWayTransmissionLink{CO2Captured}--> co2_transported_BR_<UF>_<Bacia>
      --CO2Injection (BR_<UF>_CO2_Injection)--> co2_storage_<Bacia>

Existe UM ATIVO DE INJEÇÃO POR ESTADO, 27 no total, cada um ligado a uma bacia
sedimentar. A variável lê o que o ativo de injeção puxa do nó de transporte; a
aresta de saída para o reservatório dá exatamente o mesmo número. É
ARMAZENAMENTO SUBTERRÂNEO, não remoção — a id 19 é que traz remoção.

TAXA ANUAL, NÃO ESTOQUE. A unidade é MtCO2/year, como a aba pede, e o valor é
quanto entra no reservatório naquele ano. O ESTOQUE ACUMULADO seria outra
coisa: 6.362 Mt até 2050 (3.600 na bacia do Paraná, 1.577 na Parecis, 958 na
São Francisco). Se o card quiser o acumulado, é preciso pedir — o nome da
variável na planilha ('Underground carbon stored') admite as duas leituras.

RECORTE ESPACIAL: Territory = UF, bacia na Class_3 (mudou em 01/09/2026; antes
a bacia ocupava o Territory e a UF era descartada). Somar por Class_3 devolve o
total da bacia; cada UF pertence a uma bacia só. Class_4 e Class_5 ficam N/A.

Há também uma LINHA NACIONAL (Territory = BR, Class_3 = N/A) somando tudo —
somar a coluna Value sem filtrar o Territory dobra o resultado.

CONCENTRAÇÃO. Em 2050, 306 dos 516 Mt/ano vão para a bacia do Paraná: MS 158,4,
SP 103,7, PR 27,9, SC 15,2, RS 1,1. Depois vêm Parecis (MT 88,9) e São
Francisco (GO 54,5, MG 53,5). Mato Grosso do Sul sozinho injeta 158 Mt/ano. O total de 516,4 Mt em
2050 bate com o co2_storage_edge do CO2Injection.

ATENÇÃO AO CRUZAR VARIÁVEIS: Paraná e São Francisco também nomeiam bacias
HIDROGRÁFICAS nas ids 66 e 68, com o mesmo rótulo nesta coluna. São coisas
diferentes — o que separa é o Variable_group e a Class_2 (Carbon storage aqui,
Electricity generation lá).

RESSALVA — DE ONDE VEM O VOLUME INJETADO. Não se trata de contabilizar remoção
aqui: o que está em jogo é a MAGNITUDE do que entra no reservatório. Dos 516,4
Mt injetados em 2050, 493,9 foram capturados pelo BECCSEthanolv2, e a captura
desse ativo é `co2_content x fluxo da aresta principal`. O co2_content da cana
no input é 1,558 tCO2/t — valor de matéria SECA — enquanto o rendimento (0,55
MWh de etanol por tonelada, ou 93 L/t) e o preço (19 US$/t) são de cana ÚMIDA,
que carrega cerca de 0,5 tCO2/t. É um fator de aproximadamente 3 dentro da
mesma commodity. Corrigido para base úmida, o volume injetado cairia para algo
perto de 270 Mt em 2050.

RESSALVA — NÃO HÁ LIMITE GEOLÓGICO NO MODELO (nova, 01/09/2026). No
co2_injection.csv, `edges--co2_storage_edge--has_capacity` é False, e não
existe nenhum input de volume de reservatório. O único limite é a TAXA de
injeção, na aresta de entrada, e ela é livremente expansível (can_expand True,
existing_capacity zero). Ou seja: o modelo pode injetar indefinidamente em
qualquer bacia, e ninguém verificou se as bacias comportam os 6.362 Mt
acumulados — 3.600 deles só no Paraná.

A TAXA DE INJEÇÃO É RESTRIÇÃO ATIVA. A capacidade instalada roda perto do
limite de 2035 em diante, o que quer dizer que o volume estocado não é livre:
é o que a capacidade construída permitiu.

    ano              2025   2030    2035    2040    2045    2050
    injetado (Mt)     0,3    0,4   133,2   253,1   368,9   516,4
    capacidade (Mt)   0,6    0,6   139,9   270,0   396,9   564,0
    uso              50%    75%     95%     94%     93%     92%

DEPENDE DA CONVENÇÃO, e as duas leituras são opostas:

  convenção MACRO (a do pacote)  NÃO somar esta variável com a id 19. A remoção
      da id 19 já é a absorção bruta da biomassa, e o CO2 estocado é a parcela
      dela que não voltou para a atmosfera. Somar conta o mesmo carbono duas
      vezes.

  convenção SEEG  esta variável É a remoção, e a id 19 sai inteira da conta. A
      queima de biomassa é neutra, então a absorção bruta se cancela contra a
      emissão biogênica da id 18 e sobra só o carbono enterrado. É assim que se
      obtém a linha 'convenção SEEG' da tabela na nota das ids 18/19 —
      descontando antes o CCS fóssil, que a id 18 já contabiliza líquido.

COMPOSIÇÃO DO QUE ESTÁ ESTOCADO em 2050 (Mt): BECCS de etanol 493,9, BECCS de
eletricidade 19,4, BECCS de hidrogênio 2,9, hidrogênio SMR com CCS 0,1, captura
direta do ar 0,1. É biogênico em 99,97%.
"""

NOTAS[74] = """id 74 — CO2 transport pipelines (km de duto), por bacia sedimentar (era "CO2 transport"; renomeada a pedido do David, 09/09/2026)

TERRITORY = UF E A BACIA DE DESTINO NA CLASS_3, como na id 73 (02/09/2026;
antes a bacia ocupava o Territory e a UF era descartada). Class_4 fica N/A e a
Class_5 mantém 'Pipeline' como qualificador do modal. São 27 estados e nove
bacias; somar por Class_3 devolve o total da bacia.

CONCENTRAÇÃO: dos 9.500 km, 6.400 servem a bacia do Parecis — são os dutos que
saem dos estados do Norte e do Centro-Oeste, longe de qualquer reservatório.
Depois vêm São Francisco com 900 km e Sergipe-Alagoas com 600.

NÃO HÁ LINHA NACIONAL, de propósito: somar quilômetros de dutos que servem
bacias diferentes não descreve uma rede única, e o número não teria leitura
física. Diferente da id 73, onde o CO2 estocado soma.

A distância vem do input (assets_<ano>/co2_pipeline.csv) e o resultado diz
quais dutos operam. Aqui a distância É usada no custo de investimento
(0/100/200/300/900 km -> 0/158.223/307.999/448.767/1.164.992 US$/MW), então é
dado operante — diferente da transmissão elétrica, cujo input traz a nota
'distance for record-purpose only'.

CRITÉRIO: km de duto EM OPERAÇÃO, com fluxo anual acima de 0,1 Mt (constante
LIMIAR em var_74.py). O critério óbvio — km com capacidade contratada — não
serve: todo duto recebe capacidade > 0 já no período 1 (2,1 Mt no país
inteiro), o que acende a rede inteira desde 2025 e dá 9.500 km constantes nos
seis períodos.

O LIMIAR FOI RETIRADO EM 02/09/2026. Ele definia sozinho a série publicada, e
essa era a razão para tirá-lo. Medido antes da mudança, km totais por ano:

    LIMIAR (t/ano)   2025   2030   2035   2040   2045   2050
    0 (adotado)      9.500  9.500  9.500  9.500  9.500  9.500
    10.000           2.300  3.900  3.900  3.900  3.900  7.500
    100.000 (antigo)     0      0  2.400  2.400  2.400  2.500
    1.000.000            0      0  1.200  1.200  1.300  1.500

Quatro histórias diferentes a partir do mesmo resultado, e o corte não vinha do
modelo nem da plataforma — era escolha nossa. Com o limiar antigo a variável
dizia ZERO km em 2025 e 2030, o que se lê como 'não existe rede de dutos de CO2
no Brasil'.

O QUE A SÉRIE DIZ AGORA: 9.500 km constantes nos seis períodos. A linha é plana
porque o modelo dá capacidade à rede inteira já no período 1 e não a expande —
o que varia é quanto passa por ela, não quanto existe. Se o card quiser uma
métrica que se mova, o Mt.km transportado é a que se move (ver abaixo).

Se a plataforma preferir uma métrica que varie de fato, o Mt.km transportado é
a que se move: 75 / 99 / 16.972 / 29.001 / 49.105 / 74.224.
"""

NOTAS[75] = """id 75 — Capex

Acrescentada em 02/09/2026, a pedido do usuário. Duas leituras na mesma
variável, distinguidas pela Class_2:

CAPEX (uma linha por ano, 2025-2050) — soma da coluna value de
results_period_<p>/results_period_<p>/capex.csv: todas as commodities e
tecnologias do período somadas juntas (Battery, BECCS*, ThermalPower*,
VRE{Generic}, TransmissionLink, CO2Injection etc. — 16 commodities distintas
no arquivo). É o capex BRUTO do período: sem desconto ao ano-base e sem
amortização.

NÃO CONFUNDIR com a categoria 'Investment' de costs_by_type.csv, já usada
pelas ids 24 e 26: aquela é o custo de investimento como o modelo o computa
no objetivo — descontado ao ano-base, e (a julgar pela id 26) parece ser uma
anuidade, não o capex de uma vez só. Os dois números não batem: no período 1
dos dados reais do usuário, capex.csv soma ~33,5 bilhões, a categoria
Investment de costs_by_type.csv (descontada) soma ~49,0 bilhões — e a mesma
categoria em undiscounted_costs_by_type.csv soma ~84,0 bilhões (esse arquivo,
aliás, tem linhas com NaN, inclusive a linha Total — não é uma fonte
confiável hoje). Três séries diferentes, nenhuma redutível às outras; capex.csv
é a única que corresponde literalmente ao pedido do usuário ("somar a coluna
value do arquivo capex.csv de cada período").

Total Investment Cost (UMA linha só, ano 2025) — soma do CAPEX (a série acima)
de TODOS os seis períodos. Não é uma série por ano: por pedido explícito do
usuário, essa linha existe só em 2025, não nos outros cinco anos. Nunca somar
Value sem filtrar por Class_2 — somar a coluna inteira sem separar 'CAPEX' de
'Total Investment Cost' conta o mesmo capex duas vezes (uma nas seis linhas
por período, outra na linha do total).

UNIDADE: US$, mesma convenção das ids 24, 26 e 27 (nenhuma conversão aplicada
— o valor sai de capex.csv exatamente como o modelo grava).
"""

NOTAS[18] = """id 18 e 19 — convenção de contabilidade de carbono

Os valores seguem a convenção do MACRO, não a do SEEG. O modelo faz ciclo
cheio: a absorção de CO2 pela biomassa entra como REMOÇÃO (id 19) e a combustão
de biomassa entra como EMISSÃO (id 18). O SEEG trata as duas como ciclo neutro
e não reporta nenhuma delas.

Efeito no líquido (Mt CO2/ano):
                   2025    2035    2045    2050
  convenção MACRO  613,2   167,9  -277,1  -499,8
  convenção SEEG   620,4   276,5     1,0  -160,3

A convenção MACRO foi escolhida porque é a única que reconcilia com o cap de
emissões que o modelo otimizou (614 / 391 / 168 / -54 / -277 / -500 Mt).

COMO SE CALCULA A LINHA 'convenção SEEG' (reconstruído em 01/09/2026). Ela NÃO
sai de um filtro sobre estas duas variáveis, e a instrução anterior — "filtrar
fora as linhas com Class_5 = 'CO2 (biogenic)'" — estava errada: filtrando dá
620,6 / 409,0 / 408,5 / 390,3 / 368,1 / 354,4 Mt, que é outra coisa (emissão
fóssil menos DAC).

A conta certa é uma subtração entre duas variáveis:

    SEEG = emissão FÓSSIL da id 18  -  CO2 ESTOCADO da id 73

    ano    18 fóssil   71 estocado   SEEG
    2025      620,6          0,2    620,4
    2030      409,4          0,4    409,0
    2035      409,8        133,2    276,6
    2040      392,0        253,1    139,0
    2045      369,9        368,9      1,0
    2050      356,2        516,3   -160,0

Reproduz a tabela acima na primeira casa. A lógica: no SEEG a queima de
biomassa é ciclo neutro, então a emissão biogênica da id 18 e a absorção bruta
da id 19 se cancelam e SAEM DAS DUAS PONTAS. O que sobra de remoção é só o
carbono que foi de fato enterrado — que é exatamente a id 73.

DUAS SUTILEZAS:

  A id 19 NÃO ENTRA na conta SEEG, nem a linha de captura direta do ar. O CO2
  do DAC vai para o reservatório e já está dentro da id 73; somar a linha de
  DAC da id 19 por cima conta o mesmo carbono duas vezes.

  O CCS FÓSSIL SAI da id 73 antes da subtração. A id 18 já registra a emissão
  desses ativos LÍQUIDA do que foi capturado, então creditar a captura de novo
  como remoção seria dupla contagem — enterrar carbono fóssil é emissão
  evitada, não remoção. Hoje isso é irrelevante (0,14 Mt em 2050, o
  ThermalHydrogenCCS e o ThermalPowerCCS), mas numa rodada com mais CCS fóssil
  a diferença cresce.

ESTA CONTA HERDA O PROBLEMA DA CANA. Como 493,9 dos 516,4 Mt estocados em 2050
vêm do etanol de cana, a ressalva do co2_content da cana (ver a nota da id 73:
base seca contra base úmida, fator de cerca de 3) recai inteira sobre a linha
SEEG. Corrigida a base, a id 73 de 2050 cairia para perto de 270 Mt e o SEEG de
2050 iria de -160 para algo em torno de +86 Mt — troca de sinal. O número
publicado precisa esperar essa correção.

CLASS_5 É O GÁS, E SÓ O GÁS (correção incorporada de outra rodada, 02/09/2026).
Os pares Class_5/Unit que existem no padrão da plataforma são CO2e
GWP100-AR5/tCO2e, CO2/tCO2, CH4/tCH4 e N2O/tN2O; a linha de convenção manda o
primeiro. O MACRO só rastreia CO2 — não há CH4 nem N2O — então CO2e é igual a
CO2 aqui e o GWP é indiferente; vale o rótulo do padrão para o número somar com
o dos outros modelos.

ONDE FOI PARAR A MARCAÇÃO FÓSSIL/BIOGÊNICO. Ela ocupava a Class_5 ('CO2' e
'CO2 (biogenic)') e não cabe em nenhuma coluna do padrão: nenhum outro modelo
faz contabilidade de ciclo cheio, então a plataforma não previu o corte. Ele
continua recuperável linha a linha, sem ambiguidade:

    id 18   pelo Class_4. É combustão de biomassa quando o rótulo é um destes:
            Biodiesel, Bioelectricity, Biomethane, Charcoal, Ethanol, Hydrogen,
            Renewable diesel, Renewable gasoline, Residue, Sustainable aviation
            fuel, Synthetic methane. Todo o resto é fóssil. Conferido: o
            Class_4 determina o corte em 100% das linhas.

    id 19   pelo Class_1. As três famílias de biomassa — Primary crops,
            Herbaceous residues, Woody biomass — são biogênicas. Class_1 =
            'N/A' é captura direta do ar ou insumo secundário, e não é
            biogênico.

SINAL DAS REMOÇÕES (correção incorporada de outra rodada, 02/09/2026): a id 19
sai NEGATIVA, como as 2.038 linhas de removals do padrão da plataforma. A
coluna Emissions_or_removals marca a natureza da linha, mas quem soma a coluna
Value para montar o gráfico agregado precisa que o sinal esteja lá. Os números
citados nestas notas continuam em módulo, que é como se lê uma remoção.

O GeneralFuelsEndUse agrega a demanda final: não dá para separar Transportes,
Industrial, Residencial e Comercial como o SEEG faz. Essas linhas vão com
Class_2 = 'N/A' e o combustível na Class_4.

Três ressalvas:

1. CARBONO BIOGÊNICO SEM DESTINO. O balanço de carbono da biomassa não fecha:
   entra como absorção mais do que sai como emissão ou como estoque geológico.
   O resíduo é de 7,1 Mt em 2025 e 339,6 Mt em 2050. Só no etanol: 916,8 Mt
   absorvidos, 7,0 liberados na conversão, 493,9 capturados, 74,5 queimados no
   uso final — sobram 341 Mt sem destino. Não há restrição de fechamento sobre
   o carbono biogênico no modelo, então ele sai do balanço como remoção
   líquida. Boa parte dos -499,8 Mt de 2050 vem daí.

2. EMISSÕES EXÓGENAS CONGELADAS. O bloco 'Exogenous emissions' (indústria,
   resíduos, agropecuária — tudo o que o MACRO não modela) fica em 284,4
   Mt/ano nos seis períodos. O input system/CO2_Emissions.csv previa uma
   trajetória crescente, de 284,4 (2025) a 355,9 Mt (2050), mas o modelo míope
   só lê existing_capacity no período 1 e carrega o valor de 2025 até o fim.
   Faltam cerca de 71 Mt/ano em 2050.

3. UPSTREAM FÓSSIL DE 2025. Os 172,7 Mt de 2025 caem para 12,1 em 2030. O salto
   é o laço de gás natural identificado na validação de commodities (cerca de
   164,8 Mt espúrios em 2025), não uma queda real.

Não somar a id 73 (CO2 storage) com a id 19: nesta convenção a remoção já é a
absorção bruta da biomassa, e o CO2 estocado é a parcela dela que não foi
liberada. Somar as duas conta o mesmo carbono duas vezes.

-----------------------------------------------------------------------------
EM ABERTO: REESTRUTURAÇÃO PARA O CARD 32 (Oil production)

A id 18 vai mudar para conversar com o card 32, que oferece três cenários de
produção de petróleo. Nos cenários A (expansão, PNE 2050) e B (políticas
atuais, PDE 2034) quem reporta extração e refino é o EnergyPathways; no cenário
C (produção só para o mercado interno) quem reporta é o MACRO — ver a nota da
id 71 (Oil production). O mecanismo acordado: o EP emite a linha zerada e nós
preenchemos, ou vice-versa, e a plataforma soma linhas de mesmo nome.

O SLOT DO EP: CONFERIDO NA 2plat_all EM 02/09/2026, e a nota anterior estava
errada em uma coluna. A linha existe, está zerada nos 27 anos (2024 a 2050) e é

    Model Variable_group Emissions_or_removals Class_1  Class_2  Class_3
    EP    Emissions      Emissions             Energy   industry oil production

    Class_4 vazio · Class_5 CO2e GWP100-AR5 · Unit tCO2e GWP100-AR5 · Territory BR

Class_1 é **Energy**, não 'IPPU' como esta nota dizia. A diferença importa: a
plataforma soma linhas de mesmo nome, e preencher o slot com IPPU deixaria a
nossa linha fora da soma.

E RESPONDE A UMA DAS PENDÊNCIAS: NÃO HÁ LINHA DE REFINO SEPARADA. Varri a
2plat_all inteira — nenhum modelo tem linha de refino em lugar nenhum (as linhas
de 'refinery gas' do EP são uso industrial de combustível, não refino). Logo
'oil production' é um slot único que cobre extração E refino juntos, e é ele que
a nossa Class_3 = 'Oil refining' tem de alimentar.

Para a soma funcionar é preciso alinhar o formato deles: separador ';', anos
ANUAIS de 2024 a 2050, Unit = 'tCO2e GWP100-AR5' (TONELADAS, não Mt) e
Class_5 = 'CO2e GWP100-AR5'.

NÃO EXISTE REPARTIÇÃO A FAZER — o modelo já separa (esclarecido em 01/09/2026).
A versão anterior desta nota dizia que "25,3% do diesel e 23,07% da gasolina e
do querosene são extração+refino". **Aqueles números não são percentuais**: são
0,253 e 0,2307 tCO2 POR TONELADA DE PETRÓLEO, o fator de emissão do refino, do
BEN. Foram transcritos como porcentagem em algum momento e a leitura errada se
propagou. Aplicá-los como percentual daria 62 Mt em 2050 no lugar de 19 — mais
de três vezes.

O fator já está no modelo, em `transforms--emission_rate` das três linhas de
`fossil_fuels_upstream.csv`, e é exatamente a coluna que o card 32 escreve
(macro_scenario/data/card32_emissions.py). Convertendo a 11,63 MWh por tonelada
de petróleo:

    fonte                        tCO2/MWh   tCO2/t petróleo
    caso S0, diesel               0,02001        0,2327
    caso S0, gasolina/querosene   0,01943        0,2260
    card 32, opções A e B         0,02021        0,2350
    card 32, opção C — diesel     0,02705        0,3146
    card 32, opção C — gas/quer   0,02627        0,3055
    BEN, diesel                        —         0,2530
    BEN, gasolina/querosene            —         0,2307

Todos da mesma família, com 2 a 9% de diferença entre si. É calibração, não
estrutura: escolher entre o valor do BEN e o do card é uma decisão de dado.

NÓS NÃO MEXEMOS NO NÚMERO. Este código roda na plataforma e tem de funcionar
para qualquer escolha do usuário: ele reporta o que o modelo produziu,
manuseando o formato quando preciso, nunca o valor. As emissões de extração e
refino saem como o modelo as calculou, com Class_2 = 'Fuel production' e
Class_3 = 'Oil refining', qualquer que seja a opção do card 32. Não há filtro
por cenário nem reescalonamento aqui — se houvesse, o output deixaria de bater
com o modelo, e é o modelo que a plataforma está publicando.

Trocar o fator de emissão do refino — adotar o do BEN, por exemplo — é mudança
em macro_scenario/data/card32_emissions.py e rodada nova do modelo. Não é conta
que se faça na montagem do output.

DUAS COISAS PARA A EQUIPE DA PLATAFORMA, então, e nenhuma delas é nossa:

  1. Se em A e B quem reporta extração e refino é o EP, o card 32 deveria
     escrever emission_rate ZERO nessas duas opções. Hoje escreve 0,02021, e o
     modelo gera as emissões nos três cenários — o que duplica com o slot
     'oil production' do EP quando o usuário escolhe A ou B.

  2. Se o fator do BEN é o que vale, ele entra no card. Os valores atuais
     (0,2350 em A/B; 0,3146 e 0,3055 em C, em tCO2/t) não são os do BEN
     (0,2530 e 0,2307).

QUATRO PONTOS AINDA SEM DECISÃO, aguardando planilha agregada da equipe:

1. A BASE DA REPARTIÇÃO. Repartindo o que o modelo contabiliza hoje, extração+
   refino sai de 27,2 Mt (2025) para 5,8 Mt (2050). Repartindo a queima que a
   oferta física implica, sai de 52,0 para 46,8 Mt. A diferença é o bypass de
   combustão descrito no ponto 2.

2. BYPASS DE COMBUSTÃO DO DIESEL FÓSSIL. De 2030 em diante o modelo entrega
   550 a 596 TWh de diesel fóssil por ano — o consumo real do Brasil, cerca de
   60 bilhões de litros — e contabiliza ZERO de queima. O volume chega ao nó
   diesel_demand_BR pelo UpstreamEmissions{LiquidFuels}, sem passar por ativo
   com emission_rate; o BR_Diesel_fossil_Downstream, que tem o fator 0,271,
   movimenta 0,01 TWh. Faltam cerca de 162 Mt/ano de CO2 em 2050 — mais do que
   toda a repartição que se pretende reportar, e o suficiente para levar o
   líquido de -499,8 Mt para algo perto de -280 Mt.

3. REFINO tem linha própria no EP ou divide a linha 'oil production' com a
   extração? O arquivo deles não tem slot de refino.

4. ANOS INTERMEDIÁRIOS. O EP é anual e o MACRO tem seis pontos de cinco em
   cinco anos. Nos 21 anos que não são múltiplos de cinco a contribuição do
   MACRO não existe, e no cenário C a série sairia serrilhada. Interpolar ou
   entregar só os seis pontos?
"""

NOTAS[19] = NOTAS[18] + """

-----------------------------------------------------------------------------
id 19 — CLASSES POR MATÉRIA-PRIMA

O SEEG é uma taxonomia de EMISSÃO e não tem galho para remoção. Por isso a id 19
usa a estrutura do diagrama de rotas da equipe, e só ela:

    Class_1  família da matéria-prima   Primary crops / Herbaceous residues /
                                        Woody biomass
    Class_2  matéria-prima              Sugarcane, Corn, Soybean, Macauba,
                                        Sugarcane straw, Corn stover, Rice
                                        straw, Plantation forestry, Forestry
                                        residues
    Class_3  rota de conversão          Sugarcane ethanol, Biomass power,
                                        Gasification H2, Charcoal kiln...
                                        com o CCS no próprio nome
    Class_4  vetor energético           Ethanol, Electricity, Hydrogen...
    Class_5  gás

COMO A REMOÇÃO É LIGADA À MATÉRIA-PRIMA: a captação é registrada no ATIVO de
conversão, não na biomassa, e o MACRO a calcula como

    remoção = co2_content DO ATIVO x fluxo da ARESTA PRINCIPAL

Um co2_content por ativo — 1,650 tCO2/t no etanol de milho, 1,558 na cana e na
lenha, 1,613 no FAME, 1,833 na carvoaria — aplicado a uma aresta só. Então cada
remoção vai INTEIRA para a commodity dessa aresta; não há o que ratear. A
aresta principal é o biomass_edge, ou o origin_edge nos ativos de coleta de
palha, ou o ethanol_edge no ATJ; o DAC não tem nenhuma das três. Conferido nas
28 famílias de ativo com remoção: bate na terceira casa em todas.

O COINPUT_EDGE FICA DE FORA, e essa é a diferença para a versão anterior desta
variável, que rateava a captação pela massa de TODAS as entradas. Três rotas
queimam lenha de floresta plantada como co-insumo de processo:

    ano   rota                insumo principal   lenha co-insumo   % lenha
    2025  etanol de milho      66,6 Mt milho        21,2 Mt         24,1%
    2025  FAME de soja         40,8 Mt soja          2,5 Mt          5,7%
    2050  FAME de macaúba      75,7 Mt macaúba       5,3 Mt          6,5%

O modelo não registra captação nenhuma sobre essa lenha. O rateio antigo criava
um crédito inexistente e movia, só em 2025, 30 Mt de Primary crops para Woody
biomass: milho ia a 83,4 em vez de 109,9 e floresta plantada a 60,7 em vez de
30,5. Corrigido, esta variável reproduz a planilha agregada da equipe
(co2_co2captured_technology_flows.xlsx) matéria-prima por matéria-prima, com
divergência máxima de 1,5e-05 Mt em 66 células.

A ÚNICA DIFERENÇA QUE SOBRA para aquela planilha é o DAC, que ela não traz:
0,003 Mt em 2025 e 0,086 em 2050, na linha 'Atmospheric CO2'. E o rótulo da
rota 1G2G, que lá é 'Sugarcane + sugarcane straw' e aqui é 'Sugarcane' — o
biomass_edge do ativo é cana, então é para a cana que a remoção vai; a palha
entra pelo coinput_edge e não capta nada. São 0,33 Mt em 2050.

MACAÚBA NÃO ESTÁ NO DIAGRAMA mas é a matéria-prima dominante do biodiesel neste
cenário (75,7 Mt e 122,1 Mt de CO2 capturado em 2050). Entrou como cultura
primária.

'AGGREGATED RESIDUE' é o nó Residue, que recebe as três palhas depois do
BiomassTransformation. Quem consome Residue não sabe de qual palha veio, então
essa parcela não desce até 'Corn stover' ou 'Rice straw'. A captação da palha
em si aparece na rota 'Residue collection', essa sim discriminada por palha.

DUAS DUPLAS CONTAGENS PEQUENAS, visíveis agora que a variável está por
matéria-prima (Mt/ano):

                                       2025    2035    2050
  palha -> Residue (captação no BT)    4,50   16,29   47,48
  Residue consumido a jusante          2,76    8,72   27,81
  captação repetida no consumo         0,14    0,25    3,12
  captação do etanol no ATJ            0,01    1,27    1,76

O caminho do resíduo está quase todo certo: as termelétricas a biomassa, que são
o maior consumidor (25,8 Mt de resíduo em 2050), registram captação ZERO,
porque a captação da palha já foi feita no BiomassTransformation. Mas as rotas
menores — gaseificação de H2, etanol de 2ª geração e SNG — registram captação de
novo sobre o mesmo carbono: 3,12 Mt em 2050.

O ATJ é um caso diferente: ele consome ETANOL, não biomassa, e mesmo assim
registra 1,76 Mt de captação em 2050, com emissão zero. O carbono desse etanol
já tinha sido capturado na usina. É remoção sem lastro físico.

As duas somam 4,9 Mt em 2050 — pequeno perto dos 339,6 Mt de carbono biogênico
sem destino descritos acima, mas são parte da mesma família de problema."""
