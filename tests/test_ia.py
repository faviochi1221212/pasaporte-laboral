"""Pruebas de M4 sin red: las 3 tareas del modelo con salidas falsas, y A1 a A4 y A12 en modo respaldo."""
from typing import Any

import pytest

import casos_ia
from app import config, datos, ia, qvac


class ModeloFalso:
    """Reemplaza qvac.llamar_tool: devuelve, en orden, cada salida (o lanza cada error)."""

    def __init__(self, *salidas: dict[str, Any] | Exception) -> None:
        self.salidas = list(salidas)
        self.llamadas: list[dict[str, Any]] = []

    def __call__(
        self, tarea: str, mensajes: list[dict[str, Any]], tool: dict[str, Any]
    ) -> dict[str, Any]:
        self.llamadas.append({"tarea": tarea, "mensajes": mensajes, "tool": tool})
        salida = self.salidas.pop(0)
        if isinstance(salida, Exception):
            raise salida
        return salida


@pytest.fixture
def modelo(monkeypatch: pytest.MonkeyPatch) -> Any:
    def instalar(*salidas: dict[str, Any] | Exception) -> ModeloFalso:
        falso = ModeloFalso(*salidas)
        monkeypatch.setattr(qvac, "llamar_tool", falso)
        return falso

    return instalar


def revision(
    reaccion: str = "¡6 años es harta experiencia!",
    suficiente: bool = True,
    menciona_actividad: bool = False,
    repregunta: str = "",
) -> dict[str, Any]:
    return {
        "reaccion": reaccion,
        "suficiente": suficiente,
        "menciona_actividad": menciona_actividad,
        "repregunta": repregunta,
    }


P2 = casos_ia.PREGUNTAS[2]
P4 = casos_ia.PREGUNTAS[4]
LARGA = "Cobro en efectivo y con Yape, y al final del día cuadro la caja."

# --- revisar_respuesta: reacción (A12)


def test_a12_reaccion_valida_se_usa(modelo: Any) -> None:
    modelo(revision())
    assert ia.revisar_respuesta(1, casos_ia.PREGUNTAS[1], "6 años", False)["reaccion"] == (
        "¡6 años es harta experiencia!"
    )


@pytest.mark.parametrize(
    "reaccion",
    [
        "Qué bueno que me cuentes todo esto porque así puedo conocerte mucho mejor hoy",
        "¡Eres muy competente en caja!",
        "Ya tienes casi un certificado",
        "¡Qué buena cajera certificada!",
        "Eso vale como una CERTIFICACIÓN",
        "",
    ],
)
def test_a12_reaccion_larga_o_con_palabra_prohibida_usa_la_fija(modelo: Any, reaccion: str) -> None:
    modelo(revision(reaccion=reaccion))
    assert ia.revisar_respuesta(2, P2, LARGA, False)["reaccion"] == config.TEXTO_REACCION_FIJA


# --- revisar_respuesta: repregunta (spec 5, reglas de la conversación)


def test_hu02_respuesta_suficiente_no_lleva_repregunta(modelo: Any) -> None:
    modelo(revision(suficiente=True, repregunta="¿Algo más?"))
    assert ia.revisar_respuesta(2, P2, LARGA, False)["repregunta"] is None


def test_a4_insuficiente_usa_la_repregunta_del_modelo(modelo: Any) -> None:
    modelo(revision(suficiente=False, repregunta="¿Qué cobras tú en la caja?"))
    assert ia.revisar_respuesta(2, P2, "de todo un poco", False)["repregunta"] == "¿Qué cobras tú en la caja?"


@pytest.mark.parametrize(
    "repregunta",
    ["", "¿Me puedes contar con mucho más detalle qué cosas haces tú en un día normal de trabajo?"],
)
def test_a4_repregunta_invalida_usa_la_fija_en_2_y_3(modelo: Any, repregunta: str) -> None:
    modelo(revision(suficiente=False, repregunta=repregunta))
    assert ia.revisar_respuesta(3, casos_ia.PREGUNTAS[3], "todo", False)["repregunta"] == (
        config.TEXTO_REPREGUNTA_FIJA
    )


def test_a4_repregunta_invalida_en_la_1_no_repregunta(modelo: Any) -> None:
    modelo(revision(suficiente=False, repregunta=""))
    assert ia.revisar_respuesta(1, casos_ia.PREGUNTAS[1], "harto", False)["repregunta"] is None


def test_a4_nunca_una_segunda_repregunta(modelo: Any) -> None:
    modelo(revision(suficiente=False, repregunta="¿Qué cobras tú?"))
    assert ia.revisar_respuesta(2, P2, "de todo un poco", True)["repregunta"] is None


@pytest.mark.parametrize(("menciona", "esperada"), [(True, "¿Y qué haces tú ahí?"), (False, None)])
def test_hu02_en_4_y_5_la_repregunta_es_y_que_haces_tu_ahi(
    modelo: Any, menciona: bool, esperada: str | None
) -> None:
    modelo(revision(suficiente=False, menciona_actividad=menciona, repregunta="¿Otra cosa?"))
    assert ia.revisar_respuesta(4, P4, "Ayudo a mi tío en el mercado.", False)["repregunta"] == esperada


# --- revisar_respuesta: reintento y respaldo (spec 5)


def test_m4_salida_invalida_se_reintenta_una_vez(modelo: Any) -> None:
    falso = modelo({"reaccion": 3}, revision())
    assert ia.revisar_respuesta(2, P2, LARGA, False)["reaccion"] == "¡6 años es harta experiencia!"
    assert len(falso.llamadas) == 2


def test_m4_sin_tool_dos_veces_usa_el_respaldo(modelo: Any) -> None:
    falso = modelo(qvac.ErrorSinTool("x"), qvac.ErrorSinTool("x"))
    resultado = ia.revisar_respuesta(2, P2, LARGA, False)
    assert resultado == {"reaccion": config.TEXTO_REACCION_FIJA, "repregunta": None}
    assert len(falso.llamadas) == 2


def test_m4_qvac_sin_respuesta_va_directo_al_respaldo(modelo: Any) -> None:
    falso = modelo(qvac.ErrorQvac("x"))
    ia.revisar_respuesta(2, P2, LARGA, False)
    assert len(falso.llamadas) == 1


@pytest.mark.parametrize(
    ("n", "texto", "esperada"),
    [
        (2, "de todo un poco", config.TEXTO_REPREGUNTA_FIJA),
        (3, "cuadrar la caja", config.TEXTO_REPREGUNTA_FIJA),
        (4, "un negocio", config.TEXTO_REPREGUNTA_FUERA_DEL_TRABAJO),
        (2, LARGA, None),
        (1, "6 años", None),
    ],
)
def test_m4_respaldo_repregunta_fija_si_hay_menos_de_6_palabras(
    modelo: Any, n: int, texto: str, esperada: str | None
) -> None:
    modelo(qvac.ErrorQvac("x"))
    resultado = ia.revisar_respuesta(n, casos_ia.PREGUNTAS[n], texto, False)
    assert resultado == {"reaccion": config.TEXTO_REACCION_FIJA, "repregunta": esperada}


def test_m4_respaldo_respeta_una_sola_repregunta(modelo: Any) -> None:
    modelo(qvac.ErrorQvac("x"))
    assert ia.revisar_respuesta(2, P2, "de todo", True)["repregunta"] is None


# --- extraer_perfil (spec 4 y 5)

MARIA = casos_ia.cargar_relato("maria_cajera")["respuestas"]
JORGE = casos_ia.cargar_relato("jorge_almacen")["respuestas"]


def test_m4_prompt_de_extraer_perfil_es_el_de_la_spec_con_los_26_elementos(modelo: Any) -> None:
    falso = modelo({"competencias": [], "fortalezas": []})
    ia.extraer_perfil(MARIA, datos.COMPETENCIAS)
    sistema = falso.llamadas[0]["mensajes"][0]["content"]
    assert sistema.startswith(
        "Eres un asistente del Ministerio de Trabajo del Perú. Lee lo que contó la persona y llama a "
        "extraer_perfil."
    )
    assert "compara cada cosa que cuenta la persona con toda la lista, no solo con su trabajo actual" in sistema
    assert (
        "En fortalezas va solo lo que no corresponde a ningún código de la lista, como lo que hace fuera "
        "del trabajo. No inventes nada." in sistema
    )
    for c in datos.COMPETENCIAS:
        assert c["codigo"] in sistema
        assert c["texto_simple"] in sistema
        assert all(criterio in sistema for criterio in c["criterios_clave"])


def test_m4_lista_agrupada_por_trabajo_con_titulo(modelo: Any) -> None:
    falso = modelo({"competencias": [], "fortalezas": []})
    ia.extraer_perfil(MARIA, datos.COMPETENCIAS)
    sistema = falso.llamadas[0]["mensajes"][0]["content"]
    for ocupacion in datos.OCUPACIONES:
        titulo = f"Trabajo: {ocupacion['nombre']} ({ocupacion['codigo']})"
        assert sistema.count(titulo) == 1, titulo
        grupo = sistema.split(titulo, 1)[1].split("\nTrabajo: ", 1)[0]
        for c in datos.COMPETENCIAS:
            assert (f"- {c['codigo']}: " in grupo) == (c["perfil"] == ocupacion["codigo"]), c["codigo"]


def test_a5_extraer_perfil_pasa_por_otorgar_sellos(modelo: Any) -> None:
    modelo(
        {
            "competencias": [
                {"codigo": "G2347002-1.E3", "evidencia": "Al final del día cuadro la caja"},
                {"codigo": "G2347002-1.E1", "evidencia": "abro la caja con mucho cariño"},
                {"codigo": "Z0000000-1.E1", "evidencia": "doy el vuelto"},
            ],
            "fortalezas": [],
        }
    )
    sellos = ia.extraer_perfil(MARIA, datos.COMPETENCIAS)["sellos"]
    assert [s["codigo"] for s in sellos] == ["G2347002-1.E3", "I2555001-2.E4"]


def test_a2_sellos_solo_de_las_respuestas_1_a_3(modelo: Any) -> None:
    modelo(
        {
            "competencias": [{"codigo": "G2347002-1.E2", "evidencia": "les cobro y les doy el vuelto"}],
            "fortalezas": [],
        }
    )
    assert ia.extraer_perfil(JORGE, datos.COMPETENCIAS)["sellos"] == []


def test_hu04_fortalezas_se_validan_contra_todas_las_respuestas(modelo: Any) -> None:
    modelo(
        {
            "competencias": [{"codigo": "G2347002-1.E3", "evidencia": "cuadro la caja"}],
            "fortalezas": [
                {"texto": "Enseña a compañeras nuevas", "evidencia": "A las chicas nuevas les enseño a usar la caja"},
                {"texto": "Organiza partidos", "evidencia": "organizo los partidos de fulbito"},
                {"texto": "Inventada", "evidencia": "toco guitarra en una banda"},
                {"texto": "Repetida", "evidencia": "Cuadro la caja"},
            ],
        }
    )
    fortalezas = ia.extraer_perfil(MARIA, datos.COMPETENCIAS)["fortalezas"]
    assert [f["texto"] for f in fortalezas] == ["Enseña a compañeras nuevas", "Organiza partidos"]


def test_hu04_una_sola_fortaleza_por_respuesta_contando_su_repregunta(modelo: Any) -> None:
    # "organizo los partidos…" es la respuesta 4 y "Armo los equipos…" su repregunta: cuentan como una.
    modelo(
        {
            "competencias": [],
            "fortalezas": [
                {"texto": "Organiza partidos de fulbito", "evidencia": "organizo los partidos de fulbito de mi barrio"},
                {"texto": "Arma equipos y cobra la cuota", "evidencia": "Armo los equipos, reservo la cancha"},
                {"texto": "Enseña a compañeras nuevas", "evidencia": "A las chicas nuevas les enseño a usar la caja"},
                {"texto": "Cocina para su familia", "evidencia": "Me gusta cocinar para mi familia"},
            ],
        }
    )
    fortalezas = ia.extraer_perfil(MARIA, datos.COMPETENCIAS)["fortalezas"]
    assert [f["texto"] for f in fortalezas] == [
        "Organiza partidos de fulbito",
        "Enseña a compañeras nuevas",
        "Cocina para su familia",
    ]


def test_m4_extraer_perfil_envia_las_respuestas_1_a_5(modelo: Any) -> None:
    falso = modelo({"competencias": [], "fortalezas": []})
    ia.extraer_perfil(MARIA, datos.COMPETENCIAS)
    usuario = falso.llamadas[0]["mensajes"][1]["content"]
    assert "Armo los equipos, reservo la cancha" in usuario
    assert "3 a 5 horas" not in usuario


def test_m4_extraer_perfil_sin_respuesta_valida_da_error(modelo: Any) -> None:
    modelo({"competencias": "no"}, qvac.ErrorSinTool("x"))
    with pytest.raises(ia.ErrorExtraccion):
        ia.extraer_perfil(MARIA, datos.COMPETENCIAS)


# --- extracción parcial (spec 5, HU-16)


def test_hu16_parcial_cuenta_sellos_agrupados_con_respuestas_1_a_3(modelo: Any) -> None:
    falso = modelo(
        {
            "competencias": [
                {"codigo": "G2347002-1.E1", "evidencia": "Abro mi caja"},
                {"codigo": "G2347002-1.E3", "evidencia": "cuadro la caja"},
            ],
            "fortalezas": [],
        }
    )
    assert ia.extraer_parcial(MARIA, datos.COMPETENCIAS) == {
        "sellos_ganados": 2,
        "etiquetas": ["Abre la caja", "Cuadra la caja"],
    }
    assert "fulbito" not in falso.llamadas[0]["mensajes"][1]["content"]


def test_a13_parcial_que_falla_devuelve_none(modelo: Any) -> None:
    modelo(qvac.ErrorQvac("x"))
    assert ia.extraer_parcial(MARIA, datos.COMPETENCIAS) is None


# --- redactar_resumen (spec 5, HU-10)

SELLOS = [
    {"codigos": ["G2347002-1.E1"], "etiqueta": "Abre la caja", "icono": "caja", "evidencia": "x", "sirve_en": 1},
    {"codigos": ["G2347002-1.E2"], "etiqueta": "Cobra y da vuelto", "icono": "cobro", "evidencia": "x", "sirve_en": 1},
    {"codigos": ["G2347002-1.E3", "I2555001-2.E4"], "etiqueta": "Cuadra la caja", "icono": "caja", "evidencia": "x", "sirve_en": 2},
    {"codigos": ["H2452001-1.E2"], "etiqueta": "Ordena mercadería", "icono": "mercaderia", "evidencia": "x", "sirve_en": 1},
]
RESPUESTA_1 = MARIA[0]["texto"]
PLANTILLA = (
    "Experiencia práctica en: abrir la caja: revisar el fondo de dinero y que los equipos funcionen; "
    "cobrar en efectivo, con tarjeta o con Yape y entregar lo comprado; cuadrar la caja al final del día."
)


def test_hu10_resumen_valido_del_modelo_con_anios(modelo: Any) -> None:
    resumen = "Cajera con 6 años de experiencia en supermercado. Abre, cobra y cuadra la caja."
    falso = modelo({"resumen": resumen, "anios": "6 años"})
    assert ia.redactar_resumen(SELLOS, RESPUESTA_1, datos.COMPETENCIAS) == {
        "resumen": resumen,
        "anios": "6 años",
    }
    usuario = falso.llamadas[0]["mensajes"][1]["content"]
    assert RESPUESTA_1 in usuario and "Ordena mercadería" in usuario


@pytest.mark.parametrize("anios", ["10 años", ""])
def test_hu10_anios_sin_evidencia_en_la_respuesta_1_es_null(modelo: Any, anios: str) -> None:
    modelo({"resumen": "Cajera de supermercado. Abre y cuadra la caja.", "anios": anios})
    assert ia.redactar_resumen(SELLOS, RESPUESTA_1, datos.COMPETENCIAS)["anios"] is None


@pytest.mark.parametrize(
    "resumen",
    [
        "Cajera con 6 años de experiencia.",
        "Cajera con 6 años. Cobra y cuadra. Ordena mercadería.",
        "Cajero certificado con 6 años. Cobra y cuadra la caja.",
        "Cajera certificada con 6 años. Cobra y cuadra la caja.",
        "Cajera con 6 años. Tiene certificación en caja.",
        "Cajera con 6 años. Es muy competente en caja.",
    ],
)
def test_hu10_resumen_invalido_usa_la_plantilla_sin_anios(modelo: Any, resumen: str) -> None:
    salida = {"resumen": resumen, "anios": "6 años"}
    modelo(salida, salida)
    assert ia.redactar_resumen(SELLOS, RESPUESTA_1, datos.COMPETENCIAS) == {
        "resumen": PLANTILLA,
        "anios": None,
    }


def test_hu10_plantilla_si_qvac_no_responde(modelo: Any) -> None:
    modelo(qvac.ErrorQvac("x"))
    assert ia.redactar_resumen(SELLOS, RESPUESTA_1, datos.COMPETENCIAS) == {
        "resumen": PLANTILLA,
        "anios": None,
    }


# --- A1 a A4 y A12 en modo respaldo, con los fixtures grabados contra QVAC real


@pytest.fixture
def respaldo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "QVAC_MODO", "respaldo")


@pytest.mark.parametrize("nombre", casos_ia.RELATOS_A1_A3)
def test_a1_a3_en_respaldo(respaldo: None, nombre: str) -> None:
    casos_ia.comprobar_a1_a3(nombre)


def test_a4_en_respaldo(respaldo: None) -> None:
    casos_ia.comprobar_a4()


@pytest.mark.parametrize("nombre", casos_ia.RELATOS_A1_A3)
def test_a12_en_respaldo(respaldo: None, nombre: str) -> None:
    casos_ia.comprobar_a12(nombre)
