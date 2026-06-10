"""Sincronizador automático interno.

Arranca un hilo en segundo plano que cada 30 minutos trae resultados desde la
API. Vive dentro de la app: no hace falta configurar ningún cron en EasyPanel.
El intervalo se puede cambiar con la variable SYNC_INTERVAL_SEG.
"""
import os
import threading
import time

INTERVALO = int(os.environ.get("SYNC_INTERVAL_SEG", "1800"))  # 30 min

_started = False
_lock = threading.Lock()


def _loop():
    import database as db
    import api_football

    while True:
        time.sleep(INTERVALO)
        try:
            if api_football.hay_token():
                n, a, r, limp = db.sync_partidos(api_football.obtener_partidos())
                print(f"[auto_sync] {n} nuevos, {a} actualizados, {r} con resultado, {limp} limpiados.")
        except Exception as e:  # nunca tirar el hilo
            print(f"[auto_sync] error: {e}")


def iniciar():
    """Arranca el hilo una sola vez por proceso."""
    global _started
    with _lock:
        if _started:
            return
        _started = True
    threading.Thread(target=_loop, daemon=True, name="auto-sync").start()
    print(f"[auto_sync] activo: sincroniza cada {INTERVALO}s")
