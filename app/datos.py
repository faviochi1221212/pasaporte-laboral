"""Carga los JSON de data/ una sola vez, al importar el módulo (spec 3)."""
import json
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parent.parent / "data"


def _cargar(nombre: str) -> Any:
    return json.loads((DATA / nombre).read_text(encoding="utf-8"))


OCUPACIONES: list[dict[str, Any]] = _cargar("ocupaciones.json")
COMPETENCIAS: list[dict[str, Any]] = _cargar("competencias.json")
CURSOS: list[dict[str, Any]] = _cargar("cursos.json")
AVISOS: list[dict[str, Any]] = _cargar("avisos.json")
DEMANDA: dict[str, Any] = _cargar("demanda.json")
