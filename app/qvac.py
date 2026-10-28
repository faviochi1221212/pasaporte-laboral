"""Cliente de QVAC con modo respaldo (spec 5 y 7).

Nunca registra el token ni el texto de los mensajes: solo tarea, intento, modo y tiempo.
"""
import hashlib
import json
import logging
import time
from typing import Any

import httpx

from app import config

logger = logging.getLogger(__name__)

FIXTURES = config.RAIZ / "fixtures"


class ErrorQvac(Exception):
    """QVAC no devolvió una respuesta que se pueda usar."""


class ErrorSinTool(ErrorQvac):
    """El modelo respondió sin llamar la tool pedida."""


class ErrorSinFixture(ErrorQvac):
    """En modo respaldo no hay respuesta grabada para estos mensajes."""


def clave(mensajes: list[dict[str, Any]]) -> str:
    """Hash corto del contenido de los mensajes; nombra el archivo del fixture."""
    texto = json.dumps(mensajes, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:12]


def llamar_tool(
    tarea: str,
    mensajes: list[dict[str, Any]],
    tool: dict[str, Any],
    cliente: httpx.Client | None = None,
) -> dict[str, Any]:
    """Pide al modelo que llame la tool y devuelve sus argumentos como dict."""
    ruta = FIXTURES / tarea / f"{clave(mensajes)}.json"
    if config.QVAC_MODO == "respaldo":
        if not ruta.exists():
            raise ErrorSinFixture(f"No hay respuesta grabada para la tarea {tarea}: falta {ruta.name}")
        logger.info("qvac %s: respaldo desde %s", tarea, ruta.name)
        respuesta = json.loads(ruta.read_text(encoding="utf-8"))
    else:
        respuesta = _pedir(tarea, mensajes, tool, cliente)
        if config.QVAC_GRABAR:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_text(json.dumps(respuesta, ensure_ascii=False, indent=2), encoding="utf-8")
    return _argumentos(respuesta, tool["function"]["name"])


def _pedir(
    tarea: str,
    mensajes: list[dict[str, Any]],
    tool: dict[str, Any],
    cliente: httpx.Client | None,
) -> dict[str, Any]:
    """POST a QVAC con hasta 3 intentos ante error de conexión, tiempo agotado o HTTP 5xx."""
    url = f"{config.QVAC_BASE_URL.rstrip('/')}/v1/chat/completions"
    cabeceras = {
        "Authorization": f"Bearer {config.QVAC_TOKEN}",
        "ngrok-skip-browser-warning": "true",
    }
    cuerpo = {
        "model": config.QVAC_MODEL,
        "messages": mensajes,
        "tools": [tool],
        "tool_choice": "auto",
        "temperature": 0,
        "max_tokens": config.QVAC_MAX_TOKENS,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    propio = cliente is None
    cliente = cliente or httpx.Client()
    try:
        for intento in range(1, config.QVAC_INTENTOS + 1):
            if intento > 1:
                time.sleep(config.QVAC_PAUSA)
            inicio = time.perf_counter()
            try:
                r = cliente.post(url, json=cuerpo, headers=cabeceras, timeout=config.QVAC_TIMEOUT)
            except httpx.TransportError as e:
                motivo = type(e).__name__
            else:
                if r.status_code < 400:
                    ms = (time.perf_counter() - inicio) * 1000
                    logger.info("qvac %s: intento %d, real, %.0f ms", tarea, intento, ms)
                    return r.json()
                if r.status_code < 500:
                    raise ErrorQvac(f"QVAC respondió HTTP {r.status_code} en la tarea {tarea}")
                motivo = f"HTTP {r.status_code}"
            ms = (time.perf_counter() - inicio) * 1000
            logger.warning("qvac %s: intento %d falló (%s), %.0f ms", tarea, intento, motivo, ms)
    finally:
        if propio:
            cliente.close()
    raise ErrorQvac(f"QVAC no respondió en la tarea {tarea} después de {config.QVAC_INTENTOS} intentos")


def _argumentos(respuesta: dict[str, Any], nombre: str) -> dict[str, Any]:
    """Saca los argumentos de la tool pedida; si no está o no es JSON, lanza ErrorSinTool."""
    opciones = respuesta.get("choices") or [{}]
    llamadas = opciones[0].get("message", {}).get("tool_calls") or []
    for llamada in llamadas:
        funcion = llamada.get("function", {})
        if funcion.get("name") != nombre:
            continue
        argumentos = funcion.get("arguments")
        if isinstance(argumentos, str):
            try:
                argumentos = json.loads(argumentos)
            except json.JSONDecodeError as e:
                raise ErrorSinTool(f"Los argumentos de {nombre} no son JSON válido") from e
        if isinstance(argumentos, dict):
            return argumentos
    raise ErrorSinTool(f"El modelo no llamó la tool {nombre}")
