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


def fmt_fecha_corta(iso):
    # "2026-06-11T..." -> "11/6"
    return f"{int(iso[8:10])}/{int(iso[5:7])}"


def fmt_hora(iso):
    return iso[11:16]  # "16:00"


def fmt_hora_corta(iso):
    # "16:00" -> "16h" ; "16:30" -> "16:30"
    hh, mm = iso[11:13], iso[14:16]
    return f"{int(hh)}h" if mm == "00" else f"{int(hh)}:{mm}"


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
def iniciar_sesion(u):
    """Guarda sesión en memoria y en la URL (token) para sobrevivir al refresh."""
    st.session_state.user = u
    if u.get("token"):
        st.query_params["t"] = u["token"]
    st.rerun()


def cerrar_sesion():
    st.session_state.pop("user", None)
    st.query_params.clear()
    st.rerun()


def restaurar_sesion():
    """Si hay token en la URL, re-loguea automáticamente."""
    if "user" in st.session_state:
        return
    t = st.query_params.get("t")
    if t:
        u = db.usuario_por_token(t)
        if u:
            st.session_state.user = u


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
                    iniciar_sesion(u)
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
_CSS_PRONO = """
<style>
/* Casillas de goles limpias (sin botones +/-) */
div[data-testid="stNumberInput"] button { display: none !important; }
div[data-testid="stNumberInput"] input {
    text-align: center; padding: 4px 2px; font-weight: 700;
}
div[data-testid="stNumberInput"] { min-width: 0; }

/* ---------- CELULAR ---------- */
@media (max-width: 640px) {
  /* La grilla de grupos pasa a 1 por fila (apila vertical) */
  [data-testid="stForm"] [data-testid="stHorizontalBlock"]:not([data-testid="stColumn"] [data-testid="stHorizontalBlock"]) {
    flex-direction: column !important;
  }
  /* Las filas de partido se mantienen en una sola línea horizontal */
  [data-testid="stColumn"] [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    flex-direction: row !important;
    gap: .1rem !important;
  }
  [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 0 !important;
  }
  /* Filas de partido más compactas (menos espacio vertical) */
  [data-testid="stColumn"] [data-testid="stHorizontalBlock"] {
    margin-bottom: 0 !important;
  }
  /* Tipografía y banderas más chicas para que entre todo */
  .eq-nombre { font-size: .76rem !important; }
  .eq-flag { height: 11px !important; }
  .meta { font-size: .68rem !important; }
  /* Casillas de goles más bajas y sin margen extra */
  div[data-testid="stNumberInput"] input {
    font-size: .82rem !important; padding: 2px 0 !important;
    min-height: 1.7rem !important; height: 1.7rem !important;
  }
  div[data-testid="stNumberInput"], div[data-testid="stElementContainer"] {
    margin-bottom: 0 !important;
  }
}
</style>
"""


def _equipo_html(pais, align):
    """Nombre + bandera (align 'right' = equipo local: nombre ... bandera)."""
    nombre = f"<span class='eq-nombre' style='font-weight:600;font-size:.9rem'>{flags.corto(pais)}</span>"
    bandera = flags.img(pais, h=13)
    contenido = f"{nombre}&nbsp;{bandera}" if align == "right" else f"{bandera}&nbsp;{nombre}"
    return (
        f"<div style='text-align:{align};line-height:1.7;white-space:nowrap;"
        f"overflow:hidden;text-overflow:ellipsis'>{contenido}</div>"
    )


def _meta_html(texto):
    return (
        f"<div class='meta' style='text-align:center;color:#8a93a6;font-size:.76rem;"
        f"line-height:1.7;white-space:nowrap'>{texto}</div>"
    )


def _fila_partido(par, mis, visibles):
    """Fila: [local] [fecha] [gl] : [gv] [hora] [visitante]."""
    lc, fc, gl_c, sep, gv_c, hc, vc = st.columns(
        [5, 1.7, 1.2, 0.3, 1.2, 1.7, 5], vertical_alignment="center"
    )
    lc.markdown(_equipo_html(par["local"], "right"), unsafe_allow_html=True)
    vc.markdown(_equipo_html(par["visitante"], "left"), unsafe_allow_html=True)
    fc.markdown(_meta_html(fmt_fecha_corta(par["inicio"])), unsafe_allow_html=True)
    hc.markdown(_meta_html(fmt_hora_corta(par["inicio"])), unsafe_allow_html=True)
    sep.markdown(_meta_html(":"), unsafe_allow_html=True)

    pid = par["id"]
    pron = mis.get(pid)
    jugado = par["goles_local"] is not None

    if not cerrado(par):
        gl_c.number_input(
            "gl", min_value=0, max_value=20, step=1,
            value=(pron[0] if pron else None),
            key=f"gl_{pid}", label_visibility="collapsed", placeholder="-",
        )
        gv_c.number_input(
            "gv", min_value=0, max_value=20, step=1,
            value=(pron[1] if pron else None),
            key=f"gv_{pid}", label_visibility="collapsed", placeholder="-",
        )
        visibles.append(pid)
    else:
        # Cerrado: muestro resultado real (si hay), o el pronóstico, o candado
        if jugado:
            izq, der = par["goles_local"], par["goles_visitante"]
        elif pron:
            izq, der = pron
        else:
            izq, der = "🔒", ""
        estilo = "text-align:center;font-weight:800;font-size:1rem"
        gl_c.markdown(f"<div style='{estilo}'>{izq}</div>", unsafe_allow_html=True)
        gv_c.markdown(f"<div style='{estilo}'>{der}</div>", unsafe_allow_html=True)
        if jugado and pron:
            pts = db.puntos_pronostico(pron[0], pron[1], par["goles_local"], par["goles_visitante"])
            color = {3: "#27c46b", 1: "#e0b528", 0: "#c0392b"}.get(pts, "#9aa")
            hc.markdown(
                _meta_html(f"<b style='color:{color}'>+{pts}</b><br>"
                           f"<span style='font-size:.68rem'>vos {pron[0]}-{pron[1]}</span>"),
                unsafe_allow_html=True,
            )


def _header_grupo(gkey, partidos):
    """Encabezado: letra + las selecciones con banderas (como la planilla)."""
    if gkey.startswith("Grupo "):
        letra = gkey.split(" ")[1]
        equipos, vistos = [], set()
        for p in partidos:
            for e in (p["local"], p["visitante"]):
                if e not in vistos and e != "Por definir":
                    vistos.add(e); equipos.append(e)
        chips = " · ".join(
            f"{flags.img(e, h=12)}&nbsp;{flags.corto(e)}" for e in equipos
        )
        return (
            f"<div style='display:flex;align-items:baseline;gap:.5rem'>"
            f"<span style='font-size:1.6rem;font-weight:800;color:#e0b528'>{letra}</span>"
            f"<span style='font-size:.9rem'>{chips}</span></div>"
        )
    return f"<div style='font-size:1.2rem;font-weight:800;color:#e0b528'>{gkey}</div>"


def vista_pronosticos(user):
    st.markdown(_CSS_PRONO, unsafe_allow_html=True)
    st.subheader("📝 Pronósticos")
    partidos = db.listar_partidos()
    if not partidos:
        st.info("Todavía no hay partidos cargados. (Admin → Sincronizar con la API)")
        return

    mis = db.pronosticos_de(user["id"])

    # --- selector de día ---
    dias = sorted({p["inicio"][:10] for p in partidos})
    opciones = ["Todos"] + dias
    sel = st.selectbox(
        "Día", opciones,
        format_func=lambda d: "Todos los partidos" if d == "Todos" else f"Día {fmt_dia(d)}",
    )
    mostrados = partidos if sel == "Todos" else [p for p in partidos if p["inicio"][:10] == sel]

    # --- agrupar por fase ---
    grupos = {}
    for p in mostrados:
        grupos.setdefault(p["fase"], []).append(p)
    claves = sorted(grupos.keys(), key=orden_fase)

    st.caption(
        "Cargá los goles y guardá al final. Para **anular** un pronóstico, dejá las dos "
        "casillas vacías y guardá. 🟢 +3 resultado exacto · 🟡 +1 ganador/empate."
    )

    visibles = []
    with st.form("form_prono"):
        for inicio in range(0, len(claves), 3):       # 3 grupos por fila
            cols = st.columns(3)
            for j, gkey in enumerate(claves[inicio:inicio + 3]):
                pgrupo = sorted(grupos[gkey], key=lambda p: p["inicio"])
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(_header_grupo(gkey, pgrupo), unsafe_allow_html=True)
                        st.markdown(
                            "<div style='color:#8a93a6;font-size:.72rem;letter-spacing:.05em;"
                            "margin:.3rem 0 .1rem'>PARTIDOS (HORA ARG)</div>",
                            unsafe_allow_html=True,
                        )
                        for par in pgrupo:
                            _fila_partido(par, mis, visibles)
        guardar = st.form_submit_button("💾 Guardar mis pronósticos", type="primary")

    if guardar:
        n = borrados = 0
        for pid in visibles:
            gl = st.session_state.get(f"gl_{pid}")
            gv = st.session_state.get(f"gv_{pid}")
            tenia = mis.get(pid)
            if gl is None and gv is None:
                if tenia:                       # vaciar ambos goles = anular pronóstico
                    db.borrar_pronostico(user["id"], pid)
                    borrados += 1
                continue
            if gl is None or gv is None:
                continue                        # medio cargado: se ignora
            if tenia != (gl, gv):
                db.guardar_pronostico(user["id"], pid, int(gl), int(gv))
                n += 1
        msg = f"Guardado ✔ ({n} actualizados"
        msg += f", {borrados} borrados)" if borrados else ")"
        st.success(msg)
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
                nuevos, act, conres, limp = db.sync_partidos(partidos)
                msg = (f"Sincronizado: {nuevos} nuevos, {act} actualizados, "
                       f"{conres} con resultado final.")
                if limp:
                    msg += f" Se limpiaron {limp} partidos viejos/duplicados."
                st.success(msg)
                st.rerun()
            except Exception as e:
                st.error(f"Error al sincronizar: {e}")

    st.caption(f"Partidos cargados: {len(db.listar_partidos())}")


# ---------------- main ----------------
restaurar_sesion()
if "user" not in st.session_state:
    pantalla_login()
else:
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"👤 **{user['nombre']}**")
        if user["es_admin"]:
            st.caption("Administrador")
        if st.button("Cerrar sesión"):
            cerrar_sesion()
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
