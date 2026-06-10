"""Banderas de las selecciones (imágenes de flagcdn.com, se ven igual en todos lados)."""

# país (en español, como se guarda) -> código flagcdn
COD = {
    "México": "mx", "Sudáfrica": "za", "Corea del Sur": "kr", "Chequia": "cz",
    "Canadá": "ca", "Bosnia y Herzegovina": "ba", "Qatar": "qa", "Suiza": "ch",
    "Brasil": "br", "Marruecos": "ma", "Haití": "ht", "Escocia": "gb-sct",
    "Estados Unidos": "us", "Paraguay": "py", "Australia": "au", "Turquía": "tr",
    "Alemania": "de", "Curazao": "cw", "Costa de Marfil": "ci", "Ecuador": "ec",
    "Países Bajos": "nl", "Japón": "jp", "Suecia": "se", "Túnez": "tn",
    "Bélgica": "be", "Egipto": "eg", "Irán": "ir", "Nueva Zelanda": "nz",
    "España": "es", "Cabo Verde": "cv", "Arabia Saudita": "sa", "Uruguay": "uy",
    "Francia": "fr", "Senegal": "sn", "Irak": "iq", "Noruega": "no",
    "Argentina": "ar", "Argelia": "dz", "Austria": "at", "Jordania": "jo",
    "Portugal": "pt", "RD Congo": "cd", "Uzbekistán": "uz", "Colombia": "co",
    "Inglaterra": "gb-eng", "Croacia": "hr", "Ghana": "gh", "Panamá": "pa",
}


# Nombres abreviados para la grilla (evitan que se corten)
CORTO = {
    "Bosnia y Herzegovina": "Bosnia", "Países Bajos": "P. Bajos",
    "Arabia Saudita": "Arabia S.", "Estados Unidos": "EE.UU.",
    "Corea del Sur": "Corea", "Costa de Marfil": "C. Marfil",
    "Nueva Zelanda": "N. Zelanda",
}


def corto(pais):
    return CORTO.get(pais, pais)


def img(pais, h=14):
    """Devuelve un <img> con la bandera (o un cuadrito gris si no se conoce)."""
    cod = COD.get(pais)
    if not cod:
        return (
            "<span style='display:inline-block;width:21px;height:14px;"
            "background:#444;border-radius:2px;vertical-align:middle'></span>"
        )
    return (
        f"<img src='https://flagcdn.com/h40/{cod}.png' "
        f"height='{h}' style='vertical-align:middle;border-radius:2px' alt=''>"
    )
