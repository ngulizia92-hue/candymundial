"""Fixture oficial del Mundial 2026 (fase de grupos).

Grupos definitivos post-repechaje (fuente: ESPN / cruce con Wikipedia e Infobae).
Los ENFRENTAMIENTOS son los reales; las fechas/horas son TENTATIVAS por jornada
(rango oficial 11-27 jun 2026) y conviene ajustarlas en el panel Admin con el
horario exacto de cada partido, ya que de eso depende el cierre de pronósticos.
"""

# Cada grupo: 4 selecciones en orden de bombo (pos 1 a 4).
GRUPOS = {
    "A": ["México", "Sudáfrica", "Corea del Sur", "República Checa"],
    "B": ["Canadá", "Bosnia y Herzegovina", "Catar", "Suiza"],
    "C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "D": ["Estados Unidos", "Paraguay", "Australia", "Turquía"],
    "E": ["Alemania", "Curazao", "Costa de Marfil", "Ecuador"],
    "F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
    "G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
    "I": ["Francia", "Senegal", "Irak", "Noruega"],
    "J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "K": ["Portugal", "R.D. del Congo", "Uzbekistán", "Colombia"],
    "L": ["Inglaterra", "Croacia", "Ghana", "Panamá"],
}

# Round-robin estándar FIFA por jornada (índices 0-3 dentro del grupo).
# Jornada -> lista de enfrentamientos (i, j)
JORNADAS = {
    1: [(0, 1), (2, 3)],
    2: [(0, 2), (3, 1)],
    3: [(3, 0), (1, 2)],
}

# Fecha/hora TENTATIVA por jornada (ISO). Ajustar en Admin con el calendario real.
FECHA_JORNADA = {
    1: "2026-06-15T16:00:00",
    2: "2026-06-21T16:00:00",
    3: "2026-06-26T16:00:00",
}


def partidos_fase_grupos():
    """Devuelve lista de dicts: fase, local, visitante, inicio (ISO)."""
    out = []
    for letra, equipos in GRUPOS.items():
        for jornada, cruces in JORNADAS.items():
            for i, j in cruces:
                out.append(
                    {
                        "fase": f"Grupo {letra} · J{jornada}",
                        "local": equipos[i],
                        "visitante": equipos[j],
                        "inicio": FECHA_JORNADA[jornada],
                    }
                )
    return out
