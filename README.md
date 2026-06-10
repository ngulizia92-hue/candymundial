# 🏆 Candy Mundial — Prode del Mundial 2026

App web de prode (quiniela de pronósticos) hecha con Streamlit + SQLite.

## Cómo correr (local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre en `http://localhost:8501`.

## Cómo se usa

1. **Primer ingreso:** el primer usuario que se crea es el **admin**.
2. **Admin:** carga los partidos (fase, equipos, fecha/hora) y luego los resultados.
3. **Jugadores:** se registran con nombre + PIN y cargan su pronóstico de cada partido.
4. El pronóstico se **cierra automáticamente** cuando llega la hora de inicio del partido.

## Puntaje

| Acierto | Puntos |
|---|---|
| Resultado exacto (ej. 2-1) | 3 |
| Acertar ganador/empate (sin el marcador) | 1 |

Se ajusta en `database.py` (`PTS_EXACTO`, `PTS_GANADOR`).

## Deploy

- **Streamlit Community Cloud:** conectar este repo y elegir `app.py`.
- **EasyPanel / VPS:** correr con `streamlit run app.py --server.port 8501`.

> La base `prode.db` se crea sola al primer arranque y está en `.gitignore`.
