"""Candy Mundial — Prode del Mundial 2026 (Streamlit)."""
from datetime import datetime, date, time

import pandas as pd
import streamlit as st

import database as db
import fixture_2026

st.set_page_config(page_title="Candy Mundial 🏆", page_icon="🏆", layout="centered")

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
    return datetime.now() >= parse_dt(par["inicio"])


def resultado_txt(par):
    if par["goles_local"] is None:
        return "—"
    return f'{par["goles_local"]} - {par["goles_visitante"]}'


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
def vista_pronosticos(user):
    st.subheader("📝 Mis pronósticos")
    partidos = db.listar_partidos()
    if not partidos:
        st.info("Todavía no hay partidos cargados.")
        return

    mis = db.pronosticos_de(user["id"])

    for par in partidos:
        cierra = cerrado(par)
        pgl, pgv = mis.get(par["id"], (0, 0))
        etiqueta = f'{par["local"]} vs {par["visitante"]}  ·  {par["fase"]}  ·  {fmt_dt(par["inicio"])}'
        with st.container(border=True):
            st.markdown(f"**{etiqueta}**")
            if par["goles_local"] is not None:
                st.caption(f'Resultado final: {resultado_txt(par)}')
            if cierra:
                if par["id"] in mis:
                    st.caption(f"🔒 Cerrado · tu pronóstico: {pgl} - {pgv}")
                else:
                    st.caption("🔒 Cerrado · sin pronóstico")
            else:
                c1, c2, c3 = st.columns([2, 2, 1])
                ngl = c1.number_input(par["local"], 0, 20, pgl, key=f"gl_{par['id']}")
                ngv = c2.number_input(par["visitante"], 0, 20, pgv, key=f"gv_{par['id']}")
                if c3.button("Guardar", key=f"save_{par['id']}"):
                    db.guardar_pronostico(user["id"], par["id"], int(ngl), int(ngv))
                    st.toast("Guardado ✔")
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

    with st.expander("🏆 Cargar fixture Mundial 2026 (fase de grupos)", expanded=False):
        st.caption(
            "Carga los 72 partidos de la fase de grupos. No duplica si ya están. "
            "⚠️ Las fechas/horas son tentativas por jornada: ajustá la hora real de "
            "cada partido más abajo (de eso depende el cierre de pronósticos)."
        )
        if st.button("Cargar fixture oficial"):
            n = db.seed_partidos(fixture_2026.partidos_fase_grupos())
            st.success(f"Listo: {n} partidos nuevos cargados.")
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
