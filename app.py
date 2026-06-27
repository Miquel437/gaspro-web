"""GasPro Web - Aplicació web de càlcul de canonades de gas"""
import os
import json
import logging

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS

from utils.gas_utils import GasClassifier
from utils.calculations import CalculadorHidraulic
from models.database import (
    init_db, get_gasos, get_aparells, add_aparell, delete_aparell,
    update_aparell, get_cataleg_elements, add_element, delete_element,
    save_project, list_projects, get_project, delete_project
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gaspro-secret-key-change-in-production")
CORS(app)

# Inicialitzar base de dades
init_db()


# =========== RUTES PRINCIPALS ===========

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculadora")
def calculadora():
    return render_template("calculadora.html", gasos=get_gasos())


@app.route("/cataleg")
def cataleg():
    return render_template("cataleg.html",
                           aparells=get_aparells(),
                           elements=get_cataleg_elements())


@app.route("/projectes")
def projectes():
    return render_template("projectes.html", projectes=list_projects())


# =========== API: CLASSIFICACIÓ DE GASOS ===========

@app.route("/api/classificar-gas", methods=["POST"])
def api_classificar_gas():
    data = request.get_json()
    pcs_mj = float(data.get("pcs_mj", 0))
    densitat = float(data.get("densitat", 0))
    hi_mj = pcs_mj * 0.9
    resultat = GasClassifier.classificar_gas_complet(pcs_mj, hi_mj, densitat)
    return jsonify(resultat)


@app.route("/api/gasos-estandard")
def api_gasos_estandard():
    """Retorna els valors estàndard dels gasos per al desplegable."""
    gasos = []
    for nom_tecnic, vals in GasClassifier.VALORS_ESTANDARD.items():
        gasos.append({
            "nom_tecnic": nom_tecnic,
            "desc": vals["desc"],
            "pcs_mj": vals["pcs_mj"],
            "pcs_kwh": vals["pcs_kwh"],
            "densitat": vals["densitat"]
        })
    return jsonify(gasos)


# =========== API: CÀLCUL HIDRÀULIC ===========

@app.route("/api/calcular-tram", methods=["POST"])
def api_calcular_tram():
    data = request.get_json()
    pot = float(data.get("potencia_kw", 0))
    longit = float(data.get("longitud", 0))
    dp_max = float(data.get("dp_max", 1.0))
    pcs = float(data.get("pcs_kwh", 0))
    dens = float(data.get("densitat", 0.6))
    pressio = float(data.get("pressio_mbar", 20))

    resultat = CalculadorHidraulic.calcular_tram(pot, longit, dp_max, pcs, dens, pressio)
    return jsonify(resultat)


@app.route("/api/calcular-xarxa", methods=["POST"])
def api_calcular_xarxa():
    """Rep una xarxa completa (nodes + trams) i la calcula."""
    data = request.get_json()
    trams = data.get("trams", [])
    pcs = float(data.get("pcs_kwh", 10.75))
    dens = float(data.get("densitat", 0.6))
    pressio = float(data.get("pressio_mbar", 20))
    dp_max = float(data.get("dp_max", 1.0))
    factor = float(data.get("factor_demanda", 1.0))

    # Calcula cada tram
    resultats = []
    for tram in trams:
        pot = float(tram.get("potencia_kw", 0)) * factor
        longit = float(tram.get("longitud", 1))
        r = CalculadorHidraulic.calcular_tram(pot, longit, dp_max, pcs, dens, pressio)
        resultats.append({
            "origen": tram.get("origen", ""),
            "desti": tram.get("desti", ""),
            "longitud": longit,
            **r
        })

    # Calcular DP acumulada
    dp_acum = 0.0
    for r in resultats:
        dp_acum += r["dp_real"]
        r["dp_acum"] = round(dp_acum, 4)

    return jsonify({"trams": resultats})


# =========== API: CATÀLEG D'APARELLS ===========

@app.route("/api/aparells", methods=["GET"])
def api_get_aparells():
    return jsonify(get_aparells())


@app.route("/api/aparells", methods=["POST"])
def api_add_aparell():
    data = request.get_json()
    new_id = add_aparell(
        data["nom"], data["tipus"], float(data["potencia_kw"]),
        data.get("fabricant", ""), data.get("model", ""),
        float(data.get("hores_dia", 0))
    )
    return jsonify({"id": new_id, "ok": True})


@app.route("/api/aparells/<int:id_ap>", methods=["PUT"])
def api_update_aparell(id_ap):
    data = request.get_json()
    update_aparell(id_ap, data["nom"], data["tipus"],
                   float(data["potencia_kw"]),
                   data.get("fabricant", ""), data.get("model", ""))
    return jsonify({"ok": True})


@app.route("/api/aparells/<int:id_ap>", methods=["DELETE"])
def api_delete_aparell(id_ap):
    delete_aparell(id_ap)
    return jsonify({"ok": True})


# =========== API: CATÀLEG D'ELEMENTS ===========

@app.route("/api/elements", methods=["GET"])
def api_get_elements():
    return jsonify(get_cataleg_elements())


@app.route("/api/elements", methods=["POST"])
def api_add_element():
    data = request.get_json()
    new_id = add_element(data["nom"], data["categoria"], data.get("descripcio", ""))
    return jsonify({"id": new_id, "ok": True})


@app.route("/api/elements/<int:id_el>", methods=["DELETE"])
def api_delete_element(id_el):
    delete_element(id_el)
    return jsonify({"ok": True})


# =========== API: PROJECTES ===========

@app.route("/api/projectes", methods=["GET"])
def api_list_projectes():
    return jsonify(list_projects())


@app.route("/api/projectes", methods=["POST"])
def api_save_project():
    data = request.get_json()
    nom = data.get("nom", "Projecte sense nom")
    dades = data.get("dades", {})
    new_id = save_project(nom, dades)
    return jsonify({"id": new_id, "ok": True})


@app.route("/api/projectes/<int:id_proj>", methods=["GET"])
def api_get_project(id_proj):
    proj = get_project(id_proj)
    if proj:
        return jsonify(proj)
    return jsonify({"error": "No trobat"}), 404


@app.route("/api/projectes/<int:id_proj>", methods=["DELETE"])
def api_delete_project(id_proj):
    delete_project(id_proj)
    return jsonify({"ok": True})


# =========== API: BATERIA DE BOMBONES ===========

@app.route("/api/calcular-bateria", methods=["POST"])
def api_calcular_bateria():
    """Calcula bateria de bombones de propà/butà."""
    data = request.get_json()
    gas = data.get("gas", "propa")
    potencia = float(data.get("potencia_kw", 24))
    hores = float(data.get("hores_dia", 12))
    temp = float(data.get("temperatura", 20))

    # Valors de referència
    if gas == "propa":
        pcs = 27.78  # kWh/m³
        dens_rel = 1.6
        bombones = {"11 kg": 11, "35 kg": 35}
    else:
        pcs = 32.22
        dens_rel = 2.0
        bombones = {"12.5 kg": 12.5, "35 kg": 35}

    cabal_h = potencia / pcs  # m³/h
    consum_diari = cabal_h * hores  # m³/dia

    resultats = []
    for nom_bot, kg in bombones.items():
        # Equivalència aproximada: 1 kg de gas ≈ 0.54 m³ de vapor
        m3_per_kg = 0.54
        m3_per_bombona = kg * m3_per_kg
        dies_durada = m3_per_bombona / consum_diari if consum_diari > 0 else 0
        num_bateria = max(1, round(7 / dies_durada)) if dies_durada > 0 else 1
        resultats.append({
            "bombona": nom_bot,
            "kg": kg,
            "m3_bombona": round(m3_per_bombona, 2),
            "consum_diari_m3": round(consum_diari, 2),
            "dies_durada": round(dies_durada, 1),
            "bateria_recomanada": num_bateria
        })

    return jsonify({
        "gas": gas,
        "potencia": potencia,
        "hores_dia": hores,
        "cabal_h": round(cabal_h, 3),
        "consum_diari": round(consum_diari, 2),
        "bombones": resultats
    })


# =========== INICI ===========

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
