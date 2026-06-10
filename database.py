"""Capa de datos del Prode (SQLite)."""
import os
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

# Ruta de la base. En EasyPanel apuntá PRODE_DB a un volumen persistente
# (ej. /data/prode.db) para que NO se borre en cada redeploy.
DB_PATH = Path(os.environ.get("PRODE_DB", Path(__file__).parent / "prode.db"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Puntos
PTS_EXACTO = 3   # acertás el resultado exacto (ej 2-1)
PTS_GANADOR = 1  # acertás quién gana / empate, pero no el marcador


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                pin_hash TEXT NOT NULL,
                es_admin INTEGER NOT NULL DEFAULT 0,
                creado TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS partidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fase TEXT NOT NULL DEFAULT 'Grupos',
                local TEXT NOT NULL,
                visitante TEXT NOT NULL,
                inicio TEXT NOT NULL,          -- ISO datetime (hora ARG), cierre de pronósticos
                goles_local INTEGER,           -- NULL hasta que se carga el resultado
                goles_visitante INTEGER,
                api_id INTEGER                 -- id del partido en football-data.org (NULL si es manual)
            );

            CREATE TABLE IF NOT EXISTS pronosticos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                partido_id INTEGER NOT NULL,
                goles_local INTEGER NOT NULL,
                goles_visitante INTEGER NOT NULL,
                actualizado TEXT NOT NULL,
                UNIQUE(usuario_id, partido_id),
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY(partido_id) REFERENCES partidos(id)
            );
            """
        )
        # Migración para bases creadas antes de la columna api_id
        cols = [r["name"] for r in c.execute("PRAGMA table_info(partidos)")]
        if "api_id" not in cols:
            c.execute("ALTER TABLE partidos ADD COLUMN api_id INTEGER")
        c.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_partidos_api "
            "ON partidos(api_id) WHERE api_id IS NOT NULL"
        )


def _hash(pin: str) -> str:
    return hashlib.sha256(pin.encode("utf-8")).hexdigest()


# ---------- usuarios ----------
def crear_usuario(nombre: str, pin: str, es_admin: bool = False):
    nombre = nombre.strip()
    with conn() as c:
        c.execute(
            "INSERT INTO usuarios(nombre, pin_hash, es_admin, creado) VALUES (?,?,?,?)",
            (nombre, _hash(pin), int(es_admin), datetime.now().isoformat()),
        )


def login(nombre: str, pin: str):
    with conn() as c:
        row = c.execute(
            "SELECT * FROM usuarios WHERE nombre = ? AND pin_hash = ?",
            (nombre.strip(), _hash(pin)),
        ).fetchone()
    return dict(row) if row else None


def hay_admin() -> bool:
    with conn() as c:
        return c.execute("SELECT 1 FROM usuarios WHERE es_admin=1 LIMIT 1").fetchone() is not None


def listar_usuarios():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT id, nombre, es_admin FROM usuarios ORDER BY nombre")]


# ---------- partidos ----------
def crear_partido(fase, local, visitante, inicio_iso):
    with conn() as c:
        c.execute(
            "INSERT INTO partidos(fase, local, visitante, inicio) VALUES (?,?,?,?)",
            (fase, local, visitante, inicio_iso),
        )


def editar_partido(pid, fase, local, visitante, inicio_iso):
    with conn() as c:
        c.execute(
            "UPDATE partidos SET fase=?, local=?, visitante=?, inicio=? WHERE id=?",
            (fase, local, visitante, inicio_iso, pid),
        )


def borrar_partido(pid):
    with conn() as c:
        c.execute("DELETE FROM pronosticos WHERE partido_id=?", (pid,))
        c.execute("DELETE FROM partidos WHERE id=?", (pid,))


def sync_partidos(lista):
    """Sincroniza con la API (match por api_id):
    - inserta partidos nuevos;
    - actualiza fase, equipos, inicio y resultado;
    - el resultado SOLO se escribe si la API lo trae finalizado (no pisa con None).
    Devuelve (nuevos, actualizados, con_resultado)."""
    nuevos = actualizados = con_resultado = 0
    with conn() as c:
        for p in lista:
            row = c.execute(
                "SELECT id FROM partidos WHERE api_id=?", (p["api_id"],)
            ).fetchone()
            # Adopta un partido cargado offline (sin api_id) que coincida en equipos,
            # incluso si el local/visitante quedó invertido (la API define el orden).
            if not row and p["local"] != "Por definir" and p["visitante"] != "Por definir":
                row = c.execute(
                    "SELECT id FROM partidos WHERE api_id IS NULL AND "
                    "((local=? AND visitante=?) OR (local=? AND visitante=?))",
                    (p["local"], p["visitante"], p["visitante"], p["local"]),
                ).fetchone()
            tiene_res = p["gl"] is not None and p["gv"] is not None
            if tiene_res:
                con_resultado += 1
            if row:
                if tiene_res:
                    c.execute(
                        "UPDATE partidos SET fase=?, local=?, visitante=?, inicio=?, "
                        "goles_local=?, goles_visitante=?, api_id=? WHERE id=?",
                        (p["fase"], p["local"], p["visitante"], p["inicio"], p["gl"], p["gv"], p["api_id"], row["id"]),
                    )
                else:
                    c.execute(
                        "UPDATE partidos SET fase=?, local=?, visitante=?, inicio=?, api_id=? WHERE id=?",
                        (p["fase"], p["local"], p["visitante"], p["inicio"], p["api_id"], row["id"]),
                    )
                actualizados += 1
            else:
                c.execute(
                    "INSERT INTO partidos(fase, local, visitante, inicio, goles_local, goles_visitante, api_id) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (p["fase"], p["local"], p["visitante"], p["inicio"],
                     p["gl"] if tiene_res else None, p["gv"] if tiene_res else None, p["api_id"]),
                )
                nuevos += 1
    return nuevos, actualizados, con_resultado


def borrar_todo_fixture():
    """Borra TODOS los partidos y pronósticos (para recargar limpio)."""
    with conn() as c:
        c.execute("DELETE FROM pronosticos")
        c.execute("DELETE FROM partidos")


def cargar_resultado(pid, gl, gv):
    with conn() as c:
        c.execute(
            "UPDATE partidos SET goles_local=?, goles_visitante=? WHERE id=?",
            (gl, gv, pid),
        )


def listar_partidos():
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM partidos ORDER BY inicio")]


def seed_partidos(lista):
    """Carga/actualiza partidos. Hace match por (local, visitante):
    - si ya existe, actualiza fase e inicio (no pisa el resultado cargado);
    - si no, lo inserta.
    Re-ejecutable sin duplicar. Devuelve (nuevos, actualizados)."""
    nuevos = actualizados = 0
    with conn() as c:
        for p in lista:
            row = c.execute(
                "SELECT id FROM partidos WHERE local=? AND visitante=?",
                (p["local"], p["visitante"]),
            ).fetchone()
            if row:
                c.execute(
                    "UPDATE partidos SET fase=?, inicio=? WHERE id=?",
                    (p["fase"], p["inicio"], row["id"]),
                )
                actualizados += 1
            else:
                c.execute(
                    "INSERT INTO partidos(fase, local, visitante, inicio) VALUES (?,?,?,?)",
                    (p["fase"], p["local"], p["visitante"], p["inicio"]),
                )
                nuevos += 1
    return nuevos, actualizados


# ---------- pronosticos ----------
def guardar_pronostico(usuario_id, partido_id, gl, gv):
    with conn() as c:
        c.execute(
            """INSERT INTO pronosticos(usuario_id, partido_id, goles_local, goles_visitante, actualizado)
               VALUES (?,?,?,?,?)
               ON CONFLICT(usuario_id, partido_id)
               DO UPDATE SET goles_local=excluded.goles_local,
                             goles_visitante=excluded.goles_visitante,
                             actualizado=excluded.actualizado""",
            (usuario_id, partido_id, gl, gv, datetime.now().isoformat()),
        )


def borrar_pronostico(usuario_id, partido_id):
    with conn() as c:
        c.execute(
            "DELETE FROM pronosticos WHERE usuario_id=? AND partido_id=?",
            (usuario_id, partido_id),
        )


def pronosticos_de(usuario_id):
    with conn() as c:
        rows = c.execute(
            "SELECT partido_id, goles_local, goles_visitante FROM pronosticos WHERE usuario_id=?",
            (usuario_id,),
        ).fetchall()
    return {r["partido_id"]: (r["goles_local"], r["goles_visitante"]) for r in rows}


# ---------- puntaje ----------
def _signo(gl, gv):
    return (gl > gv) - (gl < gv)  # 1 local, 0 empate, -1 visitante


def puntos_pronostico(pgl, pgv, rgl, rgv):
    if rgl is None or rgv is None:
        return None
    if pgl == rgl and pgv == rgv:
        return PTS_EXACTO
    if _signo(pgl, pgv) == _signo(rgl, rgv):
        return PTS_GANADOR
    return 0


def tabla_posiciones():
    partidos = {p["id"]: p for p in listar_partidos()}
    with conn() as c:
        usuarios = c.execute("SELECT id, nombre FROM usuarios").fetchall()
        pron = c.execute("SELECT * FROM pronosticos").fetchall()

    acc = {u["id"]: {"nombre": u["nombre"], "pts": 0, "exactos": 0, "jugados": 0} for u in usuarios}
    for p in pron:
        par = partidos.get(p["partido_id"])
        if not par:
            continue
        pts = puntos_pronostico(p["goles_local"], p["goles_visitante"], par["goles_local"], par["goles_visitante"])
        if pts is None:
            continue
        a = acc[p["usuario_id"]]
        a["pts"] += pts
        a["jugados"] += 1
        if pts == PTS_EXACTO:
            a["exactos"] += 1

    tabla = sorted(acc.values(), key=lambda x: (-x["pts"], -x["exactos"], x["nombre"]))
    return tabla
