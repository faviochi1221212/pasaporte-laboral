"""A1 a A4 y A12 contra QVAC real (solo con: pytest -m qvac). Con QVAC_GRABAR=1 graba los fixtures."""
import pytest

import casos_ia
from app import config

pytestmark = pytest.mark.qvac


@pytest.fixture(autouse=True)
def modo_real(monkeypatch: pytest.MonkeyPatch) -> None:
    if not config.QVAC_TOKEN:
        pytest.skip("Falta QVAC_TOKEN en .env")
    monkeypatch.setattr(config, "QVAC_MODO", "real")


@pytest.mark.parametrize("nombre", casos_ia.RELATOS_A1_A3)
def test_a1_a3_sellos_del_origen_con_evidencia_textual(nombre: str) -> None:
    casos_ia.comprobar_a1_a3(nombre)


def test_a4_respuesta_vaga_una_sola_repregunta() -> None:
    casos_ia.comprobar_a4()


@pytest.mark.parametrize("nombre", casos_ia.RELATOS_A1_A3)
def test_a12_reacciones_reales_cumplen_el_limite(nombre: str) -> None:
    casos_ia.comprobar_a12(nombre)
