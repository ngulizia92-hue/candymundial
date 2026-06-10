"""Sincroniza fixture y resultados desde la API football-data.org.

Pensado para correr por cron en EasyPanel (ej. cada 30 min):
    python sync_auto.py

Usa la misma base (/data) y la misma variable FOOTBALL_DATA_TOKEN que la app.
"""
from datetime import datetime

import database as db
import api_football


def main():
    if not api_football.hay_token():
        print("[sync_auto] Falta la variable FOOTBALL_DATA_TOKEN. No se sincroniza.")
        return
    db.init_db()
    partidos = api_football.obtener_partidos()
    nuevos, act, conres, limp = db.sync_partidos(partidos)
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(
        f"[sync_auto {ahora}] {nuevos} nuevos, {act} actualizados, "
        f"{conres} con resultado final, {limp} limpiados."
    )


if __name__ == "__main__":
    main()
