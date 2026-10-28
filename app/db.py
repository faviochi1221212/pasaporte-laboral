"""SQLite con el módulo sqlite3 (spec 2 y 9b): 4 tablas, id anónimo y sin datos personales."""
import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import closing, contextmanager
from typing import Any

from app import config

ESQUEMA = """
CREATE TABLE IF NOT EXISTS sesion (
    id TEXT PRIMARY KEY,
    origen TEXT,
    interes TEXT,
    horas TEXT,
    pasaporte INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS respuesta (
    sesion_id TEXT NOT NULL REFERENCES sesion(id),
    n INTEGER NOT NULL,
    texto TEXT NOT NULL,
    repregunta TEXT,
    respuesta_repregunta TEXT,
    PRIMARY KEY (sesion_id, n)
);
CREATE TABLE IF NOT EXISTS sello (
    sesion_id TEXT NOT NULL REFERENCES sesion(id),
    orden INTEGER NOT NULL,
    codigo TEXT NOT NULL,
    etiqueta TEXT NOT NULL,
    icono TEXT NOT NULL,
    evidencia TEXT NOT NULL,
    quitado INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (sesion_id, codigo)
);
CREATE TABLE IF NOT EXISTS fortaleza (
    sesion_id TEXT NOT NULL REFERENCES sesion(id),
    i INTEGER NOT NULL,
    texto TEXT NOT NULL,
    evidencia TEXT NOT NULL,
    quitada INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (sesion_id, i)
);
"""
TABLAS = ("fortaleza", "sello", "respuesta", "sesion")


@contextmanager
def _conexion() -> Iterator[sqlite3.Connection]:
    """Abre la base (creando las tablas si faltan) y confirma los cambios al salir sin error."""
    with closing(sqlite3.connect(config.DB_RUTA)) as con:
        con.row_factory = sqlite3.Row
        con.executescript(ESQUEMA)
        with con:
            yield con


def crear_sesion(origen: str | None) -> str:
    sesion_id = uuid.uuid4().hex
    with _conexion() as con:
        con.execute("INSERT INTO sesion (id, origen) VALUES (?, ?)", (sesion_id, origen))
    return sesion_id


def obtener_sesion(sesion_id: str) -> dict[str, Any] | None:
    with _conexion() as con:
        fila = con.execute("SELECT * FROM sesion WHERE id = ?", (sesion_id,)).fetchone()
    return dict(fila) if fila else None


def respuestas(sesion_id: str) -> list[dict[str, Any]]:
    with _conexion() as con:
        filas = con.execute("SELECT * FROM respuesta WHERE sesion_id = ? ORDER BY n", (sesion_id,))
        return [dict(f) for f in filas]


def guardar_respuesta(sesion_id: str, n: int, texto: str, repregunta: str | None) -> None:
    with _conexion() as con:
        con.execute(
            "INSERT INTO respuesta (sesion_id, n, texto, repregunta) VALUES (?, ?, ?, ?)",
            (sesion_id, n, texto, repregunta),
        )


def guardar_respuesta_repregunta(sesion_id: str, n: int, texto: str) -> None:
    with _conexion() as con:
        con.execute(
            "UPDATE respuesta SET respuesta_repregunta = ? WHERE sesion_id = ? AND n = ?",
            (texto, sesion_id, n),
        )


def borrar_respuestas_desde(sesion_id: str, n: int) -> None:
    """Botón Atrás: borra la respuesta n y las siguientes; el pasaporte deja de valer."""
    with _conexion() as con:
        con.execute("DELETE FROM respuesta WHERE sesion_id = ? AND n >= ?", (sesion_id, n))
        con.execute("UPDATE sesion SET pasaporte = 0 WHERE id = ?", (sesion_id,))


def guardar_pasaporte(
    sesion_id: str, sellos: list[dict[str, Any]], fortalezas: list[dict[str, Any]]
) -> None:
    """Reemplaza los sellos y fortalezas de la sesión por los de una nueva extracción."""
    with _conexion() as con:
        con.execute("DELETE FROM sello WHERE sesion_id = ?", (sesion_id,))
        con.execute("DELETE FROM fortaleza WHERE sesion_id = ?", (sesion_id,))
        con.executemany(
            "INSERT INTO sello (sesion_id, orden, codigo, etiqueta, icono, evidencia) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (sesion_id, orden, s["codigo"], s["etiqueta"], s["icono"], s["evidencia"])
                for orden, s in enumerate(sellos)
            ],
        )
        con.executemany(
            "INSERT INTO fortaleza (sesion_id, i, texto, evidencia) VALUES (?, ?, ?, ?)",
            [(sesion_id, i, f["texto"], f["evidencia"]) for i, f in enumerate(fortalezas)],
        )
        con.execute("UPDATE sesion SET pasaporte = 1 WHERE id = ?", (sesion_id,))


def sellos(sesion_id: str) -> list[dict[str, Any]]:
    with _conexion() as con:
        filas = con.execute("SELECT * FROM sello WHERE sesion_id = ? ORDER BY orden", (sesion_id,))
        return [dict(f) for f in filas]


def fortalezas(sesion_id: str) -> list[dict[str, Any]]:
    with _conexion() as con:
        filas = con.execute("SELECT * FROM fortaleza WHERE sesion_id = ? ORDER BY i", (sesion_id,))
        return [dict(f) for f in filas]


def marcar_quitados(sesion_id: str, codigos: set[str], indices: set[int]) -> None:
    """Deja como quitados exactamente esos códigos e índices (el resto vuelve a estar visible)."""
    with _conexion() as con:
        con.execute("UPDATE sello SET quitado = 0 WHERE sesion_id = ?", (sesion_id,))
        con.execute("UPDATE fortaleza SET quitada = 0 WHERE sesion_id = ?", (sesion_id,))
        con.executemany(
            "UPDATE sello SET quitado = 1 WHERE sesion_id = ? AND codigo = ?",
            [(sesion_id, c) for c in codigos],
        )
        con.executemany(
            "UPDATE fortaleza SET quitada = 1 WHERE sesion_id = ? AND i = ?",
            [(sesion_id, i) for i in indices],
        )


def guardar_preferencias(sesion_id: str, interes: str, horas: str) -> None:
    with _conexion() as con:
        con.execute("UPDATE sesion SET interes = ?, horas = ? WHERE id = ?", (interes, horas, sesion_id))


def borrar_todo() -> int:
    """Borra todas las sesiones y sus datos (después de la demo). Devuelve cuántas sesiones había."""
    with _conexion() as con:
        total = con.execute("SELECT COUNT(*) FROM sesion").fetchone()[0]
        for tabla in TABLAS:
            con.execute(f"DELETE FROM {tabla}")
    return total
