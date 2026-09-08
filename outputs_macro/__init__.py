"""Geradores dos CSVs de output do MACRO no formato da plataforma.

Um módulo por variável (var_<id>.py), cada um expondo:
    ID, NOME, COL2, gerar(root, por_uf=False, **kw) -> list[dict]

Os módulos com prefixo _ são vocabulário compartilhado, não variáveis.
"""
from . import (var_18, var_19, var_24, var_26, var_27, var_55, var_56, var_65,
               var_66, var_67, var_68, var_69, var_70, var_71, var_72,
               var_73, var_74, var_75)

MODULOS = [var_18, var_19, var_24, var_26, var_27, var_55, var_56, var_65,
           var_66, var_67, var_68, var_69, var_70, var_71, var_72,
           var_73, var_74, var_75]
VARS = {m.ID: m for m in MODULOS}

from ._notas import NOTAS as NOTAS_GERAIS   # NOTAS_GERAIS[0]: nacional x UF

PENDENTES = {
    57: ("Electricity use (intermediate and final) — não é mais publicada por "
         "outra equipe (o número foi reaproveitado alhures), mas a definição "
         "que faltava (Class_3 = Intermediate use / Final use, seguindo o "
         "electricity_flow_analysis.py) já existe; falta só portar o código. "
         "Ver a nota da variável."),
}
