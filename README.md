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

## Resultados automáticos (API football-data.org)

La app puede traer el **fixture completo (grupos + eliminatorias) y los resultados**
automáticamente desde [football-data.org](https://www.football-data.org/).

1. Sacá un token gratuito en https://www.football-data.org/client/register
2. Cargalo como variable de entorno **`FOOTBALL_DATA_TOKEN`** (en EasyPanel: pestaña *Environment*).
3. En la app: **⚙️ Admin → 🔄 Sincronizar con la API → Sincronizar ahora**.

La sincronización es re-ejecutable: agrega partidos nuevos, completa los cruces de
eliminatorias a medida que se definen y carga los resultados de los partidos
terminados. Sin token, podés usar igual la carga manual ("fixture offline" + cargar
resultados a mano).

## Deploy en EasyPanel

1. **Create Service → App** y conectá este repo de GitHub (branch `main`).
2. **Build:** tipo **Dockerfile** (ya está en el repo, lo detecta solo).
3. **Domains / Proxy:** apuntá el puerto interno **8501**.
4. **Volumes (importante):** montá un volumen en **`/data`**.
   La base queda en `/data/prode.db` (var `PRODE_DB`), así **no se borra** en cada redeploy.
5. **Environment:** agregá `FOOTBALL_DATA_TOKEN=<tu_token>` para los resultados automáticos (opcional).
6. Deploy. Entrás por el dominio que te da EasyPanel; el **primer usuario que crees es admin**.

> Sin el volumen en `/data`, cada redeploy borra usuarios, partidos y pronósticos.

## Deploy alternativos

- **Streamlit Community Cloud:** conectar el repo y elegir `app.py`.
- **Local:** `streamlit run app.py`.
