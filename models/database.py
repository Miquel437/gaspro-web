"""Servei de base de dades per a GasPro Web - SQLite/PostgreSQL"""
import os
import sqlite3
import json
import logging
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Usar PostgreSQL si està configurat, sinó SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = "postgres" in DATABASE_URL


def get_connection():
    """Retorna una connexió a la base de dades."""
    if USE_POSTGRES:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        conn.autocommit = True
        return conn
    else:
        db_path = os.environ.get("SQLITE_PATH", "gaspro.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    """Crea les taules si no existeixen."""
    conn = get_connection()
    c = conn.cursor()

    if USE_POSTGRES:
        c.execute("""CREATE TABLE IF NOT EXISTS gasos (
            id SERIAL PRIMARY KEY,
            nom TEXT, pcs REAL, densitat REAL, pressio_mbar REAL,
            pcs_mj_m3 REAL, densitat_kg_m3 REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS aparells (
            id SERIAL PRIMARY KEY, nom TEXT, tipus TEXT, potencia_kw REAL,
            fabricant TEXT DEFAULT '', model_exacte TEXT DEFAULT '',
            hores_dia REAL DEFAULT 0.0, observacions TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS cataleg_elements (
            id SERIAL PRIMARY KEY, nom TEXT, categoria TEXT,
            descripcio TEXT, fabricant TEXT DEFAULT '',
            model TEXT DEFAULT '', observacions TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS projectes (
            id SERIAL PRIMARY KEY, nom TEXT, data TEXT,
            dades_json TEXT)""")
    else:
        c.execute("""CREATE TABLE IF NOT EXISTS gasos
            (id INTEGER PRIMARY KEY, nom TEXT, pcs REAL, densitat REAL,
             pressio_mbar REAL, pcs_mj_m3 REAL, densitat_kg_m3 REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS aparells
            (id INTEGER PRIMARY KEY, nom TEXT, tipus TEXT, potencia_kw REAL,
             fabricant TEXT DEFAULT '', model_exacte TEXT DEFAULT '',
             hores_dia REAL DEFAULT 0.0, observacions TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS cataleg_elements
            (id INTEGER PRIMARY KEY, nom TEXT, categoria TEXT,
             descripcio TEXT, fabricant TEXT DEFAULT '',
             model TEXT DEFAULT '', observacions TEXT DEFAULT '')""")
        c.execute("""CREATE TABLE IF NOT EXISTS projectes
            (id INTEGER PRIMARY KEY, nom TEXT, data TEXT, dades_json TEXT)""")

    _inserir_dades_base(c)
    conn.commit()
    conn.close()


def _inserir_dades_base(c):
    """Insereix dades per defecte si la taula està buida."""
    if USE_POSTGRES:
        c.execute("SELECT COUNT(*) AS count FROM gasos")
    else:
        c.execute("SELECT COUNT(*) AS count FROM gasos")
    if c.fetchone()['count'] == 0:
        gasos = [
            ('Gas Natural', 11.63, 0.6, 20.0, 41.9, 0.735),
            ('Butà', 32.22, 2.0, 36.0, 116.0, 2.5),
            ('Propà', 27.78, 1.6, 29.0, 100.0, 2.0),
        ]
        for g in gasos:
            if USE_POSTGRES:
                c.execute("INSERT INTO gasos (nom, pcs, densitat, pressio_mbar, pcs_mj_m3, densitat_kg_m3) VALUES (%s,%s,%s,%s,%s,%s)", g)
            else:
                c.execute("INSERT INTO gasos (nom, pcs, densitat, pressio_mbar, pcs_mj_m3, densitat_kg_m3) VALUES (?,?,?,?,?,?)", g)

    if USE_POSTGRES:
        c.execute("SELECT COUNT(*) AS count FROM aparells")
    else:
        c.execute("SELECT COUNT(*) AS count FROM aparells")
    if c.fetchone()['count'] == 0:
        aparells = [
            ('Saunier Duval ThemaCondens F 25', 'caldera', 25.0, 'Saunier Duval', 'TGC-25'),
            ('Junkers Cerapur Comfort 24', 'caldera', 24.0, 'Junkers', 'ZSB-24'),
            ('Baxi (Roca) Victoria Condens 24', 'caldera', 24.0, 'Baxi', 'VIC-24'),
            ('Placa Gas Balay 4 Focs', 'cuina', 7.5, 'Balay', '3B4-700'),
            ('Junkers Hydronext 15L', 'escalfador', 26.8, 'Junkers', 'WR-15'),
            ('Cointra Superlina 20L', 'escalfador', 28.0, 'Cointra', 'SL-20'),
            ('Roca Geneva 20', 'caldera', 20.0, 'Roca', 'GVA-20'),
        ]
        for a in aparells:
            if USE_POSTGRES:
                c.execute("INSERT INTO aparells (nom, tipus, potencia_kw, fabricant, model_exacte) VALUES (%s,%s,%s,%s,%s)", a)
            else:
                c.execute("INSERT INTO aparells (nom, tipus, potencia_kw, fabricant, model_exacte) VALUES (?,?,?,?,?)", a)

    if USE_POSTGRES:
        c.execute("SELECT COUNT(*) AS count FROM cataleg_elements")
    else:
        c.execute("SELECT COUNT(*) AS count FROM cataleg_elements")
    if c.fetchone()['count'] == 0:
        elements = [
            ('Connexió a xarxa (Escomesa)', 'origen', 'Connexió xarxa distribució'),
            ("Bateria d'ampolles", 'origen', 'Conjunt bombones'),
            ('Regulador 2a etapa', 'regulacio', "Regulador d'abonat"),
            ('Comptador de gas', 'regulacio', 'Equip de mesura'),
            ("Clau d'Abonat (C.A.)", 'valvula', 'Tall habitatge'),
            ("Clau d'Edifici (C.E.)", 'valvula', 'Tall general edifici'),
            ("Presa de pressió (P.T.)", 'accessori', "Proves d'estanquitat"),
            ('Passamurs', 'accessori', 'Protecció per travessar parets'),
        ]
        for el in elements:
            if USE_POSTGRES:
                c.execute("INSERT INTO cataleg_elements (nom, categoria, descripcio) VALUES (%s,%s,%s)", el)
            else:
                c.execute("INSERT INTO cataleg_elements (nom, categoria, descripcio) VALUES (?,?,?)", el)


# ---------- MÈTODES CRUD ----------

def get_gasos() -> List[dict]:
    conn = get_connection()
    if USE_POSTGRES:
        c = conn.cursor()
        c.execute("SELECT id, nom, pcs, densitat, pressio_mbar, pcs_mj_m3, densitat_kg_m3 FROM gasos ORDER BY nom")
    else:
        c = conn.cursor()
        c.execute("SELECT id, nom, pcs, densitat, pressio_mbar, pcs_mj_m3, densitat_kg_m3 FROM gasos ORDER BY nom")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_aparells() -> List[dict]:
    conn = get_connection()
    if USE_POSTGRES:
        c = conn.cursor()
        c.execute("SELECT id, nom, tipus, potencia_kw, fabricant, model_exacte, hores_dia FROM aparells ORDER BY tipus, nom")
    else:
        c = conn.cursor()
        c.execute("SELECT id, nom, tipus, potencia_kw, fabricant, model_exacte, hores_dia FROM aparells ORDER BY tipus, nom")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_aparell(nom: str, tipus: str, potencia: float, fabricant: str = "",
               model: str = "", hores: float = 0.0) -> int:
    conn = get_connection()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute("INSERT INTO aparells (nom, tipus, potencia_kw, fabricant, model_exacte, hores_dia) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
                  (nom, tipus, potencia, fabricant, model, hores))
        new_id = c.fetchone()['id']
    else:
        c.execute("INSERT INTO aparells (nom, tipus, potencia_kw, fabricant, model_exacte, hores_dia) VALUES (?,?,?,?,?,?)",
                  (nom, tipus, potencia, fabricant, model, hores))
        new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def delete_aparell(id_ap: int) -> None:
    conn = get_connection()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute("DELETE FROM aparells WHERE id=%s", (id_ap,))
    else:
        c.execute("DELETE FROM aparells WHERE id=?", (id_ap,))
    conn.commit()
    conn.close()


def update_aparell(id_ap: int, nom: str, tipus: str, potencia: float,
                   fabricant: str = "", model: str = "") -> None:
    conn = get_connection()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute("UPDATE aparells SET nom=%s, tipus=%s, potencia_kw=%s, fabricant=%s, model_exacte=%s WHERE id=%s",
                  (nom, tipus, potencia, fabricant, model, id_ap))
    else:
        c.execute("UPDATE aparells SET nom=?, tipus=?, potencia_kw=?, fabricant=?, model_exacte=? WHERE id=?",
                  (nom, tipus, potencia, fabricant, model, id_ap))
    conn.commit()
    conn.close()


def get_cataleg_elements() -> List[dict]:
    conn = get_connection()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute("SELECT id, nom, categoria, descripcio FROM cataleg_elements ORDER BY categoria, nom")
    else:
        c.execute("SELECT id, nom, categoria, descripcio FROM cataleg_elements ORDER BY categoria, nom")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_element(nom: str, categoria: str, descripcio: str = "") -> int:
    conn = get_connection()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute("INSERT INTO cataleg_elements (nom, categoria, descripcio) VALUES (%s,%s,%s) RETURNING id",
                  (nom, categoria, descripcio))
        new_id = c.fetchone()['id']
    else:
        c.execute("INSERT INTO cataleg_elements (nom, categoria, descripcio) VALUES (?,?,?)",
                  (nom, categoria, descripcio))
        new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def delete_element(id_el: int) -> None:
    conn = get_connection()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute("DELETE FROM cataleg_elements WHERE id=%s", (id_el,))
    else:
        c.execute("DELETE FROM cataleg_elements WHERE id=?", (id_el,))
    conn.commit()
    conn.close()


# ---------- PROJECTES ----------

def save_project(nom: str, dades: dict) -> int:
    import json, datetime
    conn = get_connection()
    c = conn.cursor()
    data_str = datetime.datetime.now().isoformat()
    dades_json = json.dumps(dades, ensure_ascii=False)
    if USE_POSTGRES:
        c.execute("INSERT INTO projectes (nom, data, dades_json) VALUES (%s,%s,%s) RETURNING id",
                  (nom, data_str, dades_json))
        new_id = c.fetchone()['id']
    else:
        c.execute("INSERT INTO projectes (nom, data, dades_json) VALUES (?,?,?)",
                  (nom, data_str, dades_json))
        new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def list_projects() -> List[dict]:
    conn = get_connection()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute("SELECT id, nom, data FROM projectes ORDER BY data DESC")
    else:
        c.execute("SELECT id, nom, data FROM projectes ORDER BY data DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_project(id_proj: int) -> Optional[dict]:
    conn = get_connection()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute("SELECT id, nom, data, dades_json FROM projectes WHERE id=%s", (id_proj,))
    else:
        c.execute("SELECT id, nom, data, dades_json FROM projectes WHERE id=?", (id_proj,))
    row = c.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["dades"] = json.loads(d["dades_json"])
        return d
    return None


def delete_project(id_proj: int) -> None:
    conn = get_connection()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute("DELETE FROM projectes WHERE id=%s", (id_proj,))
    else:
        c.execute("DELETE FROM projectes WHERE id=?", (id_proj,))
    conn.commit()
    conn.close()
