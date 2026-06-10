"""Candy Mundial — Prode del Mundial 2026 (Streamlit)."""
from datetime import datetime, date, time
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

# Todo el prode trabaja en hora de Argentina (las horas del fixture son ART).
ART = ZoneInfo("America/Argentina/Buenos_Aires")


def ahora_art():
    """Fecha/hora actual en Argentina, naive (para comparar con el fixture)."""
    return datetime.now(ART).replace(tzinfo=None)

import database as db
import fixture_2026
import api_football
import flags

st.set_page_config(
    page_title="Candy Mundial 🏆", page_icon="🏆",
    layout="wide", initial_sidebar_state="collapsed",
)

db.init_db()

# Selecciones (para los selectores; igual se puede escribir cualquier nombre).
SELECCIONES = [
    "Argentina", "Brasil", "Uruguay", "Chile", "Colombia", "Ecuador", "Paraguay",
    "Perú", "Bolivia", "Venezuela", "México", "Estados Unidos", "Canadá",
    "Costa Rica", "Panamá", "Honduras", "Jamaica", "España", "Francia",
    "Inglaterra", "Alemania", "Italia", "Portugal", "Países Bajos", "Bélgica",
    "Croacia", "Suiza", "Dinamarca", "Polonia", "Austria", "Serbia", "Escocia",
    "Gales", "Noruega", "Marruecos", "Senegal", "Nigeria", "Egipto", "Camerún",
    "Ghana", "Costa de Marfil", "Argelia", "Túnez", "Japón", "Corea del Sur",
    "Irán", "Arabia Saudita", "Catar", "Australia", "Nueva Zelanda",
]
FASES = ["Grupos", "16avos", "Octavos", "Cuartos", "Semifinal", "3er puesto", "Final"]


# ---------------- helpers ----------------
def parse_dt(iso):
    return datetime.fromisoformat(iso)


def fmt_dt(iso):
    return parse_dt(iso).strftime("%d/%m %H:%M")


def cerrado(par):
    return ahora_art() >= parse_dt(par["inicio"])


def resultado_txt(par):
    if par["goles_local"] is None:
        return "—"
    return f'{par["goles_local"]} - {par["goles_visitante"]}'


_ORDEN_ELIM = {"16avos": 1, "Octavos": 2, "Cuartos": 3, "Semifinal": 4, "3er puesto": 5, "Final": 6}


def orden_fase(f):
    """Grupos primero (A→L), después eliminatorias en orden."""
    if f.startswith("Grupo "):
        return (0, f)
    return (1, _ORDEN_ELIM.get(f, 9), f)


def fmt_dia(iso10):
    # "2026-06-11" -> "11/06"
    return f"{iso10[8:10]}/{iso10[5:7]}"


def fmt_hora(iso):
    return iso[11:16]  # "16:00"


def parse_marcador(s):
    """'2-1' o '2:1' -> (2,1); inválido/vacío -> None."""
    if not s:
        return None
    s = s.strip().replace(":", "-").replace(" ", "")
    parts = s.split("-")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


# ---------------- auth ----------------
def pantalla_login():
    st.title("🏆 Candy Mundial")
    st.caption("Prode del Mundial 2026")

    if not db.hay_admin():
        st.info("No hay administrador todavía. Creá el primer usuario (será admin).")
        with st.form("setup_admin"):
            nombre = st.text_input("Nombre de admin")
            pin = st.text_input("PIN", type="password")
            if st.form_submit_button("Crear admin") and nombre and pin:
                db.crear_usuario(nombre, pin, es_admin=True)
                st.success("Admin creado. Iniciá sesión.")
                st.rerun()
        return

    tab_login, tab_registro = st.tabs(["Ingresar", "Registrarme"])
    with tab_login:
        with st.form("login"):
            nombre = st.text_input("Nombre")
            pin = st.text_input("PIN", type="password")
            if st.form_submit_button("Ingresar"):
                u = db.login(nombre, pin)
                if u:
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Nombre o PIN incorrecto.")
    with tab_registro:
        with st.form("registro"):
            nombre = st.text_input("Tu nombre", key="r_nombre")
            pin = st.text_input("Elegí un PIN", type="password", key="r_pin")
            if st.form_submit_button("Crear cuenta") and nombre and pin:
                try:
                    db.crear_usuario(nombre, pin)
                    st.success("Cuenta creada. Ya podés ingresar.")
                except Exception:
                    st.error("Ese nombre ya existe.")


# ---------------- vistas ----------------
def _equipo_html(pais, align):
    """Nombre + bandera alineados (align 'right' = bandera a la derecha del nombre)."""
    nombre = f"<span style='font-weight:600;font-size:.9rem'>{flags.corto(pais)}</span>"
    bandera = flags.img(pais)
    if align == "right":   # equipo local: nombre ... bandera
        contenido = f"{nombre}&nbsp;{bandera}"
    else:                  # equipo visitante: bandera ... nombre
        contenido = f"{bandera}&nbsp;{nombre}"
    return (
        f"<div style='text-align:{align};line-height:2.1;white-space:nowrap;"
        f"overflow:hidden;text-overflow:ellipsis'>{contenido}</div>"
    )


def _fila_partido(par, mis, visibles):
    """Una fila de partido dentro de la tarjeta de grupo."""
    lc, mc, vc = st.columns([5, 2, 5], vertical_alignment="center")
    lc.markdown(_equipo_html(par["local"], "right"), unsafe_allow_html=True)
    vc.markdown(_equipo_html(par["visitante"], "left"), unsafe_allow_html=True)

    pid = par["id"]
    pron = mis.get(pid)
    jugado = par["goles_local"] is not None
    with mc:
        if not cerrado(par):
            # Editable: el usuario carga su pronóstico
            default = f"{pron[0]}-{pron[1]}" if pron else ""
            st.text_input(
                "marcador", value=default, key=f"m_{pid}",
                placeholder="0-0", label_visibility="collapsed",
            )
            st.markdown(
                f"<div style='text-align:center;color:#9aa;font-size:.72rem;white-space:nowrap'>{fmt_hora(par['inicio'])}</div>",
                unsafe_allow_html=True,
            )
            visibles.append(pid)
        else:
            # Cerrado: muestro resultado real (si hay) y el pronóstico del usuario
            centro = resultado_txt(par) if jugado else (f"{pron[0]}-{pron[1]}" if pron else "🔒")
            st.markdown(
                f"<div style='text-align:center;font-weight:700;font-size:1.05rem'>{centro}</div>",
                unsafe_allow_html=True,
            )
            if jugado:
                if pron:
                    pts = db.puntos_pronostico(pron[0], pron[1], par["goles_local"], par["goles_visitante"])
                    color = {3: "#27c46b", 1: "#e0b528", 0: "#c0392b"}.get(pts, "#9aa")
                    detalle = f"tuyo {pron[0]}-{pron[1]} · <b style='color:{color}'>+{pts}</b>"
                else:
                    detalle = "sin pronóstico"
            else:
                detalle = fmt_hora(par["inicio"])
            st.markdown(
                f"<div style='text-align:center;color:#9aa;font-size:.72rem;white-space:nowrap'>{detalle}</div>",
                unsafe_allow_html=True,
            )


def vista_pronosticos(user):
    st.subheader("📝 Pronósticos")
    partidos = db.listar_partidos()
    if not partidos:
        st.info("Todavía no hay partidos cargados. (Admin → Sincronizar con la API)")
        return

    mis = db.pronosticos_de(user["id"])

    # --- selector de día ---
    dias = sorted({p["inicio"][:10] for p in partidos})
    opciones = ["Todos"] + dias
    sel = st.radio(
        "Día", opciones, horizontal=True, label_visibility="collapsed",
        format_func=lambda d: "Todos" if d == "Todos" else fmt_dia(d),
    )
    mostrados = partidos if sel == "Todos" else [p for p in partidos if p["inicio"][:10] == sel]

    # --- agrupar por fase (Grupo A, ..., eliminatorias) ---
    grupos = {}
    for p in mostrados:
        grupos.setdefault(p["fase"], []).append(p)
    claves = sorted(grupos.keys(), key=orden_fase)

    st.caption("Cargá tu marcador en formato **2-1** y guardá al final. 🟢 +3 exacto · 🟡 +1 ganador.")

    visibles = []
    with st.form("form_prono"):
        for inicio in range(0, len(claves), 3):       # 3 grupos por fila
            cols = st.columns(3)
            for j, gkey in enumerate(claves[inicio:inicio + 3]):
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"#### {gkey}")
                        for par in sorted(grupos[gkey], key=lambda p: p["inicio"]):
                            _fila_partido(par, mis, visibles)
        guardar = st.form_submit_button("💾 Guardar mis pronósticos", type="primary")

    if guardar:
        n = 0
        for pid in visibles:
            m = parse_marcador(st.session_state.get(f"m_{pid}", ""))
            if m is None:
                continue
            actual = mis.get(pid)
            if actual != m:
                db.guardar_pronostico(user["id"], pid, m[0], m[1])
                n += 1
        st.success(f"Guardado ✔ ({n} pronóstico/s actualizados)")
        st.rerun()


def vista_tabla():
    st.subheader("🏅 Tabla de posiciones")
    tabla = db.tabla_posiciones()
    if not tabla:
        st.info("Sin datos todavía.")
        return
    df = pd.DataFrame(tabla)
    df.index = range(1, len(df) + 1)
    df = df.rename(columns={"nombre": "Jugador", "pts": "Puntos", "exactos": "Exactos", "jugados": "Jugados"})
    st.dataframe(df[["Jugador", "Puntos", "Exactos", "Jugados"]], use_container_width=True)


def vista_partidos():
    st.subheader("📅 Fixture")
    partidos = db.listar_partidos()
    if not partidos:
        st.info("Sin partidos.")
        return
    rows = [
        {
            "Fase": p["fase"],
            "Partido": f'{p["local"]} vs {p["visitante"]}',
            "Fecha": fmt_dt(p["inicio"]),
            "Resultado": resultado_txt(p),
        }
        for p in partidos
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def vista_admin():
    st.subheader("⚙️ Admin")

    with st.expander("🔄 Sincronizar con la API (recomendado)", expanded=True):
        st.caption(
            "Trae el fixture completo (grupos + eliminatorias) y los resultados "
            "de los partidos ya jugados desde football-data.org. Apretalo cuando "
            "quieras actualizar resultados; no pisa resultados con partidos sin terminar."
        )
        if not api_football.hay_token():
            st.warning(
                "Falta configurar la variable de entorno **FOOTBALL_DATA_TOKEN** "
                "en EasyPanel para usar la sincronización automática."
            )
        if st.button("Sincronizar ahora", disabled=not api_football.hay_token()):
            try:
                partidos = api_football.obtener_partidos()
                nuevos, act, conres = db.sync_partidos(partidos)
                st.success(
                    f"Sincronizado: {nuevos} nuevos, {act} actualizados, "
                    f"{conres} con resultado final."
                )
                st.rerun()
            except Exception as e:
                st.error(f"Error al sincronizar: {e}")

    with st.expander("🏆 Cargar fixture offline (sin API)", expanded=False):
        st.caption(
            "Carga los 72 partidos de la fase de grupos con fecha y hora de Argentina. "
            "Se puede volver a apretar para corregir fechas: no duplica y no pisa "
            "resultados ya cargados."
        )
        if st.button("Cargar / actualizar fixture oficial"):
            nuevos, act = db.seed_partidos(fixture_2026.partidos_fase_grupos())
            st.success(f"Listo: {nuevos} partidos nuevos, {act} actualizados.")
            st.rerun()

    with st.expander("➕ Cargar partido", expanded=False):
        with st.form("nuevo_partido"):
            fase = st.selectbox("Fase", FASES)
            c1, c2 = st.columns(2)
            local = c1.selectbox("Local", SELECCIONES, key="np_local")
            visitante = c2.selectbox("Visitante", SELECCIONES, index=1, key="np_visit")
            c3, c4 = st.columns(2)
            f = c3.date_input("Fecha", value=date.today())
            h = c4.time_input("Hora", value=time(16, 0))
            if st.form_submit_button("Crear partido"):
                inicio = datetime.combine(f, h).isoformat()
                db.crear_partido(fase, local, visitante, inicio)
                st.success("Partido creado.")
                st.rerun()

    st.markdown("##### Partidos cargados")
    for p in db.listar_partidos():
        with st.container(border=True):
            st.markdown(f'**{p["local"]} vs {p["visitante"]}** · {p["fase"]} · {fmt_dt(p["inicio"])}')
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            gl = c1.number_input("GL", 0, 20, p["goles_local"] or 0, key=f"rgl_{p['id']}")
            gv = c2.number_input("GV", 0, 20, p["goles_visitante"] or 0, key=f"rgv_{p['id']}")
            if c3.button("Guardar resultado", key=f"res_{p['id']}"):
                db.cargar_resultado(p["id"], int(gl), int(gv))
                st.toast("Resultado cargado ✔")
                st.rerun()
            if c4.button("🗑 Borrar", key=f"del_{p['id']}"):
                db.borrar_partido(p["id"])
                st.rerun()


# ---------------- main ----------------
if "user" not in st.session_state:
    pantalla_login()
else:
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"👤 **{user['nombre']}**")
        if user["es_admin"]:
            st.caption("Administrador")
        if st.button("Cerrar sesión"):
            del st.session_state.user
            st.rerun()
        st.divider()
        st.caption("Puntos: 3 exacto · 1 ganador/empate")

    tabs = ["📝 Pronósticos", "🏅 Posiciones", "📅 Fixture"]
    if user["es_admin"]:
        tabs.append("⚙️ Admin")
    seleccion = st.tabs(tabs)

    with seleccion[0]:
        vista_pronosticos(user)
    with seleccion[1]:
        vista_tabla()
    with seleccion[2]:
        vista_partidos()
    if user["es_admin"]:
        with seleccion[3]:
            vista_admin()
