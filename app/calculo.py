"""Cálculos sin IA (spec 4, 6 y 6b). Funciones puras: reciben datos y devuelven datos."""
import logging
import math
import re
import unicodedata
from collections.abc import Iterable
from typing import Any

from app import config

logger = logging.getLogger(__name__)

Datos = list[dict[str, Any]]


def normalizar(texto: str) -> str:
    """Pasa a minúsculas y quita tildes, signos y espacios dobles."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn"
    )
    return " ".join(re.sub(r"[^\w\s]|_", " ", sin_tildes).split())


def evidencia_valida(frase: str, respuestas: Iterable[str]) -> bool:
    """La frase aparece tal cual, con palabras completas, en alguna respuesta (spec 4, condición 2)."""
    buscada = normalizar(frase)
    if not buscada:
        return False
    return any(f" {buscada} " in f" {normalizar(r)} " for r in respuestas)


def otorgar_sellos(
    propuestas: Datos, respuestas: list[str], competencias: Datos, quitados: set[str]
) -> Datos:
    """Da un sello por código con las 3 condiciones de la spec 4.

    respuestas = solo preguntas 1 a 3 (con sus repreguntas); las 4 y 5 solo dan fortalezas.
    Un código que gana su sello lo pasa, con la misma frase, a los códigos con su misma etiqueta,
    y quitar un código quita también los de su misma etiqueta.
    """
    por_codigo = {c["codigo"]: c for c in competencias}
    etiquetas_quitadas = {por_codigo[q]["sello"]["etiqueta"] for q in quitados if q in por_codigo}
    evidencias: dict[str, str] = {}
    for propuesta in propuestas:
        codigo, frase = propuesta["codigo"], propuesta["evidencia"]
        if codigo not in por_codigo:
            logger.info("sello descartado: %s, código inexistente", codigo)
            continue
        if not evidencia_valida(frase, respuestas):
            logger.info("sello descartado: %s, evidencia no textual", codigo)
            continue
        etiqueta = por_codigo[codigo]["sello"]["etiqueta"]
        for c in competencias:
            if c["sello"]["etiqueta"] == etiqueta:
                evidencias.setdefault(c["codigo"], frase)
    return [
        {
            "codigo": c["codigo"],
            "etiqueta": c["sello"]["etiqueta"],
            "icono": c["sello"]["icono"],
            "evidencia": evidencias[c["codigo"]],
        }
        for c in competencias
        if c["codigo"] in evidencias and c["sello"]["etiqueta"] not in etiquetas_quitadas
    ]


def agrupar_sellos(sellos: Datos) -> Datos:
    """Junta los sellos con la misma etiqueta en uno solo ("sirve en 2 trabajos", spec 6b caso 1)."""
    grupos: dict[str, dict[str, Any]] = {}
    for sello in sellos:
        grupo = grupos.setdefault(
            sello["etiqueta"],
            {
                "codigos": [],
                "etiqueta": sello["etiqueta"],
                "icono": sello["icono"],
                "evidencia": sello["evidencia"],
            },
        )
        grupo["codigos"].append(sello["codigo"])
    return [{**g, "sirve_en": len(g["codigos"])} for g in grupos.values()]


def afinidad(
    sellos: set[str],
    interes: str | None,
    origen: str | None,
    ocupaciones: Datos,
    competencias: Datos,
    demanda: dict[str, dict[str, Any]],
) -> Datos:
    """Hasta 3 destinos ordenados por puntaje, con desempate por cobertura y demanda (spec 6 y 6b)."""
    destinos = []
    for ocupacion in ocupaciones:
        codigo = ocupacion["codigo"]
        if codigo == origen:
            continue
        elementos = [c["codigo"] for c in competencias if c["perfil"] == codigo]
        tienes = [e for e in elementos if e in sellos]
        if not tienes:
            continue
        cobertura = len(tienes) / len(elementos)
        coincide = 1 if ocupacion["tipo"] == interes else 0
        dem = demanda[codigo]["demanda"]
        destinos.append(
            {
                "codigo": codigo,
                "nombre": ocupacion["nombre"],
                "tienes": tienes,
                "cobertura": cobertura,
                "interes": coincide,
                "demanda": dem,
                "puntaje": config.PESO_COBERTURA * cobertura
                + config.PESO_INTERES * coincide
                + config.PESO_DEMANDA * dem,
                "avisos_lima": demanda[codigo]["avisos"],
            }
        )
    destinos.sort(key=lambda d: (round(d["puntaje"], 4), d["cobertura"], d["demanda"]), reverse=True)
    return destinos[: config.MAX_DESTINOS]


def curso_para(codigo: str, horas_libres: str, cursos: Datos) -> dict[str, Any] | None:
    """El curso de menos horas que cubre el código, con las semanas que tomaría (spec 6b caso 5)."""
    opciones = [
        (curso, item) for curso in cursos for item in curso["cubre"] if item["codigo"] == codigo
    ]
    if not opciones:
        return None
    curso, item = min(opciones, key=lambda o: o[0]["horas"])
    return {
        "id": curso["id"],
        "nombre": curso["nombre"],
        "horas": curso["horas"],
        "url": curso["url"],
        "alcance": item["alcance"],
        "modulo": item["modulo"],
        "se_lleva": item["se_lleva"],
        "semanas": math.ceil(curso["horas"] / config.HORAS_POR_SEMANA[horas_libres]),
    }


def faltantes(
    sellos: set[str], destino: str, competencias: Datos, cursos: Datos, horas_libres: str
) -> Datos:
    """Elementos del destino que la persona no tiene, cada uno con su curso o el mensaje fijo."""
    resultado = []
    for c in competencias:
        if c["perfil"] != destino or c["codigo"] in sellos:
            continue
        curso = curso_para(c["codigo"], horas_libres, cursos)
        if curso is None:
            logger.info("faltante sin curso: %s", c["codigo"])
        resultado.append(
            {
                "codigo": c["codigo"],
                "etiqueta": c["sello"]["etiqueta"],
                "curso": curso,
                "mensaje": None if curso else config.TEXTO_SIN_CURSO,
            }
        )
    return resultado


def avisos_para(perfil: str, avisos: Datos) -> dict[str, Any]:
    """Los 3 primeros avisos del perfil, o el mensaje fijo si no hay (spec 6 y 6b caso 5)."""
    del_perfil = [a for a in avisos if a["perfil"] == perfil][: config.MAX_AVISOS]
    return {"avisos": del_perfil, "mensaje": None if del_perfil else config.TEXTO_SIN_AVISOS}
