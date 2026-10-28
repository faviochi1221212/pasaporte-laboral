"""Recorrido completo de María por la API (A8).

Lo usan test_api_qvac.py (QVAC real, graba fixtures) y test_api.py (modo respaldo, lee esos fixtures).
El recorrido es siempre el mismo para que los mensajes, y por eso las claves de los fixtures, coincidan.
"""
from typing import Any

from fastapi.testclient import TestClient

import casos_ia
from app import config

# Si el modelo repregunta donde el relato no trae respuesta, se contesta con esta frase inventada.
RESPUESTA_A_REPREGUNTA_SIN_RELATO = "Preparo el almuerzo del domingo."
SELLO_A_QUITAR = "H2452001-1.E2"


def recorrer_maria(cliente: TestClient) -> dict[str, Any]:
    """Recorre los 9 endpoints como lo haría la pantalla y devuelve lo que respondió cada uno."""
    relato = casos_ia.cargar_relato("maria_cajera")
    resultado: dict[str, Any] = {"turnos": [], "parciales": []}

    r = cliente.post("/api/sesiones", json={"ocupacion_origen": relato["ocupacion_origen"]})
    assert r.status_code == 200, r.text
    sesion = r.json()["sesion_id"]
    base = f"/api/sesiones/{sesion}"

    for respuesta in relato["respuestas"]:
        n = respuesta["n"]
        turno = cliente.post(f"{base}/respuestas", json={"n": n, "texto": respuesta["texto"]}).json()
        resultado["turnos"].append(turno)
        if turno["tipo"] == "repregunta":
            texto = respuesta.get("repregunta") or RESPUESTA_A_REPREGUNTA_SIN_RELATO
            turno = cliente.post(f"{base}/respuestas", json={"n": n, "texto": texto}).json()
            resultado["turnos"].append(turno)
        assert turno["tipo"] in ("siguiente", "fin"), turno
        if turno["parcial_listo"]:
            resultado["parciales"].append(cliente.post(f"{base}/sellos-parciales"))

    r = cliente.post(f"{base}/pasaporte")
    assert r.status_code == 200, r.text
    resultado["pasaporte"] = r.json()

    r = cliente.put(f"{base}/pasaporte", json={"quitar": [SELLO_A_QUITAR], "quitar_fortalezas": []})
    assert r.status_code == 200, r.text
    resultado["pasaporte_editado"] = r.json()

    esperado = relato["esperado"]
    r = cliente.put(f"{base}/preferencias", json={"interes": esperado["interes"], "horas": esperado["horas"]})
    assert r.json() == {"ok": True}

    r = cliente.get(f"{base}/ruta")
    assert r.status_code == 200, r.text
    resultado["ruta"] = r.json()
    destino = resultado["ruta"]["destinos"][0]["codigo"]

    r = cliente.get(f"{base}/avisos", params={"destino": destino})
    assert r.status_code == 200, r.text
    resultado["avisos"] = r.json()

    r = cliente.get(f"{base}/cv", params={"destino": destino})
    assert r.status_code == 200, r.text
    resultado["cv"] = r.json()
    return resultado


def comprobar_a8(resultado: dict[str, Any]) -> None:
    """A8: el recorrido completo funciona y usa respuestas del modelo, no solo los respaldos fijos."""
    turnos = resultado["turnos"]
    assert turnos[-1]["tipo"] == "fin"
    assert turnos[-1]["cierre"] == config.TEXTO_CIERRE
    assert any(t["reaccion"] not in (None, config.TEXTO_REACCION_FIJA) for t in turnos)
    assert [p.status_code for p in resultado["parciales"]] == [200, 200]

    codigos = {s["codigo"] for s in resultado["pasaporte"]["sellos"]}
    assert len({c for c in codigos if c.startswith("G2347002")}) >= 2
    assert SELLO_A_QUITAR not in {s["codigo"] for s in resultado["pasaporte_editado"]["sellos"]}

    destinos = resultado["ruta"]["destinos"]
    assert destinos and all(d["codigo"] != "G2347002" for d in destinos)
    assert resultado["avisos"]["avisos"] or resultado["avisos"]["mensaje"]
    cv = resultado["cv"]
    assert cv["puesto"] == "Cajero/a"
    assert cv["resumen"] and cv["sellos"]
