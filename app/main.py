"""Rutas HTTP de la API (spec 6)."""
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app import config

app = FastAPI(title="Pasaporte Laboral")


class Salud(BaseModel):
    """Estado de la API y modo de QVAC en uso."""

    ok: bool
    modo: Literal["real", "respaldo"]


@app.get("/api/salud", response_model=Salud)
def salud() -> Salud:
    """Indica que la API está viva y si QVAC corre en modo real o respaldo."""
    return Salud(ok=True, modo=config.QVAC_MODO)
