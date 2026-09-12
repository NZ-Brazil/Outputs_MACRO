"""Classificação compartilhada pelas variáveis de eletricidade (66, 67, 68)."""
import re

# Class_2/Class_3 do SEEG. A sub-categoria de "Geração de eletricidade" é uma
# cópia literal da categoria no SEEG — no esquema posicional (a) ela repete
# mesmo, e o combustível/fonte desce para a Class_4.
C2 = "Electricity generation"
C3 = "Electricity generation (public service)"

EXCLUIR_TRANSMISSAO = {"TransmissionLink{Electricity}",
                       "OneWayTransmissionLink{Electricity}"}

# resource_type -> (Class_4 fonte, Class_5 detalhe). None => decidir pela família.
FONTE = {
    "VRE{Generic}":                (None, None),
    "MustRun":                     ("Hydropower", "Run-of-river"),
    "HydroRes":                    ("Hydropower", "Reservoir"),
    "Battery":                     ("Battery storage", "NA"),
    "ThermalPower{NaturalGas}":    ("Natural gas", "Without CCS"),
    "ThermalPowerCCS{NaturalGas}": ("Natural gas", "With CCS"),
    "ThermalPower{Coal}":          ("Coal", "NA"),
    "ThermalPower{Uranium}":       ("Nuclear", "NA"),
    "ThermalPower{Hydrogen}":      ("Hydrogen", "NA"),
    "BECCSEthanolv2":              ("Bioelectricity", "Cogeneration (ethanol plants)"),
    "BioGasifSNG":                 ("Bioelectricity", "Cogeneration (biomethane plants)"),
}

BECCS_ELEC = {
    "biomass_wood_thermal_plant":     "Dedicated wood",
    "biomass_wood_thermal_plant_CCS": "Dedicated wood with CCS",
    "biomass_thermal_plant":          "Residue",
    "biomass_thermal_plant_CCS":      "Residue with CCS",
}


def vre(fam: str):
    if fam.startswith("Solar"):         return ("Solar photovoltaic", "Utility-scale")
    if fam.startswith("rooftop_pv"):    return ("Solar photovoltaic", "Rooftop")
    if fam.startswith("Wind_Onshore"):  return ("Wind", "Onshore")
    if fam.startswith("Wind_Offshore"): return ("Wind", "Offshore")
    return ("Solar and wind", fam)


def classificar(resource_type: str, resource_id: str, battery_label="NA"):
    fam = re.sub(r"^BR_[A-Z]{2}_", "", str(resource_id))
    if resource_type == "VRE{Generic}":
        return vre(fam)
    if resource_type == "BECCSElectricity":
        return "Bioelectricity", BECCS_ELEC.get(fam, fam)
    if resource_type == "Battery":
        return "Battery storage", battery_label
    return FONTE.get(resource_type, (resource_type, "NA"))
