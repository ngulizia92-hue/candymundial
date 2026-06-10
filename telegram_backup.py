"""Envío de backups del prode por Telegram.

Se usa de dos formas:
- desde la app (botón en Admin) para enviar un backup al instante;
- como script de cron diario en EasyPanel:  python telegram_backup.py

Requiere las variables de entorno:
  TELEGRAM_BOT_TOKEN  -> token del bot (lo da @BotFather)
  TELEGRAM_CHAT_ID    -> id del chat/grupo destino
"""
import os
import io
from datetime import datetime

import requests

_URL = "https://api.telegram.org/bot{token}/sendDocument"


def _conf():
    return (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip(),
        os.environ.get("TELEGRAM_CHAT_ID", "").strip(),
    )


def configurado():
    token, chat = _conf()
    return bool(token and chat)


def enviar_documento(nombre, contenido, caption=""):
    token, chat = _conf()
    if not (token and chat):
        raise RuntimeError("Faltan TELEGRAM_BOT_TOKEN y/o TELEGRAM_CHAT_ID.")
    r = requests.post(
        _URL.format(token=token),
        data={"chat_id": chat, "caption": caption},
        files={"document": (nombre, contenido)},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram rechazó el envío: {data}")
    return True


def enviar_backup():
    """Envía la base completa y los pronósticos en Excel por Telegram."""
    import database as db
    import pandas as pd

    fecha = datetime.now().strftime("%Y-%m-%d_%H%M")
    enviar_documento(
        f"prode_backup_{fecha}.db",
        db.backup_db_bytes(),
        f"🏆 Candy Mundial — backup {fecha}",
    )
    pron = db.exportar_pronosticos()
    if pron:
        csv = pd.DataFrame(pron).to_csv(index=False).encode("utf-8-sig")
        enviar_documento(
            f"pronosticos_{fecha}.csv", csv, "Pronósticos (CSV)"
        )
    return True


if __name__ == "__main__":
    enviar_backup()
    print("Backup enviado por Telegram.")
