"""Classificació de gasos segons UNE-EN 437:2022 - Índex de Wobbe"""
import math
from typing import Optional, Dict, Any, Tuple


class GasClassifier:
    RANGES = [
        ("Primera", "a", 22.4, 24.8),
        ("Segona", "L", 39.1, 44.8),
        ("Segona", "E", 40.9, 54.7),
        ("Segona", "H", 45.7, 54.7),
        ("Tercera", "P", 72.9, 76.8),
        ("Tercera", "B", 81.8, 87.3),
        ("Tercera", "B/P", 72.9, 87.3),
    ]

    GAS_DESIGNACIONS = {
        ("Primera", "a"):   ("G110", "Gas de ciutat"),
        ("Segona", "L"):    ("G25", "Gas natural L"),
        ("Segona", "E"):    ("G20", "Gas natural E"),
        ("Segona", "H"):    ("G20", "Gas natural H"),
        ("Tercera", "P"):   ("G31", "Propà"),
        ("Tercera", "B"):   ("G30", "Butà"),
        ("Tercera", "B/P"): ("G30/G31", "Barreja butà/propà"),
    }

    VALORS_ESTANDARD = {
        "G110":   {"pcs_mj": 17.0,  "pcs_kwh": 4.72,  "densitat": 0.50},
        "G25":    {"pcs_mj": 34.5,  "pcs_kwh": 9.58,  "densitat": 0.65},
        "G20":    {"pcs_mj": 38.7,  "pcs_kwh": 10.75, "densitat": 0.60},
        "G31":    {"pcs_mj": 93.0,  "pcs_kwh": 25.83, "densitat": 1.55},
        "G30":    {"pcs_mj": 122.0, "pcs_kwh": 33.89, "densitat": 2.00},
        "G30/G31":{"pcs_mj": 107.0, "pcs_kwh": 29.72, "densitat": 1.75},
    }

    @staticmethod
    def calcular_wobbe(pcs_mj_m3: float, densitat_relativa: float) -> float:
        if densitat_relativa <= 0:
            return 0.0
        return pcs_mj_m3 / math.sqrt(densitat_relativa)

    @classmethod
    def classificar(cls, pcs_mj_m3: float, densitat_relativa: float
                    ) -> Tuple[Optional[str], Optional[str], Optional[float]]:
        ws = cls.calcular_wobbe(pcs_mj_m3, densitat_relativa)
        for familia, grup, ws_min, ws_max in cls.RANGES:
            if ws_min <= ws <= ws_max:
                return familia, grup, ws
        return None, None, ws

    @classmethod
    def obtenir_valors_estandard(cls, nom_tecnic: str) -> Optional[Dict[str, Any]]:
        return cls.VALORS_ESTANDARD.get(nom_tecnic)

    @classmethod
    def classificar_gas_complet(cls, hs_mj_m3: float, hi_mj_m3: float,
                                densitat_relativa: float) -> dict:
        familia, grup, ws = cls.classificar(hs_mj_m3, densitat_relativa)
        wi = cls.calcular_wobbe(hi_mj_m3, densitat_relativa) if hi_mj_m3 > 0 else 0.0
        designacio = cls.GAS_DESIGNACIONS.get((familia, grup))
        nom_tecnic = designacio[0] if designacio else None
        return {
            "ws_mj_m3": round(ws, 2) if ws else 0.0,
            "wi_mj_m3": round(wi, 2),
            "familia": familia or "No classificat",
            "grup": grup or "-",
            "dins_rang": familia is not None,
            "nom_tecnic": nom_tecnic,
            "designacio": f"{designacio[0]} - {designacio[1]}" if designacio else None,
        }
