"""Las 3 tareas del modelo (spec 5): revisar_respuesta, extraer_perfil y redactar_resumen.

El modelo conversa, extrae y redacta; todo lo que ve el usuario se valida aquí en código.
"""
import logging
import re
from collections.abc import Callable
from typing import Any

from app import calculo, config, qvac

logger = logging.getLogger(__name__)

Datos = list[dict[str, Any]]

PROMPT_REVISAR = (
    "Eres el asistente de empleo del Ministerio de Trabajo del Perú y conversas con una persona "
    "sobre su trabajo. Lee la pregunta y su respuesta y llama a revisar_respuesta. "
    "reaccion: una frase cálida de máximo 12 palabras sobre algo concreto que dijo la persona; "
    "no repitas la pregunta ni prometas nada. "
    "suficiente: true si cuenta al menos una tarea o actividad concreta. "
    "menciona_actividad: true si menciona alguna actividad que hace. "
    "repregunta: si no es suficiente, una pregunta corta de máximo 15 palabras para que cuente algo "
    "concreto; si es suficiente, déjala vacía. "
    "No uses palabras que empiecen con \"certific\" o \"competen\" (como certificado, certificación, "
    "competente o competencia), ni \"brecha\" ni \"no sirves\"."
)

PROMPT_EXTRAER = (
    "Eres un asistente del Ministerio de Trabajo del Perú. Lee lo que contó la persona y llama a "
    "extraer_perfil. Usa solo códigos de la lista. Para cada competencia, copia como evidencia la "
    "frase exacta que la persona escribió; si no hay frase exacta, no la incluyas. Lo que hace fuera "
    "de su trabajo, y lo que hace en su trabajo que no está en la lista, va en fortalezas, nunca en "
    "competencias. No inventes nada."
)

PROMPT_RESUMEN = (
    "Eres un asistente del Ministerio de Trabajo del Perú. Escribe exactamente 2 frases cortas para "
    "el perfil de un CV y llama a redactar_resumen. Usa solo las tareas y la respuesta que te paso; "
    "no inventes nada. No uses palabras que empiecen con \"certific\" o \"competen\" (como "
    "certificado, certificación, competente o competencia), ni \"brecha\" ni \"no sirves\"."
)


def _tool(nombre: str, descripcion: str, propiedades: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": nombre,
            "description": descripcion,
            "parameters": {"type": "object", "properties": propiedades, "required": list(propiedades)},
        },
    }


def _lista_de(propiedades: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "array",
        "items": {"type": "object", "properties": propiedades, "required": list(propiedades)},
    }


TOOL_REVISAR = _tool(
    "revisar_respuesta",
    "Reacciona a la respuesta y dice si hace falta repreguntar.",
    {
        "reaccion": {"type": "string"},
        "suficiente": {"type": "boolean"},
        "menciona_actividad": {"type": "boolean"},
        "repregunta": {"type": "string"},
    },
)
TOOL_EXTRAER = _tool(
    "extraer_perfil",
    "Guarda las competencias de la lista y las fortalezas, cada una con la frase exacta de la persona.",
    {
        "competencias": _lista_de({"codigo": {"type": "string"}, "evidencia": {"type": "string"}}),
        "fortalezas": _lista_de({"texto": {"type": "string"}, "evidencia": {"type": "string"}}),
    },
)
TOOL_RESUMEN = _tool(
    "redactar_resumen",
    "Guarda las 2 frases del perfil del CV.",
    {"resumen": {"type": "string"}},
)


class ErrorExtraccion(Exception):
    """No se pudo leer el relato: la pantalla muestra TEXTO_ERROR_EXTRACCION."""


# --- validación


def _texto_valido(texto: str, max_palabras: int) -> bool:
    return 0 < len(texto.split()) <= max_palabras and not calculo.tiene_palabra_prohibida(texto)


def _lista_valida(valor: Any, campos: tuple[str, ...]) -> bool:
    return isinstance(valor, list) and all(
        isinstance(item, dict) and all(isinstance(item.get(c), str) for c in campos) for item in valor
    )


def _revision_valida(args: dict[str, Any]) -> bool:
    return (
        isinstance(args.get("reaccion"), str)
        and isinstance(args.get("suficiente"), bool)
        and isinstance(args.get("menciona_actividad"), bool)
        and isinstance(args.get("repregunta"), str)
    )


def _perfil_valido(args: dict[str, Any]) -> bool:
    return _lista_valida(args.get("competencias"), ("codigo", "evidencia")) and _lista_valida(
        args.get("fortalezas"), ("texto", "evidencia")
    )


def _resumen_valido(args: dict[str, Any]) -> bool:
    resumen = args.get("resumen")
    if not isinstance(resumen, str):
        return False
    frases = [f for f in re.split(r"[.!?]+", resumen) if f.strip()]
    return len(frases) == 2 and not calculo.tiene_palabra_prohibida(resumen)


def _llamar(
    tarea: str, mensajes: Datos, tool: dict[str, Any], valida: Callable[[dict[str, Any]], bool]
) -> dict[str, Any] | None:
    """Llama al modelo con un solo reintento si la salida no es válida; None si hay que usar el respaldo."""
    for intento in (1, 2):
        try:
            args = qvac.llamar_tool(tarea, mensajes, tool)
        except qvac.ErrorSinTool:
            logger.warning("%s: intento %d sin tool", tarea, intento)
            continue
        except qvac.ErrorQvac as e:
            logger.warning("%s: QVAC sin respuesta (%s), se usa el respaldo", tarea, type(e).__name__)
            return None
        if valida(args):
            return args
        logger.warning("%s: intento %d con salida fuera del esquema", tarea, intento)
    logger.warning("%s: se usa el respaldo", tarea)
    return None


def _textos(respuestas: Datos, hasta: int) -> list[str]:
    """Textos de las respuestas 1 a `hasta`, con sus repreguntas."""
    return [
        texto
        for r in respuestas
        if r["n"] <= hasta
        for texto in (r["texto"], r.get("repregunta"))
        if texto
    ]


# --- revisar_respuesta


def revisar_respuesta(n: int, pregunta: str, respuesta: str, ya_repregunto: bool) -> dict[str, Any]:
    """Reacción y repregunta (o None) para la respuesta a una de las preguntas 1 a 5."""
    mensajes = [
        {"role": "system", "content": PROMPT_REVISAR},
        {"role": "user", "content": f"Pregunta: {pregunta}\nRespuesta: {respuesta}"},
    ]
    args = _llamar("revisar_respuesta", mensajes, TOOL_REVISAR, _revision_valida)
    fuera_del_trabajo = n in (4, 5)
    if args is None:
        reaccion = config.TEXTO_REACCION_FIJA
        corta = n >= 2 and len(respuesta.split()) < config.MIN_PALABRAS
        if not corta:
            repregunta = None
        elif fuera_del_trabajo:
            repregunta = config.TEXTO_REPREGUNTA_FUERA_DEL_TRABAJO
        else:
            repregunta = config.TEXTO_REPREGUNTA_FIJA
    else:
        reaccion = args["reaccion"]
        if not _texto_valido(reaccion, config.MAX_PALABRAS_REACCION):
            reaccion = config.TEXTO_REACCION_FIJA
        if fuera_del_trabajo:
            repregunta = config.TEXTO_REPREGUNTA_FUERA_DEL_TRABAJO if args["menciona_actividad"] else None
        elif args["suficiente"]:
            repregunta = None
        elif _texto_valido(args["repregunta"], config.MAX_PALABRAS_REPREGUNTA):
            repregunta = args["repregunta"]
        else:
            repregunta = config.TEXTO_REPREGUNTA_FIJA if n >= 2 else None
    return {"reaccion": reaccion, "repregunta": None if ya_repregunto else repregunta}


# --- extraer_perfil


def _mensajes_extraer(respuestas: Datos, competencias: Datos, hasta: int) -> Datos:
    lista = "\n".join(
        f"- {c['codigo']}: {c['texto_simple']}. Ejemplos: {'; '.join(c['criterios_clave'])}"
        if c["criterios_clave"]
        else f"- {c['codigo']}: {c['texto_simple']}."
        for c in competencias
    )
    relato = []
    for r in respuestas:
        if r["n"] > hasta:
            continue
        fuera = " (fuera del trabajo)" if r["n"] in (4, 5) else ""
        relato.append(f"Respuesta {r['n']}{fuera}: {r['texto']}")
        if r.get("repregunta"):
            relato.append(f"Respuesta {r['n']}{fuera}, al repreguntar: {r['repregunta']}")
    return [
        {"role": "system", "content": f"{PROMPT_EXTRAER}\n\nLista de competencias:\n{lista}"},
        {"role": "user", "content": "\n".join(relato)},
    ]


def extraer_perfil(respuestas: Datos, competencias: Datos) -> dict[str, Datos]:
    """Sellos (por otorgar_sellos, con las respuestas 1 a 3) y fortalezas con evidencia textual."""
    mensajes = _mensajes_extraer(respuestas, competencias, 5)
    args = _llamar("extraer_perfil", mensajes, TOOL_EXTRAER, _perfil_valido)
    if args is None:
        raise ErrorExtraccion(config.TEXTO_ERROR_EXTRACCION)
    sellos = calculo.otorgar_sellos(args["competencias"], _textos(respuestas, 3), competencias, set())
    de_sellos = {calculo.normalizar(s["evidencia"]) for s in sellos}
    todas = _textos(respuestas, 5)
    fortalezas = []
    for f in args["fortalezas"]:
        if not calculo.evidencia_valida(f["evidencia"], todas):
            logger.info("fortaleza descartada: evidencia no textual")
        elif calculo.normalizar(f["evidencia"]) in de_sellos:
            logger.info("fortaleza descartada: misma frase que un sello")
        else:
            fortalezas.append({"texto": f["texto"], "evidencia": f["evidencia"]})
    return {"sellos": sellos, "fortalezas": fortalezas}


def extraer_parcial(respuestas: Datos, competencias: Datos) -> dict[str, Any] | None:
    """Sellos ganados con las respuestas 1 a 3, solo para el contador del chat; None si falla."""
    mensajes = _mensajes_extraer(respuestas, competencias, 3)
    args = _llamar("extraer_parcial", mensajes, TOOL_EXTRAER, _perfil_valido)
    if args is None:
        return None
    sellos = calculo.otorgar_sellos(args["competencias"], _textos(respuestas, 3), competencias, set())
    etiquetas = [g["etiqueta"] for g in calculo.agrupar_sellos(sellos)]
    return {"sellos_ganados": len(etiquetas), "etiquetas": etiquetas}


# --- redactar_resumen


def redactar_resumen(sellos: Datos, respuesta_1: str, competencias: Datos) -> str:
    """2 frases de perfil para el CV, o la plantilla fija si el modelo falla."""
    simples = {c["codigo"]: c["texto_simple"] for c in competencias}
    tareas = "\n".join(f"- {s['etiqueta']}: {simples[s['codigos'][0]]}" for s in sellos)
    mensajes = [
        {"role": "system", "content": PROMPT_RESUMEN},
        {"role": "user", "content": f"Tareas:\n{tareas}\nRespuesta 1: {respuesta_1}"},
    ]
    args = _llamar("redactar_resumen", mensajes, TOOL_RESUMEN, _resumen_valido)
    if args is not None:
        return args["resumen"]
    textos = [simples[s["codigos"][0]] for s in sellos[: config.MAX_SELLOS_RESUMEN]]
    return config.TEXTO_RESUMEN_PLANTILLA.format(tareas="; ".join(t[0].lower() + t[1:] for t in textos))
