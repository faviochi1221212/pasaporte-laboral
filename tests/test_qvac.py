"""Pruebas de M3: cliente de QVAC con servidor falso (sin red) y modo respaldo (spec 5 y 7)."""
import json
import logging
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
import pytest

from app import config, qvac

# Valores de .env, guardados antes de que el fixture los reemplace por falsos.
CONFIG_REAL = {n: getattr(config, n) for n in ("QVAC_TOKEN", "QVAC_BASE_URL", "QVAC_MODEL")}
TOKEN = "token-secreto-de-prueba"
TEXTO_PERSONA = "Cuadro la caja al final del día"
MENSAJES = [
    {"role": "system", "content": "Llama a guardar."},
    {"role": "user", "content": TEXTO_PERSONA},
]
TOOL = {
    "type": "function",
    "function": {
        "name": "guardar",
        "description": "Guarda una tarea.",
        "parameters": {
            "type": "object",
            "properties": {"tarea": {"type": "string"}},
            "required": ["tarea"],
        },
    },
}


def respuesta_con_tool(argumentos: Any, nombre: str = "guardar") -> dict[str, Any]:
    return {
        "choices": [
            {
                "message": {
                    "content": "",
                    "tool_calls": [{"function": {"name": nombre, "arguments": argumentos}}],
                },
                "finish_reason": "tool_calls",
            }
        ]
    }


RESPUESTA_OK = respuesta_con_tool(json.dumps({"tarea": "cuadrar caja"}))


@pytest.fixture(autouse=True)
def entorno(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(config, "QVAC_MODO", "real")
    monkeypatch.setattr(config, "QVAC_GRABAR", False)
    monkeypatch.setattr(config, "QVAC_TOKEN", TOKEN)
    monkeypatch.setattr(config, "QVAC_BASE_URL", "https://qvac.falso/")
    monkeypatch.setattr(config, "QVAC_MODEL", "modelo-falso")
    monkeypatch.setattr(config, "QVAC_PAUSA", 0)
    monkeypatch.setattr(qvac, "FIXTURES", tmp_path / "fixtures")


def cliente_falso(
    respuestas: list[Callable[[httpx.Request], httpx.Response]],
    pedidos: list[httpx.Request],
) -> httpx.Client:
    """Cliente cuyo servidor responde, en orden, con cada función de la lista."""

    def manejar(pedido: httpx.Request) -> httpx.Response:
        pedidos.append(pedido)
        return respuestas[len(pedidos) - 1](pedido)

    return httpx.Client(transport=httpx.MockTransport(manejar))


def ok(_: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=RESPUESTA_OK)


def caida(pedido: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("sin conexión", request=pedido)


def lenta(pedido: httpx.Request) -> httpx.Response:
    raise httpx.ReadTimeout("tiempo agotado", request=pedido)


def error_500(_: httpx.Request) -> httpx.Response:
    return httpx.Response(502, text="Bad Gateway")


def error_401(_: httpx.Request) -> httpx.Response:
    return httpx.Response(401, text="Unauthorized")


# --- pedido y respuesta


def test_m3_envia_parametros_fijos_y_cabeceras() -> None:
    pedidos: list[httpx.Request] = []
    qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([ok], pedidos))
    pedido = pedidos[0]
    assert str(pedido.url) == "https://qvac.falso/v1/chat/completions"
    assert pedido.headers["Authorization"] == f"Bearer {TOKEN}"
    assert pedido.headers["ngrok-skip-browser-warning"] == "true"
    assert json.loads(pedido.content) == {
        "model": "modelo-falso",
        "messages": MENSAJES,
        "tools": [TOOL],
        "tool_choice": "auto",
        "temperature": 0,
        "max_tokens": 2000,
        "chat_template_kwargs": {"enable_thinking": False},
    }


def test_m3_devuelve_los_argumentos_como_dict() -> None:
    argumentos = qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([ok], []))
    assert argumentos == {"tarea": "cuadrar caja"}


def test_m3_acepta_argumentos_que_ya_vienen_como_dict() -> None:
    def con_dict(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=respuesta_con_tool({"tarea": "x"}))

    assert qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([con_dict], [])) == {"tarea": "x"}


@pytest.mark.parametrize(
    "respuesta",
    [
        {"choices": [{"message": {"content": "Hola, no llamo a nada."}}]},
        respuesta_con_tool(json.dumps({"tarea": "x"}), nombre="otra_tool"),
        respuesta_con_tool("{no es json"),
        {"choices": []},
    ],
)
def test_m3_error_propio_si_el_modelo_no_llamo_la_tool(respuesta: dict[str, Any]) -> None:
    def sin_tool(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=respuesta)

    with pytest.raises(qvac.ErrorSinTool):
        qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([sin_tool], []))


# --- reintentos


@pytest.mark.parametrize("falla", [caida, lenta, error_500])
def test_hu15_reintenta_ante_conexion_tiempo_agotado_o_5xx(
    falla: Callable[[httpx.Request], httpx.Response],
) -> None:
    pedidos: list[httpx.Request] = []
    argumentos = qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([falla, falla, ok], pedidos))
    assert argumentos == {"tarea": "cuadrar caja"}
    assert len(pedidos) == 3


def test_hu15_error_claro_despues_de_3_intentos() -> None:
    pedidos: list[httpx.Request] = []
    with pytest.raises(qvac.ErrorQvac, match="3 intentos"):
        qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([caida] * 4, pedidos))
    assert len(pedidos) == 3


def test_m3_no_reintenta_ante_error_4xx() -> None:
    pedidos: list[httpx.Request] = []
    with pytest.raises(qvac.ErrorQvac, match="401"):
        qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([error_401, ok], pedidos))
    assert len(pedidos) == 1


# --- log


def test_m3_log_con_tiempo_y_sin_token_ni_texto_de_la_persona(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.DEBUG):
        qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([caida, error_500, ok], []))
    assert "prueba" in caplog.text
    assert " ms" in caplog.text
    assert TOKEN not in caplog.text
    assert TEXTO_PERSONA not in caplog.text


# --- modo respaldo y grabación


def test_hu15_respaldo_responde_desde_el_fixture_sin_red(monkeypatch: pytest.MonkeyPatch) -> None:
    ruta = qvac.FIXTURES / "prueba" / f"{qvac.clave(MENSAJES)}.json"
    ruta.parent.mkdir(parents=True)
    ruta.write_text(json.dumps(RESPUESTA_OK), encoding="utf-8")
    monkeypatch.setattr(config, "QVAC_MODO", "respaldo")
    pedidos: list[httpx.Request] = []
    argumentos = qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([ok], pedidos))
    assert argumentos == {"tarea": "cuadrar caja"}
    assert pedidos == []


def test_hu15_respaldo_sin_fixture_da_error_claro(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "QVAC_MODO", "respaldo")
    with pytest.raises(qvac.ErrorSinFixture, match=qvac.clave(MENSAJES)):
        qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([ok], []))


def test_m3_clave_cambia_con_los_mensajes_y_es_corta() -> None:
    otra = [*MENSAJES[:1], {"role": "user", "content": "Otra cosa"}]
    assert qvac.clave(MENSAJES) == qvac.clave(json.loads(json.dumps(MENSAJES)))
    assert qvac.clave(MENSAJES) != qvac.clave(otra)
    assert len(qvac.clave(MENSAJES)) == 12


def test_m3_grabar_guarda_la_respuesta_real_en_el_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "QVAC_GRABAR", True)
    qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([ok], []))
    ruta = qvac.FIXTURES / "prueba" / f"{qvac.clave(MENSAJES)}.json"
    assert json.loads(ruta.read_text(encoding="utf-8")) == RESPUESTA_OK


def test_m3_sin_grabar_no_escribe_fixtures() -> None:
    qvac.llamar_tool("prueba", MENSAJES, TOOL, cliente_falso([ok], []))
    assert not qvac.FIXTURES.exists()


# --- QVAC real (solo con: pytest -m qvac)


@pytest.mark.qvac
def test_a9_llamada_real_devuelve_tool_en_menos_de_8_s(monkeypatch: pytest.MonkeyPatch) -> None:
    for nombre, valor in CONFIG_REAL.items():
        monkeypatch.setattr(config, nombre, valor)
    monkeypatch.setattr(config, "QVAC_MODO", "real")
    if not config.QVAC_TOKEN:
        pytest.skip("Falta QVAC_TOKEN en .env")
    inicio = time.perf_counter()
    argumentos = qvac.llamar_tool("prueba", MENSAJES, TOOL)
    segundos = time.perf_counter() - inicio
    assert isinstance(argumentos.get("tarea"), str)
    assert segundos < 8, f"tardó {segundos:.1f} s"
