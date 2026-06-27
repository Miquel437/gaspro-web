"""Càlcul hidràulic de canonades de gas (fórmula de Renouard)"""
import math
from typing import List, Tuple


class CalculadorHidraulic:
    MATERIALS: List[Tuple[str, float]] = [
        ("Coure 12x1 (10 int)", 10.0),
        ("Coure 15x1 (13 int)", 13.0),
        ("Coure 18x1 (16 int)", 16.0),
        ("Coure 22x1 (20 int)", 20.0),
        ("Coure 28x1.5 (25 int)", 25.0),
        ("Coure 35x1.5 (32 int)", 32.0),
        ("Coure 42x1.5 (39 int)", 39.0),
        ("Coure 54x1.5 (51 int)", 51.0),
        ("Acero DN25 (28 int)", 28.0),
        ("Acero DN32 (36 int)", 36.0),
        ("Acero DN40 (42 int)", 42.0)
    ]

    @classmethod
    def calcular_tram(cls, potencia_kw: float, longitud: float,
                      dp_limit_mbar: float, pcs_kwh_m3: float,
                      densitat_relativa: float, pressio_treball_mbar: float
                      ) -> dict:
        if potencia_kw <= 0 or longitud <= 0:
            return {"cabal": 0, "diam_int": 0, "tub": "-",
                    "dp_real": 0, "diam_teoric": 0, "velocitat": 0}

        cabal = potencia_kw / pcs_kwh_m3 if pcs_kwh_m3 > 0 else 0.0
        pressio_bar = pressio_treball_mbar / 1000.0
        d_teoric = 0.0

        if pressio_treball_mbar <= 150:
            numerador = 23200.0 * densitat_relativa * longitud * pow(cabal, 1.82)
            if dp_limit_mbar > 0:
                d_teoric = pow(numerador / dp_limit_mbar, 1 / 4.82)
        else:
            p1_abs = pressio_bar + 1.01325
            p2_abs_min = p1_abs - (dp_limit_mbar / 1000.0)
            numerador = 48.6 * densitat_relativa * longitud * pow(cabal, 1.82)
            den_p = pow(p1_abs, 2) - pow(p2_abs_min, 2)
            if den_p > 0:
                d_teoric = pow(numerador / den_p, 1 / 4.82)
            else:
                d_teoric = 10.0

        tub_escollit = ("Massa Gran", 999.0)
        dp_real = 0.0
        velocitat = 0.0

        for nom, d_int in cls.MATERIALS:
            if d_int >= d_teoric:
                tub_escollit = (nom, d_int)
                area_m2 = math.pi * pow(d_int / 2000.0, 2)
                factor_p = 1.01325 / (pressio_bar + 1.01325)
                cabal_real = cabal * factor_p
                if area_m2 > 0:
                    velocitat = (cabal_real / 3600.0) / area_m2

                if pressio_treball_mbar <= 150:
                    n = 23200.0 * densitat_relativa * longitud * pow(cabal, 1.82)
                    dp_real = n / pow(d_int, 4.82)
                else:
                    p1_abs = pressio_bar + 1.01325
                    n = 48.6 * densitat_relativa * longitud * pow(cabal, 1.82)
                    terme_dreta = n / pow(d_int, 4.82)
                    p2_quadrat = pow(p1_abs, 2) - terme_dreta
                    if p2_quadrat > 0:
                        dp_real = (p1_abs - math.sqrt(p2_quadrat)) * 1000.0
                break

        return {
            "cabal": round(cabal, 4),
            "diam_int": tub_escollit[1],
            "tub": tub_escollit[0],
            "dp_real": round(dp_real, 4),
            "diam_teoric": round(d_teoric, 2),
            "velocitat": round(velocitat, 2),
        }

    @classmethod
    def factor_simultaneitat_irc(cls, num_habitatges: int) -> float:
        if num_habitatges <= 1:
            return 1.0
        if num_habitatges <= 5:
            return 0.8
        if num_habitatges <= 10:
            return 0.7
        if num_habitatges <= 20:
            return 0.6
        return 0.5
