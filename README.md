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

## Sincronización automática de resultados

Para que los resultados y la tabla se actualicen solos (sin apretar el botón),
configurá un **cron job** en EasyPanel que ejecute:
```
python sync_auto.py
```
- Programalo cada 30 min: `*/30 * * * *` (o como prefieras).
- Usa la misma base (`/data`) y la variable `FOOTBALL_DATA_TOKEN`.
- Trae el fixture y los resultados de los partidos terminados; no pisa nada cargado a mano.

## Backup automático por Telegram

La app puede mandar un respaldo (base `.db` + pronósticos en Excel) a un chat de Telegram.

**1. Crear el bot y obtener los datos:**
- Abrí Telegram, hablá con **@BotFather** → `/newbot` → te da el **token**.
- Mandale un mensaje a tu bot (o agregalo a un grupo y escribí algo).
- Obtené el **chat_id**: abrí `https://api.telegram.org/bot<TOKEN>/getUpdates` en el navegador y buscá `"chat":{"id":...}`.

**2. Variables de entorno en EasyPanel:**
```
TELEGRAM_BOT_TOKEN=<token de BotFather>
TELEGRAM_CHAT_ID=<id del chat o grupo>
```

**3. Envío manual:** en la app, **⚙️ Admin → 💾 Backup → Enviar backup por Telegram ahora**.

**4. Envío diario automático (cron en EasyPanel):**
- En el servicio, sección **Cron Jobs / Scheduled**, creá una tarea con el comando:
  ```
  python telegram_backup.py
  ```
- Programala a la hora que quieras (ej. `0 9 * * *` = 9:00 todos los días).
- Corre en el mismo contenedor, así que usa la misma base (`/data`) y las mismas variables.

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
