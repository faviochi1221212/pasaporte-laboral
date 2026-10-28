"""Pruebas de M6 sin navegador: FastAPI sirve web/dist y los textos de pantalla cumplen la regla 5."""
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import calculo, config
from app.main import app

RAIZ = Path(__file__).resolve().parent.parent
TEXTOS = RAIZ / "web" / "src" / "textos.ts"
FRASE_CV = "competencias declaradas"


@pytest.fixture
def dist(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<!doctype html><title>Pasaporte</title>", encoding="utf-8")
    (tmp_path / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    (tmp_path.parent / "secreto.txt").write_text("no", encoding="utf-8")
    monkeypatch.setattr(config, "WEB_DIST", tmp_path)
    return tmp_path


def test_m6_fastapi_sirve_el_build_en_la_raiz(dist: Path) -> None:
    cliente = TestClient(app)
    assert "<title>Pasaporte</title>" in cliente.get("/").text
    assert cliente.get("/assets/app.js").text == "console.log(1)"


def test_m6_las_rutas_de_react_devuelven_index(dist: Path) -> None:
    respuesta = TestClient(app).get("/sesion/pasaporte")
    assert respuesta.status_code == 200
    assert "<title>Pasaporte</title>" in respuesta.text


def test_m6_la_api_no_queda_tapada_por_el_build(dist: Path) -> None:
    cliente = TestClient(app)
    assert cliente.get("/api/salud").json()["ok"] is True
    assert cliente.get("/api/no-existe").json()["error"]["codigo"] == "no_encontrado"


def test_m6_no_se_sale_de_la_carpeta_del_build(dist: Path) -> None:
    respuesta = TestClient(app).get("/..%2Fsecreto.txt")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "no_encontrado"


def test_m6_sin_build_la_raiz_da_404_con_formato_unico(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(config, "WEB_DIST", tmp_path / "no-existe")
    assert TestClient(app).get("/").json()["error"]["codigo"] == "no_encontrado"


def _literales(codigo: str) -> list[str]:
    """Textos entre comillas dobles o invertidas (plantillas como `Pregunta ${n} de 6`)."""
    return [a or b for a, b in re.findall(r'"((?:[^"\\]|\\.)*)"|`((?:[^`\\]|\\.)*)`', codigo)]


def test_regla5_textos_de_pantalla_sin_palabras_prohibidas() -> None:
    codigo = re.sub(r"(?m)^\s*//.*$", "", TEXTOS.read_text(encoding="utf-8"))
    inicio_cv = codigo.index("export const TEXTOS_CV")
    for texto in _literales(codigo[:inicio_cv]):
        assert not calculo.tiene_palabra_prohibida(texto), texto
    for texto in _literales(codigo[inicio_cv:]):
        sin_frase = re.sub(FRASE_CV, "", texto, flags=re.IGNORECASE)
        assert not calculo.tiene_palabra_prohibida(sin_frase), texto
