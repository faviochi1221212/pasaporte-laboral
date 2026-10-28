"""A8 contra QVAC real (solo con: pytest -m qvac). Con QVAC_GRABAR=1 graba los fixtures del recorrido de María."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import casos_api
from app import config
from app.main import app

pytestmark = pytest.mark.qvac


@pytest.fixture(autouse=True)
def entorno(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    if not config.QVAC_TOKEN:
        pytest.skip("Falta QVAC_TOKEN en .env")
    monkeypatch.setattr(config, "QVAC_MODO", "real")
    monkeypatch.setattr(config, "DB_RUTA", tmp_path / "prueba.db")


def test_a8_recorrido_de_maria_con_qvac_real() -> None:
    casos_api.comprobar_a8(casos_api.recorrer_maria(TestClient(app)))
