"""Pruebas de M5: los 9 endpoints (spec 6) con un modelo falso, y A8 en modo respaldo con los fixtures."""
import runpy
import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

import casos_api
import casos_ia
from app import config, qvac
from app.main import app

MARIA = casos_ia.cargar_relato("maria_cajera")["respuestas"]

EXTRACCION_MARIA = {
    "competencias": [
        {"codigo": "G2347002-1.E1", "evidencia": "Abro mi caja"},
        {"codigo": "G2347002-1.E2", "evidencia": "Cobro en efectivo, con tarjeta y con Yape"},
        {"codigo": "G2347002-1.E3", "evidencia": "Al final del día cuadro la caja"},
        {"codigo": "I2555001-2.E1", "evidencia": "atiendo su reclamo"},
        {"codigo": "H2452001-1.E2", "evidencia": "ayudo a ordenar la mercadería"},
    ],
    "fortalezas": [
        {"texto": "Organiza partidos de fulbito", "evidencia": "organizo los partidos de fulbito de mi barrio"},
        {"texto": "Enseña a compañeras nuevas", "evidencia": "A las chicas nuevas les enseño a usar la caja"},
    ],
}
RESUMEN = {"resumen": "Cajera con 6 años en supermercado. Abre, cobra y cuadra la caja.", "anios": "6 años"}


def revision(
    suficiente: bool = True, repregunta: str = "", menciona_actividad: bool = False
) -> dict[str, Any]:
    return {
        "reaccion": "¡Qué bien!",
        "suficiente": suficiente,
        "menciona_actividad": menciona_actividad,
        "repregunta": repregunta,
    }


@pytest.fixture
def cliente(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    monkeypatch.setattr(config, "DB_RUTA", tmp_path / "prueba.db")
    return TestClient(app)


@pytest.fixture
def modelo(monkeypatch: pytest.MonkeyPatch) -> Callable[..., dict[str, Any]]:
    """Instala un modelo falso; cada tarea responde con lo que se le pase (o lanza el error dado)."""

    def instalar(**por_tarea: Any) -> dict[str, Any]:
        salidas: dict[str, Any] = {
            "revisar_respuesta": revision(),
            "extraer_perfil": EXTRACCION_MARIA,
            "extraer_parcial": EXTRACCION_MARIA,
            "redactar_resumen": RESUMEN,
            **por_tarea,
        }

        def llamar(tarea: str, mensajes: list[dict[str, Any]], tool: dict[str, Any]) -> dict[str, Any]:
            salida = salidas[tarea]
            if isinstance(salida, Exception):
                raise salida
            return salida

        monkeypatch.setattr(qvac, "llamar_tool", llamar)
        return salidas

    instalar()
    return instalar


def crear(cliente: TestClient, origen: str | None = "G2347002") -> str:
    return cliente.post("/api/sesiones", json={"ocupacion_origen": origen}).json()["sesion_id"]


def responder(cliente: TestClient, sesion: str, n: int, texto: str) -> Any:
    return cliente.post(f"/api/sesiones/{sesion}/respuestas", json={"n": n, "texto": texto})


def conversar(cliente: TestClient, sesion: str) -> None:
    """Responde las 6 preguntas de María (sin repreguntas con el modelo falso por defecto)."""
    for r in MARIA:
        assert responder(cliente, sesion, r["n"], r["texto"]).status_code == 200


def con_pasaporte(cliente: TestClient) -> str:
    sesion = crear(cliente)
    conversar(cliente, sesion)
    assert cliente.post(f"/api/sesiones/{sesion}/pasaporte").status_code == 200
    return sesion


def con_preferencias(cliente: TestClient) -> str:
    sesion = con_pasaporte(cliente)
    cliente.put(f"/api/sesiones/{sesion}/preferencias", json={"interes": "gente", "horas": "3-5"})
    return sesion


def es_error(respuesta: Any, estado: int, codigo: str) -> None:
    assert respuesta.status_code == estado, respuesta.text
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"error"}
    assert cuerpo["error"]["codigo"] == codigo
    assert isinstance(cuerpo["error"]["mensaje"], str) and cuerpo["error"]["mensaje"]


# --- sesiones (HU-01, spec 5b)


@pytest.mark.parametrize("origen", ["G2347002", "H2452001", "M2981001", None])
def test_hu01_crear_sesion_con_saludo_y_pregunta_1(
    cliente: TestClient, modelo: Any, origen: str | None
) -> None:
    r = cliente.post("/api/sesiones", json={"ocupacion_origen": origen})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["sesion_id"]
    assert cuerpo["saludo"] == config.TEXTO_SALUDO
    assert cuerpo["pregunta"] == {
        "n": 1,
        "texto": "¿Cuánto tiempo llevas en esto?",
        "ejemplos": ["Menos de 1 año", "1 a 5 años", "Más de 5"],
    }


@pytest.mark.parametrize("origen", ["I2555001", "X0000000"])
def test_hu01_origen_que_no_es_de_inicio_da_error(cliente: TestClient, origen: str) -> None:
    es_error(cliente.post("/api/sesiones", json={"ocupacion_origen": origen}), 422, "origen_invalido")


def test_m5_sesion_inexistente_da_404_con_formato_unico(cliente: TestClient) -> None:
    es_error(cliente.get("/api/sesiones/no-existe/ruta"), 404, "sesion_no_existe")


def test_m5_datos_invalidos_dan_422_con_formato_unico(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    es_error(responder(cliente, sesion, 1, "   "), 422, "datos_invalidos")
    es_error(cliente.post(f"/api/sesiones/{sesion}/respuestas", json={"n": 9, "texto": "x"}), 422, "datos_invalidos")


# --- respuestas (HU-02, spec 5 y 6)


def test_hu02_seis_preguntas_en_orden_y_cierre(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    turnos = [responder(cliente, sesion, r["n"], r["texto"]).json() for r in MARIA]
    for n, turno in enumerate(turnos[:5], start=1):
        assert turno["tipo"] == "siguiente"
        assert turno["reaccion"] == "¡Qué bien!"
        assert turno["pregunta"]["n"] == n + 1
        assert turno["pregunta"]["texto"] == config.GUION[n + 1]["texto"]
        assert turno["cierre"] is None
    assert turnos[5] == {
        "tipo": "fin",
        "reaccion": None,
        "pregunta": None,
        "cierre": config.TEXTO_CIERRE,
        "parcial_listo": False,
    }


def test_hu16_parcial_listo_solo_al_cerrar_las_preguntas_2_y_3(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    listos = [responder(cliente, sesion, r["n"], r["texto"]).json()["parcial_listo"] for r in MARIA]
    assert listos == [False, True, True, False, False, False]


def test_a4_repregunta_con_el_mismo_n_y_nunca_una_segunda(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    responder(cliente, sesion, 1, MARIA[0]["texto"])
    modelo(revisar_respuesta=revision(suficiente=False, repregunta="¿Qué haces tú en la caja?"))
    turno = responder(cliente, sesion, 2, "de todo un poco").json()
    assert turno["tipo"] == "repregunta"
    assert turno["pregunta"] == {"n": 2, "texto": "¿Qué haces tú en la caja?", "ejemplos": []}
    turno = responder(cliente, sesion, 2, "de todo pues").json()
    assert turno["tipo"] == "siguiente"
    assert turno["pregunta"]["n"] == 3


def test_hu02_pregunta_fuera_de_orden_da_409(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    es_error(responder(cliente, sesion, 2, "Cobro y cuadro la caja todos los días."), 409, "fuera_de_orden")


def test_hu02_despues_del_fin_no_hay_pregunta_7(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    conversar(cliente, sesion)
    es_error(cliente.post(f"/api/sesiones/{sesion}/respuestas", json={"n": 7, "texto": "x"}), 422, "datos_invalidos")


def test_hu02_atras_borra_esa_respuesta_y_las_siguientes(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    for r in MARIA[:3]:
        responder(cliente, sesion, r["n"], r["texto"])
    turno = responder(cliente, sesion, 2, "Abro la caja y cobro.").json()
    assert turno["pregunta"]["n"] == 3
    es_error(responder(cliente, sesion, 4, MARIA[3]["texto"]), 409, "fuera_de_orden")


# --- sellos parciales (HU-16, A13)


def test_hu16_sellos_parciales(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    for r in MARIA[:2]:
        responder(cliente, sesion, r["n"], r["texto"])
    r = cliente.post(f"/api/sesiones/{sesion}/sellos-parciales")
    assert r.status_code == 200
    assert r.json() == {
        "sellos_ganados": 3,
        "etiquetas": ["Abre la caja", "Cobra y da vuelto", "Cuadra la caja"],
    }


def test_a13_si_parciales_falla_el_recorrido_sigue_y_el_pasaporte_sale_igual(
    cliente: TestClient, modelo: Any
) -> None:
    normal = con_pasaporte(cliente)
    esperado = cliente.put(f"/api/sesiones/{normal}/pasaporte", json={"quitar": [], "quitar_fortalezas": []})

    modelo(extraer_parcial=qvac.ErrorQvac("x"))
    sesion = crear(cliente)
    for r in MARIA:
        turno = responder(cliente, sesion, r["n"], r["texto"]).json()
        if turno["parcial_listo"]:
            es_error(cliente.post(f"/api/sesiones/{sesion}/sellos-parciales"), 503, "parcial_no_disponible")
    r = cliente.post(f"/api/sesiones/{sesion}/pasaporte")
    assert r.status_code == 200
    assert r.json() == esperado.json()


# --- pasaporte (HU-04)


def test_hu04_pasaporte_antes_del_fin_da_409(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    responder(cliente, sesion, 1, MARIA[0]["texto"])
    es_error(cliente.post(f"/api/sesiones/{sesion}/pasaporte"), 409, "conversacion_incompleta")


def test_hu04_pasaporte_con_sellos_y_fortalezas(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    conversar(cliente, sesion)
    cuerpo = cliente.post(f"/api/sesiones/{sesion}/pasaporte").json()
    assert [s["codigo"] for s in cuerpo["sellos"]] == [
        "G2347002-1.E1",
        "G2347002-1.E2",
        "G2347002-1.E3",
        "H2452001-1.E2",
        "I2555001-2.E1",
        "I2555001-2.E4",
    ]
    assert cuerpo["sellos"][0] == {
        "codigo": "G2347002-1.E1",
        "etiqueta": "Abre la caja",
        "icono": "caja",
        "evidencia": "Abro mi caja",
    }
    assert [f["texto"] for f in cuerpo["fortalezas"]] == [
        "Organiza partidos de fulbito",
        "Enseña a compañeras nuevas",
    ]


def test_hu04_quitar_sello_quita_su_etiqueta_y_se_puede_deshacer(cliente: TestClient, modelo: Any) -> None:
    sesion = con_pasaporte(cliente)
    url = f"/api/sesiones/{sesion}/pasaporte"
    cuerpo = cliente.put(url, json={"quitar": ["G2347002-1.E3"], "quitar_fortalezas": [0]}).json()
    codigos = [s["codigo"] for s in cuerpo["sellos"]]
    assert "G2347002-1.E3" not in codigos and "I2555001-2.E4" not in codigos
    assert [f["texto"] for f in cuerpo["fortalezas"]] == ["Enseña a compañeras nuevas"]
    cuerpo = cliente.put(url, json={"quitar": [], "quitar_fortalezas": []}).json()
    assert len(cuerpo["sellos"]) == 6 and len(cuerpo["fortalezas"]) == 2


def test_hu04_relato_no_leido_da_el_mensaje_fijo(cliente: TestClient, modelo: Any) -> None:
    modelo(extraer_perfil=qvac.ErrorSinTool("x"))
    sesion = crear(cliente)
    conversar(cliente, sesion)
    r = cliente.post(f"/api/sesiones/{sesion}/pasaporte")
    es_error(r, 502, "relato_no_leido")
    assert r.json()["error"]["mensaje"] == config.TEXTO_ERROR_EXTRACCION


def test_a2_a_otorgar_sellos_solo_llegan_las_respuestas_1_a_3(cliente: TestClient, modelo: Any) -> None:
    # "reservo la cancha" solo está en la respuesta a la repregunta de la pregunta 4.
    modelo(
        revisar_respuesta=revision(menciona_actividad=True),
        extraer_perfil={
            "competencias": [{"codigo": "I2556002-2.E1", "evidencia": "reservo la cancha"}],
            "fortalezas": [{"texto": "Organiza partidos", "evidencia": "reservo la cancha"}],
        },
    )
    sesion = crear(cliente)
    for r in MARIA:
        if responder(cliente, sesion, r["n"], r["texto"]).json()["tipo"] == "repregunta":
            responder(cliente, sesion, r["n"], r.get("repregunta") or "Cocino arroz con pollo.")
    cuerpo = cliente.post(f"/api/sesiones/{sesion}/pasaporte").json()
    assert cuerpo["sellos"] == []
    assert [f["texto"] for f in cuerpo["fortalezas"]] == ["Organiza partidos"]


# --- preferencias, ruta y avisos (HU-05, 06, 07, 09, 13)


def test_hu05_preferencias_invalidas_dan_422(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    url = f"/api/sesiones/{sesion}/preferencias"
    es_error(cliente.put(url, json={"interes": "plata", "horas": "3-5"}), 422, "datos_invalidos")
    assert cliente.put(url, json={"interes": "papeles", "horas": "5+"}).json() == {"ok": True}


def test_hu06_ruta_sin_pasaporte_o_sin_preferencias_da_409(cliente: TestClient, modelo: Any) -> None:
    es_error(cliente.get(f"/api/sesiones/{crear(cliente)}/ruta"), 409, "falta_pasaporte")
    es_error(cliente.get(f"/api/sesiones/{con_pasaporte(cliente)}/ruta"), 409, "faltan_preferencias")


def test_hu06_hu13_ruta_con_sustento_y_sin_el_origen(cliente: TestClient, modelo: Any) -> None:
    sesion = con_preferencias(cliente)
    cuerpo = cliente.get(f"/api/sesiones/{sesion}/ruta").json()
    assert cuerpo["foto"] == "2026-10-27T19:58-05:00"
    destinos = cuerpo["destinos"]
    assert 1 <= len(destinos) <= 3
    assert "G2347002" not in [d["codigo"] for d in destinos]
    puntajes = [d["puntaje"] for d in destinos]
    assert puntajes == sorted(puntajes, reverse=True)
    for d in destinos:
        assert d["puntaje"] == pytest.approx(0.60 * d["cobertura"] + 0.25 * d["interes"] + 0.15 * d["demanda"])
        assert len(d["que_harias"]) == 3 and d["tienes"]
        for f in d["faltan"]:
            assert (f["curso"] is None) == (f["mensaje"] == config.TEXTO_SIN_CURSO)
        assert d["avisos_parecidos"] == (d["codigo"] == "I2555001")


def test_hu09_avisos_con_y_sin_avisos(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente)
    url = f"/api/sesiones/{sesion}/avisos"
    con = cliente.get(url, params={"destino": "I2555001"}).json()
    assert 1 <= len(con["avisos"]) <= 3 and con["mensaje"] is None
    assert all(a["que_piden"] and a["nota"].startswith("Aviso parecido") for a in con["avisos"])
    assert cliente.get(url, params={"destino": "I2555002"}).json() == {
        "avisos": [],
        "mensaje": config.TEXTO_SIN_AVISOS,
    }
    es_error(cliente.get(url, params={"destino": "X"}), 422, "destino_invalido")


# --- CV (HU-10)


def test_hu10_cv_en_json(cliente: TestClient, modelo: Any) -> None:
    sesion = con_preferencias(cliente)
    cliente.put(f"/api/sesiones/{sesion}/pasaporte", json={"quitar": [], "quitar_fortalezas": [1]})
    cv = cliente.get(f"/api/sesiones/{sesion}/cv", params={"destino": "H2452001"}).json()
    assert cv["resumen"] == RESUMEN["resumen"]
    assert cv["puesto"] == "Cajero/a"
    assert cv["anios"] == "6 años"
    assert cv["sellos"][2] == {
        "etiqueta": "Cuadra la caja",
        "texto_simple": "Cuadrar la caja al final del día",
        "codigos": ["G2347002-1.E3", "I2555001-2.E4"],
    }
    assert [f["texto"] for f in cv["fortalezas"]] == ["Organiza partidos de fulbito"]
    assert cv["destino"] == "Operaciones de Almacén"
    # Faltan H2452001-1.E1 (sin curso) y E3 (Logística 360°): va el primero que tiene curso.
    assert cv["curso"]["id"] == "logistica-360"
    assert cv["curso"]["semanas"] == 5


def test_hu10_cv_sin_origen_no_tiene_puesto(cliente: TestClient, modelo: Any) -> None:
    sesion = crear(cliente, origen=None)
    conversar(cliente, sesion)
    cliente.post(f"/api/sesiones/{sesion}/pasaporte")
    cliente.put(f"/api/sesiones/{sesion}/preferencias", json={"interes": "gente", "horas": "1-2"})
    assert cliente.get(f"/api/sesiones/{sesion}/cv", params={"destino": "I2555001"}).json()["puesto"] is None


# --- datos (spec 9b)


def test_9b_la_base_no_guarda_datos_personales(cliente: TestClient, modelo: Any) -> None:
    con_pasaporte(cliente)
    with sqlite3.connect(config.DB_RUTA) as con:
        columnas = {
            fila[1]
            for tabla in ("sesion", "respuesta", "sello", "fortaleza")
            for fila in con.execute(f"PRAGMA table_info({tabla})")
        }
    prohibidas = {"nombre", "dni", "telefono", "correo", "distrito", "edad", "genero"}
    assert not columnas & prohibidas


# --- A8: recorrido completo de María en modo respaldo, con los fixtures grabados


def test_a8_recorrido_de_maria_en_respaldo(cliente: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "QVAC_MODO", "respaldo")
    casos_api.comprobar_a8(casos_api.recorrer_maria(cliente))


# --- borrar sesiones después de la demo (spec 9b)


def test_9b_borrar_sesiones_deja_la_base_vacia(
    cliente: TestClient, modelo: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    con_pasaporte(cliente)
    crear(cliente)
    runpy.run_path(str(Path(__file__).parent.parent / "scripts" / "borrar_sesiones.py"), run_name="__main__")
    assert "2 sesiones borradas" in capsys.readouterr().out
    with sqlite3.connect(config.DB_RUTA) as con:
        for tabla in ("sesion", "respuesta", "sello", "fortaleza"):
            assert con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0] == 0
