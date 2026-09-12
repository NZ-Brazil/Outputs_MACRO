"""Vocabulário compartilhado pelas variáveis de CO2 (73, 74)."""
import re

GRUPO = "Underground carbon storage"
C2    = "Carbon storage"

# Bacias SEDIMENTARES (armazenamento de CO2). Paraná e São Francisco também
# nomeiam bacias HIDROGRÁFICAS nas ids 66 e 68; o rótulo é o mesmo e as duas
# famílias se distinguem pelo Variable_group e pela Class_2 — Carbon storage
# aqui, Electricity generation lá.
BACIA = {"Parana": "Paraná", "Parecis": "Parecis", "SaoFrancisco": "São Francisco",
         "Reconcavo": "Recôncavo", "EspiritoSanto": "Espírito Santo",
         "Campos": "Campos", "Potiguar": "Potiguar", "Ceara": "Ceará",
         "SergipeAlagoas": "Sergipe-Alagoas"}


def _rotulo(bruto):
    return BACIA.get(str(bruto), str(bruto))


def de_no(no):
    """co2_transported_BR_MS_Parana -> ('MS', 'Paraná')"""
    m = re.match(r"co2_transported_BR_([A-Z]{2})_(.+)$", str(no))
    if not m:
        return None, None
    return m.group(1), _rotulo(m.group(2))


def de_duto(rid):
    """BR_MS_CO2_Pipeline_Parana -> ('MS', 'Paraná')"""
    m = re.match(r"BR_([A-Z]{2})_CO2_Pipeline_(.+)$", str(rid))
    if not m:
        return "BR", "NA"
    return m.group(1), _rotulo(m.group(2))
