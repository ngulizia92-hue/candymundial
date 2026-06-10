"""Fixture oficial del Mundial 2026 — fase de grupos.

72 partidos con fecha y HORA DE ARGENTINA (ART), transcriptos del calendario
oficial. Grupos definitivos post-repechaje. Cada par de un grupo se enfrenta
una vez (verificado contra el round-robin de los 12 grupos).
"""

# (fase, local, visitante, inicio_iso_ART)
PARTIDOS = [
    # Grupo A
    ("Grupo A", "México", "Sudáfrica", "2026-06-11T16:00:00"),
    ("Grupo A", "Corea del Sur", "Chequia", "2026-06-11T23:00:00"),
    ("Grupo A", "México", "Corea del Sur", "2026-06-18T22:00:00"),
    ("Grupo A", "Sudáfrica", "Chequia", "2026-06-18T13:00:00"),
    ("Grupo A", "Chequia", "México", "2026-06-25T22:00:00"),
    ("Grupo A", "Sudáfrica", "Corea del Sur", "2026-06-25T22:00:00"),
    # Grupo B
    ("Grupo B", "Canadá", "Bosnia y Herzegovina", "2026-06-12T16:00:00"),
    ("Grupo B", "Qatar", "Suiza", "2026-06-13T16:00:00"),
    ("Grupo B", "Canadá", "Qatar", "2026-06-18T19:00:00"),
    ("Grupo B", "Suiza", "Bosnia y Herzegovina", "2026-06-18T16:00:00"),
    ("Grupo B", "Bosnia y Herzegovina", "Qatar", "2026-06-25T22:00:00"),
    ("Grupo B", "Canadá", "Suiza", "2026-06-25T22:00:00"),
    # Grupo C
    ("Grupo C", "Brasil", "Marruecos", "2026-06-13T19:00:00"),
    ("Grupo C", "Haití", "Escocia", "2026-06-13T22:00:00"),
    ("Grupo C", "Brasil", "Haití", "2026-06-19T21:00:00"),
    ("Grupo C", "Escocia", "Marruecos", "2026-06-19T19:00:00"),
    ("Grupo C", "Marruecos", "Haití", "2026-06-26T22:00:00"),
    ("Grupo C", "Escocia", "Brasil", "2026-06-26T22:00:00"),
    # Grupo D
    ("Grupo D", "Estados Unidos", "Paraguay", "2026-06-12T22:00:00"),
    ("Grupo D", "Australia", "Turquía", "2026-06-13T01:00:00"),
    ("Grupo D", "Estados Unidos", "Australia", "2026-06-19T16:00:00"),
    ("Grupo D", "Turquía", "Paraguay", "2026-06-19T01:00:00"),
    ("Grupo D", "Paraguay", "Australia", "2026-06-26T22:00:00"),
    ("Grupo D", "Turquía", "Estados Unidos", "2026-06-26T22:00:00"),
    # Grupo E
    ("Grupo E", "Alemania", "Curazao", "2026-06-14T14:00:00"),
    ("Grupo E", "Costa de Marfil", "Ecuador", "2026-06-14T20:00:00"),
    ("Grupo E", "Alemania", "Costa de Marfil", "2026-06-20T17:00:00"),
    ("Grupo E", "Ecuador", "Curazao", "2026-06-20T23:00:00"),
    ("Grupo E", "Curazao", "Costa de Marfil", "2026-06-25T16:00:00"),
    ("Grupo E", "Ecuador", "Alemania", "2026-06-25T16:00:00"),
    # Grupo F
    ("Grupo F", "Países Bajos", "Japón", "2026-06-14T17:00:00"),
    ("Grupo F", "Suecia", "Túnez", "2026-06-14T23:00:00"),
    ("Grupo F", "Países Bajos", "Suecia", "2026-06-20T14:00:00"),
    ("Grupo F", "Túnez", "Japón", "2026-06-20T01:00:00"),
    ("Grupo F", "Japón", "Suecia", "2026-06-25T22:00:00"),
    ("Grupo F", "Túnez", "Países Bajos", "2026-06-25T22:00:00"),
    # Grupo G
    ("Grupo G", "Bélgica", "Egipto", "2026-06-15T16:00:00"),
    ("Grupo G", "Irán", "Nueva Zelanda", "2026-06-15T22:00:00"),
    ("Grupo G", "Bélgica", "Irán", "2026-06-21T16:00:00"),
    ("Grupo G", "Nueva Zelanda", "Egipto", "2026-06-21T22:00:00"),
    ("Grupo G", "Egipto", "Irán", "2026-06-26T16:00:00"),
    ("Grupo G", "Nueva Zelanda", "Bélgica", "2026-06-26T16:00:00"),
    # Grupo H
    ("Grupo H", "España", "Cabo Verde", "2026-06-15T13:00:00"),
    ("Grupo H", "Arabia Saudita", "Uruguay", "2026-06-15T19:00:00"),
    ("Grupo H", "España", "Arabia Saudita", "2026-06-21T13:00:00"),
    ("Grupo H", "Uruguay", "Cabo Verde", "2026-06-21T19:00:00"),
    ("Grupo H", "Cabo Verde", "Arabia Saudita", "2026-06-26T16:00:00"),
    ("Grupo H", "Uruguay", "España", "2026-06-26T16:00:00"),
    # Grupo I
    ("Grupo I", "Francia", "Senegal", "2026-06-16T16:00:00"),
    ("Grupo I", "Irak", "Noruega", "2026-06-16T19:00:00"),
    ("Grupo I", "Francia", "Irak", "2026-06-22T18:00:00"),
    ("Grupo I", "Noruega", "Senegal", "2026-06-22T21:00:00"),
    ("Grupo I", "Senegal", "Irak", "2026-06-27T16:00:00"),
    ("Grupo I", "Noruega", "Francia", "2026-06-27T16:00:00"),
    # Grupo J
    ("Grupo J", "Argentina", "Argelia", "2026-06-16T22:00:00"),
    ("Grupo J", "Austria", "Jordania", "2026-06-16T01:00:00"),
    ("Grupo J", "Argentina", "Austria", "2026-06-22T14:00:00"),
    ("Grupo J", "Jordania", "Argelia", "2026-06-22T01:00:00"),
    ("Grupo J", "Argelia", "Austria", "2026-06-27T22:00:00"),
    ("Grupo J", "Jordania", "Argentina", "2026-06-27T22:00:00"),
    # Grupo K
    ("Grupo K", "Portugal", "RD Congo", "2026-06-17T14:00:00"),
    ("Grupo K", "Uzbekistán", "Colombia", "2026-06-17T23:00:00"),
    ("Grupo K", "Portugal", "Uzbekistán", "2026-06-23T14:00:00"),
    ("Grupo K", "Colombia", "RD Congo", "2026-06-23T23:00:00"),
    ("Grupo K", "RD Congo", "Uzbekistán", "2026-06-27T22:00:00"),
    ("Grupo K", "Colombia", "Portugal", "2026-06-27T22:00:00"),
    # Grupo L
    ("Grupo L", "Inglaterra", "Croacia", "2026-06-17T17:00:00"),
    ("Grupo L", "Ghana", "Panamá", "2026-06-17T20:00:00"),
    ("Grupo L", "Inglaterra", "Ghana", "2026-06-23T17:00:00"),
    ("Grupo L", "Panamá", "Croacia", "2026-06-23T20:00:00"),
    ("Grupo L", "Croacia", "Ghana", "2026-06-27T22:00:00"),
    ("Grupo L", "Panamá", "Inglaterra", "2026-06-27T22:00:00"),
]


def partidos_fase_grupos():
    """Devuelve lista de dicts: fase, local, visitante, inicio (ISO, hora ART)."""
    return [
        {"fase": f, "local": loc, "visitante": vis, "inicio": ini}
        for (f, loc, vis, ini) in PARTIDOS
    ]
