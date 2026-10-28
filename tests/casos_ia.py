"""Aserciones de A1 a A4 y A12 con los relatos inventados de tests/relatos/.

Las usan test_ia_qvac.py (QVAC real, graba fixtures) y test_ia.py (modo respaldo, lee esos fixtures).
"""
import json
from pathlib import Path
from typing import Any

from app import calculo, config, datos, ia

RELATOS = Path(__file__).parent / "relatos"

# Preguntas 1 a 5 del guion (config.GUION, copiado de docs/mockup/V3Guion.dc.html). La clave de
# cada fixture sale del texto de los mensajes: si cambian, hay que volver a grabar.
PREGUNTAS = {n: p["texto"] for n, p in config.GUION.items() if n <= 5}

RELATOS_A1_A3 = ["maria_cajera", "jorge_almacen", "rosa_limpieza"]


def cargar_relato(nombre: str) -> dict[str, Any]:
    return json.loads((RELATOS / f"{nombre}.json").read_text(encoding="utf-8"))


def textos(respuestas: list[dict[str, Any]], hasta: int) -> list[str]:
    """Textos de las respuestas 1 a `hasta`, con sus repreguntas."""
    return [
        t
        for r in respuestas
        if r["n"] <= hasta
        for t in (r["texto"], r.get("repregunta"))
        if t
    ]


def comprobar_a1_a3(nombre: str) -> None:
    """A1, A2 y A3: al menos la mitad de los sellos del origen, todos con evidencia textual."""
    relato = cargar_relato(nombre)
    esperado = relato["esperado"]
    perfil = ia.extraer_perfil(relato["respuestas"], datos.COMPETENCIAS)
    del_origen = {
        s["codigo"] for s in perfil["sellos"] if s["codigo"].startswith(esperado["perfil_origen"])
    }
    assert len(del_origen) >= esperado["minimo_sellos_del_origen"], perfil["sellos"]
    de_1_a_3 = textos(relato["respuestas"], 3)
    for sello in perfil["sellos"]:
        assert calculo.evidencia_valida(sello["evidencia"], de_1_a_3), sello
    todas = textos(relato["respuestas"], 5)
    for fortaleza in perfil["fortalezas"]:
        assert calculo.evidencia_valida(fortaleza["evidencia"], todas), fortaleza
    for palabra in esperado.get("fortalezas_deben_incluir", []):
        en_fortalezas = [
            f for f in perfil["fortalezas"] if palabra in calculo.normalizar(f["texto"] + " " + f["evidencia"])
        ]
        assert en_fortalezas, perfil["fortalezas"]
        assert all(palabra not in calculo.normalizar(s["evidencia"]) for s in perfil["sellos"])


def comprobar_a4() -> None:
    """A4: a una respuesta vaga se le repregunta una vez y nunca una segunda."""
    respuesta = cargar_relato("respuesta_vaga")["respuestas"][0]
    n, texto = respuesta["n"], respuesta["texto"]
    primera = ia.revisar_respuesta(n, PREGUNTAS[n], texto, ya_repregunto=False)
    assert primera["repregunta"]
    segunda = ia.revisar_respuesta(n, PREGUNTAS[n], texto, ya_repregunto=True)
    assert segunda["repregunta"] is None


def comprobar_a12(nombre: str) -> None:
    """A12: las reacciones del modelo a las preguntas 1 a 5 cumplen el límite y no son la fija."""
    for respuesta in cargar_relato(nombre)["respuestas"]:
        n = respuesta["n"]
        if n > 5:
            continue
        reaccion = ia.revisar_respuesta(n, PREGUNTAS[n], respuesta["texto"], ya_repregunto=False)["reaccion"]
        assert reaccion != config.TEXTO_REACCION_FIJA, (n, reaccion)
        assert len(reaccion.split()) <= config.MAX_PALABRAS_REACCION, reaccion
        assert not calculo.tiene_palabra_prohibida(reaccion), reaccion
