"""Borra todas las sesiones y sus respuestas, sellos y fortalezas (spec 9b: al final de la demo se borra todo).

Uso: python scripts/borrar_sesiones.py   (desde la raíz del repositorio)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import db  # noqa: E402


def main() -> None:
    print(f"{db.borrar_todo()} sesiones borradas")


if __name__ == "__main__":
    main()
