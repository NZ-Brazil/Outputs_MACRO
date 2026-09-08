# Outputs_MACRO

README — COMO RODAR O PIPELINE — NZ-Brazil
================================================================================
Só os passos para gerar os resultados. Para entender o que cada arquivo é,
ver LEIA-PRIMEIRO.txt.


0. ANTES DE RODAR: LINKAR O scenario_config.csv
--------------------------------------------------------------------------------
O scenario_config.csv é o arquivo que diz qual opção do card 32 (cenário de
produção de petróleo) está em uso no caso — é dele que a id 71 (Oil
production) lê se deve calcular o cenário C ou não. Ele não faz parte do
projeto MacroEnergy.jl em si, então PRECISA estar presente (copiado ou
linkado) num dos dois lugares abaixo, antes de rodar:

    <pasta do projeto MacroEnergy.jl>\scenario_config.csv
    <pasta do projeto MacroEnergy.jl>\..\scenario_config.csv     (uma pasta acima)

Ou seja, dentro ou um nível acima de:
    C:\Users\rache\NZ-Brazil-MacroEnergy_default\Default_scenario\

Sem esse arquivo (ou com ele apontando para outra opção que não 'c'), a id 71
só sai com os cenários A e B — o C não aparece, e o pipeline roda normalmente
do mesmo jeito, só sem essa linha. Vale conferir esse arquivo TODA VEZ que
trocar de caso ou de cenário do card 32, porque ele não é regerado pelo
pipeline — só lido.


1. RODAR TUDO DE UMA VEZ (a partir do flows.csv.gz bruto)
--------------------------------------------------------------------------------
Abra o terminal na pasta outputs_MACRO e rode:

    cd "C:\Users\rache\Desktop\outputs_MACRO"
    python run_pipeline_completo.py --model-root "C:\Users\rache\NZ-Brazil-MacroEnergy_default\Default_scenario" --montar-args --xlsx

Isso faz, em sequência:
  a) roda o run_full_pipeline.py do projeto MacroEnergy.jl — agrega o
     flows.csv.gz em annual_aggregation/ e gera as 20 planilhas de
     tecnologia por commodity em results_001/flow_analysis/;
  b) roda o montar.py sobre os mesmos resultados, gerando os CSVs de
     plataforma/ e, se o cenário C estiver escolhido no scenario_config.csv,
     a tabela de detalhe da id 71 em
     results_001/flow_analysis/oil_production_scenarios.csv.

Isso demora mais, porque reprocessa o flows.csv.gz inteiro. Só é necessário
quando os resultados do modelo mudaram desde a última vez.


2. RODAR SÓ O montar.py (annual_aggregation já existe, nada do modelo mudou)
--------------------------------------------------------------------------------
Se o passo 1 já rodou antes e só o scenario_config.csv (ou outra coisa que
não depende do flows.csv.gz) mudou, pule a reagregação:

    cd "C:\Users\rache\Desktop\outputs_MACRO"
    python run_pipeline_completo.py --model-root "C:\Users\rache\NZ-Brazil-MacroEnergy_default\Default_scenario" --skip-run-full-pipeline --montar-args --xlsx

(equivalente a rodar direto: python montar.py --root "<pasta do projeto>" --out plataforma --xlsx)


3. CONSOLIDAR PARA A PLATAFORMA
--------------------------------------------------------------------------------
Depois de gerar (ou regerar) os CSVs de plataforma/, junte tudo nas duas
planilhas finais:

    python consolidar_plataforma.py --plataforma plataforma

Gera:
    plataforma/2plat_macro_outputs.csv     todas as variáveis, exceto 18 e 19
    plataforma/2plat_macro_emissions.csv   18 e 19 juntas, sem o bloco de
                                            indústria


O QUE CONFERIR DEPOIS DE RODAR
--------------------------------------------------------------------------------
  - A linha "[71] ... linhas -> .../71_oil_production.csv" no terminal: se
    tiver 12 linhas, só saiu A e B (scenario_config.csv ausente ou não é
    'c'); se tiver 18, saíram os três cenários.
  - Se apareceu "aviso: ...flow_analysis não existe — 71 não tem cópia em
    flow_analysis": normal quando --model-root não é a rodada viva do
    MacroEnergy.jl (por exemplo, ao rodar sobre um resultado arquivado).
  - Se apareceu "aviso: cenário C não escolhido — oil_production_scenarios.csv
    não foi criado/atualizado": normal quando o scenario_config.csv está
    ausente ou aponta para outra opção — o arquivo (se já existir de uma
    rodada anterior) fica como estava, sem ser criado nem sobrescrito.
  - A linha "[75] ... linhas -> .../75_capex.csv" no terminal: precisa ter
    7 linhas (6 anos de CAPEX + 1 de Total Investment Cost em 2025). Se
    faltar, provavelmente falta capex.csv em algum results_period_<p> (a id
    75 não tem gate de scenario_config.csv — não depende do card 32, só
    precisa de capex.csv em cada um dos seis períodos).
  - Contagem de linhas removidas de indústria no consolidar_plataforma.py
    (deve aparecer sempre que 2plat_macro_emissions.csv é gerado).


Requer: Python 3, pandas, openpyxl (pip install pandas openpyxl).
