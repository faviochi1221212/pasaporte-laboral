"""Pruebas de M2: cálculos sin IA de app/calculo.py (spec 4, 6 y 6b)."""
import json
import logging
from pathlib import Path
from typing import Any

import pytest

from app import calculo, config, datos

# Datos fijos para A6 y A7: no dependen de la foto de data/.
OCUPACIONES: list[dict[str, Any]] = [
    {"codigo": "O", "nombre": "Origen", "tipo": "gente"},
    {"codigo": "A", "nombre": "Destino A", "tipo": "gente"},
    {"codigo": "B", "nombre": "Destino B", "tipo": "cosas"},
    {"codigo": "C", "nombre": "Destino C", "tipo": "cosas"},
    {"codigo": "D", "nombre": "Destino D", "tipo": "papeles"},
]


def competencia(codigo: str, perfil: str, etiqueta: str = "", icono: str = "caja") -> dict[str, Any]:
    return {
        "codigo": codigo,
        "perfil": perfil,
        "sello": {"icono": icono, "etiqueta": etiqueta or codigo},
    }


COMPETENCIAS = [
    competencia("O1", "O"),
    competencia("O2", "O"),
    competencia("A1", "A"),
    competencia("A2", "A"),
    competencia("B1", "B"),
    competencia("B2", "B"),
    competencia("B3", "B"),
    competencia("B4", "B"),
    competencia("C1", "C"),
    competencia("C2", "C"),
    competencia("D1", "D"),
]
DEMANDA = {
    "O": {"avisos": 10, "demanda": 1.0},
    "A": {"avisos": 5, "demanda": 0.5},
    "B": {"avisos": 10, "demanda": 1.0},
    "C": {"avisos": 2, "demanda": 0.2},
    "D": {"avisos": 0, "demanda": 0.0},
}
CURSOS = [
    {
        "id": "largo",
        "nombre": "Curso largo",
        "horas": 20,
        "url": "https://ejemplo.pe/largo",
        "cubre": [{"codigo": "B3", "alcance": "solo_teoria", "modulo": "M1", "se_lleva": "Teoría"}],
    },
    {
        "id": "corto",
        "nombre": "Curso corto",
        "horas": 4,
        "url": "https://ejemplo.pe/corto",
        "cubre": [
            {"codigo": "B3", "alcance": "completo", "modulo": "M2", "se_lleva": "Práctica"},
            {"codigo": "B4", "alcance": "completo", "modulo": "M3", "se_lleva": "Práctica"},
        ],
    },
]

RESPUESTAS = [
    "Trabajo 6 años de cajera en una bodega.",
    "Al cerrar, cuadro la caja y reviso el fondo.",
]


# --- normalizar y evidencia (spec 4, condición 2)


def test_a5_normalizar_quita_mayusculas_tildes_signos_y_espacios() -> None:
    assert calculo.normalizar("  ¡Cuadró   la CAJA, al cerrar!  ") == "cuadro la caja al cerrar"


def test_a5_evidencia_valida_comparando_sin_tildes_ni_signos() -> None:
    assert calculo.evidencia_valida("cuadró la caja", RESPUESTAS)


def test_a5_evidencia_debe_ser_palabras_completas() -> None:
    assert not calculo.evidencia_valida("caj", RESPUESTAS)


def test_a5_evidencia_vacia_no_vale() -> None:
    assert not calculo.evidencia_valida(" ¡! ", RESPUESTAS)


# --- otorgar_sellos (spec 4)


def test_a5_evidencia_inventada_se_descarta(caplog: pytest.LogCaptureFixture) -> None:
    propuestas = [{"codigo": "G2347002-1.E2", "evidencia": "cobro con Yape"}]
    with caplog.at_level(logging.INFO, logger="app.calculo"):
        sellos = calculo.otorgar_sellos(propuestas, RESPUESTAS, datos.COMPETENCIAS, set())
    assert sellos == []
    assert "G2347002-1.E2" in caplog.text
    assert "cobro con Yape" not in caplog.text


def test_a5_codigo_inexistente_se_descarta(caplog: pytest.LogCaptureFixture) -> None:
    propuestas = [{"codigo": "X9999999-1.E1", "evidencia": "cuadro la caja"}]
    with caplog.at_level(logging.INFO, logger="app.calculo"):
        sellos = calculo.otorgar_sellos(propuestas, RESPUESTAS, datos.COMPETENCIAS, set())
    assert sellos == []
    assert "X9999999-1.E1" in caplog.text


def test_hu04_sello_valido_guarda_codigo_etiqueta_icono_y_frase() -> None:
    propuestas = [{"codigo": "G2347002-1.E1", "evidencia": "reviso el fondo"}]
    sellos = calculo.otorgar_sellos(propuestas, RESPUESTAS, datos.COMPETENCIAS, set())
    assert sellos == [
        {
            "codigo": "G2347002-1.E1",
            "etiqueta": "Abre la caja",
            "icono": "caja",
            "evidencia": "reviso el fondo",
        }
    ]


def test_hu04_un_codigo_da_un_solo_sello() -> None:
    propuestas = [
        {"codigo": "G2347002-1.E1", "evidencia": "reviso el fondo"},
        {"codigo": "G2347002-1.E1", "evidencia": "bodega"},
    ]
    sellos = calculo.otorgar_sellos(propuestas, RESPUESTAS, datos.COMPETENCIAS, set())
    assert [s["evidencia"] for s in sellos] == ["reviso el fondo"]


def test_hu04_misma_etiqueta_gana_todos_sus_codigos_con_la_misma_frase() -> None:
    propuestas = [{"codigo": "G2347002-1.E3", "evidencia": "cuadro la caja"}]
    sellos = calculo.otorgar_sellos(propuestas, RESPUESTAS, datos.COMPETENCIAS, set())
    assert {s["codigo"]: s["evidencia"] for s in sellos} == {
        "G2347002-1.E3": "cuadro la caja",
        "I2555001-2.E4": "cuadro la caja",
    }


def test_hu04_sello_quitado_no_se_otorga() -> None:
    propuestas = [
        {"codigo": "G2347002-1.E1", "evidencia": "reviso el fondo"},
        {"codigo": "G2347002-1.E3", "evidencia": "cuadro la caja"},
    ]
    quitados = {"G2347002-1.E3", "I2555001-2.E4"}
    sellos = calculo.otorgar_sellos(propuestas, RESPUESTAS, datos.COMPETENCIAS, quitados)
    assert [s["codigo"] for s in sellos] == ["G2347002-1.E1"]


def test_hu04_quitar_un_codigo_quita_los_de_su_misma_etiqueta() -> None:
    propuestas = [{"codigo": "G2347002-1.E3", "evidencia": "cuadro la caja"}]
    sellos = calculo.otorgar_sellos(propuestas, RESPUESTAS, datos.COMPETENCIAS, {"G2347002-1.E3"})
    assert sellos == []


def test_a2_frase_de_la_pregunta_4_no_da_sello() -> None:
    relato = json.loads(
        (Path(__file__).parent / "relatos" / "jorge_almacen.json").read_text(encoding="utf-8")
    )
    todas = [t for r in relato["respuestas"] for t in (r["texto"], r.get("repregunta", ""))]
    de_1_a_3 = [
        t for r in relato["respuestas"] if r["n"] <= 3 for t in (r["texto"], r.get("repregunta", ""))
    ]
    propuestas = [{"codigo": "G2347002-1.E2", "evidencia": "les cobro y les doy el vuelto"}]
    # Con todas las respuestas la frase sí aparece; por eso solo se pasan las de 1 a 3.
    assert calculo.evidencia_valida("les cobro y les doy el vuelto", todas)
    assert calculo.otorgar_sellos(propuestas, de_1_a_3, datos.COMPETENCIAS, set()) == []


def test_hu04_agrupa_sellos_con_la_misma_etiqueta() -> None:
    propuestas = [
        {"codigo": "G2347002-1.E1", "evidencia": "reviso el fondo"},
        {"codigo": "G2347002-1.E3", "evidencia": "cuadro la caja"},
    ]
    sellos = calculo.otorgar_sellos(propuestas, RESPUESTAS, datos.COMPETENCIAS, set())
    assert calculo.agrupar_sellos(sellos) == [
        {
            "codigos": ["G2347002-1.E1"],
            "etiqueta": "Abre la caja",
            "icono": "caja",
            "evidencia": "reviso el fondo",
            "sirve_en": 1,
        },
        {
            "codigos": ["G2347002-1.E3", "I2555001-2.E4"],
            "etiqueta": "Cuadra la caja",
            "icono": "caja",
            "evidencia": "cuadro la caja",
            "sirve_en": 2,
        },
    ]


# --- afinidad (spec 6 y 6b caso 2)

SELLOS_A6 = {"O1", "A1", "B1", "B2", "C1"}


def a_mano(cobertura: float, interes: float, demanda: float) -> float:
    return 0.60 * cobertura + 0.25 * interes + 0.15 * demanda


def test_a6_orden_y_puntajes_coinciden_con_calculo_a_mano() -> None:
    destinos = calculo.afinidad(SELLOS_A6, "gente", "O", OCUPACIONES, COMPETENCIAS, DEMANDA)
    esperado = [
        ("A", a_mano(1 / 2, 1, 0.5)),  # 0,625
        ("B", a_mano(2 / 4, 0, 1.0)),  # 0,45
        ("C", a_mano(1 / 2, 0, 0.2)),  # 0,33
    ]
    assert [d["codigo"] for d in destinos] == [c for c, _ in esperado]
    for destino, (_, puntaje) in zip(destinos, esperado):
        assert destino["puntaje"] == pytest.approx(puntaje)


def test_a6_nunca_aparece_el_origen_ni_destinos_con_0_compartidos() -> None:
    destinos = calculo.afinidad(SELLOS_A6, "gente", "O", OCUPACIONES, COMPETENCIAS, DEMANDA)
    codigos = [d["codigo"] for d in destinos]
    assert "O" not in codigos
    assert "D" not in codigos


def test_a6_sin_origen_todos_los_perfiles_compiten_y_maximo_3() -> None:
    sellos = {"O1", "O2", "A1", "B1", "C1"}
    destinos = calculo.afinidad(sellos, "gente", None, OCUPACIONES, COMPETENCIAS, DEMANDA)
    # O: 1,0 · A: 0,625 · C: 0,60 × 1/2 + 0,15 × 0,2 = 0,33 · B: 0,60 × 1/4 + 0,15 × 1 = 0,30
    assert [d["codigo"] for d in destinos] == ["O", "A", "C"]
    assert len(destinos) == config.MAX_DESTINOS


def test_a6_empate_de_puntaje_gana_mayor_cobertura() -> None:
    ocupaciones = [
        {"codigo": "X", "nombre": "X", "tipo": "gente"},
        {"codigo": "Y", "nombre": "Y", "tipo": "cosas"},
    ]
    competencias = [competencia(f"X{i}", "X") for i in range(4)]
    competencias += [competencia(f"Y{i}", "Y") for i in range(2)]
    demanda = {"X": {"avisos": 0, "demanda": 0.0}, "Y": {"avisos": 2, "demanda": 2 / 3}}
    # X: 0,60 × 1/4 + 0,25 × 1 = 0,40 · Y: 0,60 × 1/2 + 0,15 × 2/3 = 0,40
    destinos = calculo.afinidad({"X0", "Y0"}, "gente", None, ocupaciones, competencias, demanda)
    assert destinos[0]["puntaje"] == pytest.approx(destinos[1]["puntaje"])
    assert [d["codigo"] for d in destinos] == ["Y", "X"]


def test_a6_empate_de_puntaje_y_cobertura_gana_mayor_demanda() -> None:
    ocupaciones = [
        {"codigo": "X", "nombre": "X", "tipo": "cosas"},
        {"codigo": "Y", "nombre": "Y", "tipo": "cosas"},
    ]
    competencias = [competencia("X0", "X"), competencia("Y0", "Y")]
    # La diferencia de demanda cambia el puntaje en menos de lo que se redondea.
    demanda = {"X": {"avisos": 1, "demanda": 0.10000}, "Y": {"avisos": 1, "demanda": 0.10001}}
    destinos = calculo.afinidad({"X0", "Y0"}, "cosas", None, ocupaciones, competencias, demanda)
    assert [d["codigo"] for d in destinos] == ["Y", "X"]


def test_hu13_cada_destino_guarda_su_sustento() -> None:
    destino = calculo.afinidad(SELLOS_A6, "gente", "O", OCUPACIONES, COMPETENCIAS, DEMANDA)[0]
    assert destino == {
        "codigo": "A",
        "nombre": "Destino A",
        "tienes": ["A1"],
        "cobertura": 0.5,
        "interes": 1,
        "demanda": 0.5,
        "puntaje": pytest.approx(0.625),
        "avisos_lima": 5,
    }


# --- faltantes y cursos (spec 6b casos 4 y 5)


def test_a7_faltante_sin_curso_dice_el_mensaje_exacto(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="app.calculo"):
        faltan = calculo.faltantes({"C1"}, "C", COMPETENCIAS, CURSOS, "1-2")
    assert faltan == [
        {
            "codigo": "C2",
            "etiqueta": "C2",
            "curso": None,
            "mensaje": "No encontramos un curso gratuito del MTPE que cubra esto",
        }
    ]
    assert "C2" in caplog.text


def test_hu08_faltante_con_curso_no_lleva_mensaje() -> None:
    faltan = calculo.faltantes({"B1", "B2"}, "B", COMPETENCIAS, CURSOS, "1-2")
    assert [f["codigo"] for f in faltan] == ["B3", "B4"]
    assert all(f["curso"] is not None and f["mensaje"] is None for f in faltan)


def test_hu07_si_no_falta_nada_la_lista_esta_vacia() -> None:
    assert calculo.faltantes({"A1", "A2"}, "A", COMPETENCIAS, CURSOS, "1-2") == []


def test_a7_si_hay_varios_cursos_gana_el_de_menos_horas() -> None:
    curso = calculo.curso_para("B3", "1-2", CURSOS)
    assert curso is not None
    assert curso["id"] == "corto"


def test_a7_curso_de_solo_teoria_devuelve_su_alcance() -> None:
    curso = calculo.curso_para("H2452001-1.E2", "3-5", datos.CURSOS)
    assert curso is not None
    assert curso["alcance"] == "solo_teoria"
    assert curso["modulo"] == "Gestión de inventarios y almacenamiento"


@pytest.mark.parametrize(
    ("codigo", "horas", "semanas"),
    [
        ("B3", "1-2", 3),  # 4 h / 1,5 = 2,67 → 3
        ("B3", "3-5", 1),  # 4 h / 4 = 1
        ("B3", "5+", 1),  # 4 h / 6 = 0,67 → 1
    ],
)
def test_a7_semanas_se_redondean_hacia_arriba(codigo: str, horas: str, semanas: int) -> None:
    curso = calculo.curso_para(codigo, horas, CURSOS)
    assert curso is not None
    assert curso["semanas"] == semanas


def test_a7_semanas_de_un_curso_de_20_horas() -> None:
    cursos = [CURSOS[0]]
    assert calculo.curso_para("B3", "1-2", cursos)["semanas"] == 14  # 13,3 → 14
    assert calculo.curso_para("B3", "3-5", cursos)["semanas"] == 5  # 5 exacto
    assert calculo.curso_para("B3", "5+", cursos)["semanas"] == 4  # 3,3 → 4


# --- avisos (spec 6b caso 5, HU-09)


def test_hu09_maximo_3_avisos_por_destino() -> None:
    avisos = [{"id": str(i), "perfil": "A"} for i in range(5)]
    resultado = calculo.avisos_para("A", avisos)
    assert [a["id"] for a in resultado["avisos"]] == ["0", "1", "2"]
    assert resultado["mensaje"] is None


def test_hu09_sin_avisos_dice_el_mensaje_exacto() -> None:
    resultado = calculo.avisos_para("B", [{"id": "1", "perfil": "A"}])
    assert resultado == {"avisos": [], "mensaje": "Hoy no hay avisos en Lima para esto"}
