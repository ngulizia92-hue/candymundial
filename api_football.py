"""Integración con football-data.org (v4) para el Mundial 2026.

Trae el fixture completo (grupos + eliminatorias) y los resultados a medida que
se juegan. El token se lee de la variable de entorno FOOTBALL_DATA_TOKEN.
"""
import os
import urllib.request
import json
from datetime import datetime
from zoneinfo import ZoneInfo

API_URL = "https://api.football-data.org/v4/competitions/WC/matches"
ART = ZoneInfo("America/Argentina/Buenos_Aires")

# Nombres de la API (inglés) -> español
EQUIPOS_ES = {
    "Algeria": "Argelia", "Argentina": "Argentina", "Australia": "Australia",
    "Austria": "Austria", "Belgium": "Bélgica", "Bosnia-Herzegovina": "Bosnia y Herzegovina",
    "Brazil": "Brasil", "Canada": "Canadá", "Cape Verde Islands": "Cabo Verde",
    "Colombia": "Colombia", "Congo DR": "RD Congo", "Croatia": "Croacia",
    "Curaçao": "Curazao", "Czechia": "Chequia", "Ecuador": "Ecuador",
    "Egypt": "Egipto", "England": "Inglaterra", "France": "Francia",
    "Germany": "Alemania", "Ghana": "Ghana", "Haiti": "Haití", "Iran": "Irán",
    "Iraq": "Irak", "Ivory Coast": "Costa de Marfil", "Japan": "Japón",
    "Jordan": "Jordania", "Mexico": "México", "Morocco": "Marruecos",
    "Netherlands": "Países Bajos", "New Zealand": "Nueva Zelanda", "Norway": "Noruega",
    "Panama": "Panamá", "Paraguay": "Paraguay", "Portugal": "Portugal",
    "Qatar": "Qatar", "Saudi Arabia": "Arabia Saudita", "Scotland": "Escocia",
    "Senegal": "Senegal", "South Africa": "Sudáfrica", "South Korea": "Corea del Sur",
    "Spain": "España", "Sweden": "Suecia", "Switzerland": "Suiza",
    "Tunisia": "Túnez", "Turkey": "Turquía", "United States": "Estados Unidos",
    "Uruguay": "Uruguay", "Uzbekistan": "Uzbekistán",
}

# Etapas eliminatorias
STAGE_ES = {
    "LAST_32": "16avos", "LAST_16": "Octavos", "QUARTER_FINALS": "Cuartos",
    "SEMI_FINALS": "Semifinal", "THIRD_PLACE": "3er puesto", "FINAL": "Final",
}

GRUPO_ES = {f"GROUP_{l}": f"Grupo {l}" for l in "ABCDEFGHIJKL"}


def _token():
    return os.environ.get("FOOTBALL_DATA_TOKEN", "").strip()


def hay_token():
    return bool(_token())


def _es(nombre):
    if not nombre:
        return "Por definir"
    return EQUIPOS_ES.get(nombre, nombre)


def _fase(m):
    stage = m.get("stage")
    if stage == "GROUP_STAGE":
        return GRUPO_ES.get(m.get("group"), "Grupos")
    return STAGE_ES.get(stage, stage or "—")


def _inicio_art(utc_iso):
    # "2026-06-11T19:00:00Z" (UTC) -> ART naive
    dt = datetime.fromisoformat(utc_iso.replace("Z", "+00:00"))
    return dt.astimezone(ART).replace(tzinfo=None).isoformat()


def _resultado(score):
    """Marcador que cuenta el prode: SOLO los 90 minutos (sin alargue ni penales).

    - Partidos con alargue/penales: se usa 'regularTime' (marcador a los 90').
    - Partidos regulares (grupos): la API trae 'regularTime' vacío y el marcador
      de los 90' está en 'fullTime' → se usa fullTime.
    """
    reg = score.get("regularTime") or {}
    if reg.get("home") is not None:
        return reg.get("home"), reg.get("away")
    ft = score.get("fullTime") or {}
    return ft.get("home"), ft.get("away")


def obtener_partidos():
    """Devuelve lista de dicts: api_id, fase, local, visitante, inicio (ART),
    gl, gv (None si no finalizó). Lanza excepción si falla la API/token."""
    token = _token()
    if not token:
        raise RuntimeError("Falta la variable de entorno FOOTBALL_DATA_TOKEN.")

    req = urllib.request.Request(API_URL, headers={"X-Auth-Token": token})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)

    out = []
    for m in data.get("matches", []):
        finalizado = m.get("status") == "FINISHED"
        gl, gv = _resultado(m.get("score") or {}) if finalizado else (None, None)
        out.append(
            {
                "api_id": m["id"],
                "fase": _fase(m),
                "local": _es(m["homeTeam"].get("name")),
                "visitante": _es(m["awayTeam"].get("name")),
                "inicio": _inicio_art(m["utcDate"]),
                "gl": gl,
                "gv": gv,
            }
        )
    return out
