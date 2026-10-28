"""Pruebas de M1: los datos de data/ cumplen las reglas de la spec 3 y 6b."""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from app import calculo, config

RAIZ = Path(__file__).resolve().parent.parent
DATA = RAIZ / "data"


def cargar(nombre: str) -> Any:
    return json.loads((DATA / nombre).read_text(encoding="utf-8"))


ocupaciones = cargar("ocupaciones.json")
competencias = cargar("competencias.json")
cursos = cargar("cursos.json")
avisos = cargar("avisos.json")
demanda = cargar("demanda.json")

# Spec 3: sellos por perfil.
SELLOS_POR_PERFIL = {
    "G2347002": 3,
    "H2452001": 3,
    "M2981001": 3,
    "I2555001": 7,
    "I2555002": 6,
    "I2556002": 4,
}

# Spec 3: íconos válidos de los sellos.
ICONOS_VALIDOS = {
    "caja",
    "cobro",
    "mercaderia",
    "limpieza",
    "revision",
    "maleta",
    "atencion",
    "registro",
    "habitacion",
    "mesa",
}

# Spec 6b: etiquetas que comparten dos elementos ("sirve en 2 trabajos").
ETIQUETAS_COMPARTIDAS = {
    frozenset({"G2347002-1.E3", "I2555001-2.E4"}),
    frozenset({"M2981001-1.E1", "I2555002-1.E1"}),
    frozenset({"M2981001-1.E2", "I2555002-1.E2"}),
}

# Spec 6b caso 5: qué curso cubre qué código y con cuántas horas.
COBERTURA_CURSOS = {
    "H2452001-1.E2": 20,
    "H2452001-1.E3": 20,
    "I2555001-2.E1": 4,
    "I2555002-3.E1": 4,
}


def test_m1_validar_datos_pasa() -> None:
    resultado = subprocess.run(
        [sys.executable, str(RAIZ / "scripts" / "validar_datos.py")],
        capture_output=True,
    )
    assert resultado.returncode == 0


def test_m1_hay_26_elementos_repartidos_por_perfil() -> None:
    assert len(competencias) == 26
    assert {o["codigo"] for o in ocupaciones} == set(SELLOS_POR_PERFIL)
    assert Counter(c["perfil"] for c in competencias) == SELLOS_POR_PERFIL


def test_m1_ocupaciones_tienen_tipo_origen_y_3_que_harias() -> None:
    assert {o["codigo"] for o in ocupaciones if o["origen"]} == {
        "G2347002",
        "H2452001",
        "M2981001",
    }
    for o in ocupaciones:
        assert o["tipo"] in ("gente", "cosas", "papeles")
        assert len(o["que_harias"]) == 3


def test_hu04_cada_elemento_tiene_texto_simple_y_sello() -> None:
    for c in competencias:
        assert c["texto_simple"].strip()
        assert c["sello"]["etiqueta"].strip()
        assert c["sello"]["icono"].strip()


def test_m1_iconos_estan_en_la_lista_valida() -> None:
    for c in competencias:
        assert c["sello"]["icono"] in ICONOS_VALIDOS, c["codigo"]


def test_m1_etiquetas_tienen_de_2_a_4_palabras() -> None:
    for c in competencias:
        assert 2 <= len(c["sello"]["etiqueta"].split()) <= 4, c["codigo"]


def test_hu04_etiquetas_repetidas_tienen_el_mismo_icono() -> None:
    iconos: dict[str, set[str]] = {}
    for c in competencias:
        iconos.setdefault(c["sello"]["etiqueta"], set()).add(c["sello"]["icono"])
    for etiqueta, usados in iconos.items():
        assert len(usados) == 1, etiqueta


def test_hu04_solo_se_juntan_las_etiquetas_de_la_spec() -> None:
    por_etiqueta: dict[str, set[str]] = {}
    for c in competencias:
        por_etiqueta.setdefault(c["sello"]["etiqueta"], set()).add(c["codigo"])
    compartidas = {frozenset(cods) for cods in por_etiqueta.values() if len(cods) > 1}
    assert compartidas == ETIQUETAS_COMPARTIDAS


def test_regla5_textos_visibles_sin_palabras_prohibidas() -> None:
    textos = [c["texto_simple"] for c in competencias]
    textos += [c["sello"]["etiqueta"] for c in competencias]
    textos += [t for o in ocupaciones for t in o["que_harias"]]
    for texto in textos:
        assert not calculo.tiene_palabra_prohibida(texto), texto


def test_hu08_cursos_cubren_lo_que_dice_la_spec() -> None:
    assert len(cursos) == 2
    cubre = {item["codigo"]: curso["horas"] for curso in cursos for item in curso["cubre"]}
    assert cubre == COBERTURA_CURSOS
    for curso in cursos:
        assert curso["url"].startswith("https://")


def test_hu08_logistica_solo_cubre_teoria() -> None:
    logistica = next(c for c in cursos if c["id"] == "logistica-360")
    assert {item["alcance"] for item in logistica["cubre"]} == {"solo_teoria"}


def test_m1_demanda_es_avisos_entre_el_maximo() -> None:
    perfiles = demanda["perfiles"]
    assert set(perfiles) == set(SELLOS_POR_PERFIL)
    maximo = max(p["avisos"] for p in perfiles.values())
    for codigo, p in perfiles.items():
        assert 0 <= p["demanda"] <= 1, codigo
        assert p["demanda"] == pytest.approx(p["avisos"] / maximo, abs=0.005), codigo


def test_hu09_hasta_3_avisos_por_perfil_con_que_piden() -> None:
    por_perfil = Counter(a["perfil"] for a in avisos)
    assert set(por_perfil) <= set(SELLOS_POR_PERFIL)
    assert all(n <= config.MAX_AVISOS for n in por_perfil.values())
    for a in avisos:
        assert 1 <= len(a["que_piden"]) <= 2, a["id"]
        assert a["url"].startswith("https://"), a["id"]
        assert a["empresa"] and a["distrito"] and a["cierre"], a["id"]
