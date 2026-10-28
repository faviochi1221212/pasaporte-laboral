"""Pruebas de M0: salud de la API y lectura de .env (spec 2)."""
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import config
from app.main import app

cliente = TestClient(app)


def test_m0_salud_responde_ok_y_modo_respaldo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "QVAC_MODO", "respaldo")
    respuesta = cliente.get("/api/salud")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True, "modo": "respaldo"}


def test_m0_salud_responde_modo_real(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "QVAC_MODO", "real")
    assert cliente.get("/api/salud").json() == {"ok": True, "modo": "real"}


@pytest.mark.parametrize("valor", ["", "otro", "REAL", None])
def test_m0_modo_invalido_usa_respaldo(valor: str | None) -> None:
    assert config.normalizar_modo(valor) == "respaldo"


def test_m0_lector_env_ignora_comentarios_y_no_sobrescribe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ruta = tmp_path / ".env"
    ruta.write_text(
        "# comentario\n\nPRUEBA_NUEVA=uno\nPRUEBA_EXISTENTE=archivo\n# PRUEBA_COMENTADA=x\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("PRUEBA_NUEVA", raising=False)
    monkeypatch.delenv("PRUEBA_COMENTADA", raising=False)
    monkeypatch.setenv("PRUEBA_EXISTENTE", "entorno")

    config.cargar_env(ruta)

    assert os.environ["PRUEBA_NUEVA"] == "uno"
    assert os.environ["PRUEBA_EXISTENTE"] == "entorno"
    assert "PRUEBA_COMENTADA" not in os.environ
    monkeypatch.delenv("PRUEBA_NUEVA")
