"""Rutas HTTP de la API (spec 6). Errores con un solo formato: {"error": {"codigo", "mensaje"}}."""
import logging
from typing import Annotated, Any, Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, StringConstraints
from starlette.exceptions import HTTPException

from app import calculo, config, datos, db, ia

logger = logging.getLogger(__name__)

app = FastAPI(title="Pasaporte Laboral")

ORIGENES = {o["codigo"] for o in datos.OCUPACIONES if o["origen"]}
OCUPACIONES = {o["codigo"]: o for o in datos.OCUPACIONES}
TEXTO_SIMPLE = {c["codigo"]: c["texto_simple"] for c in datos.COMPETENCIAS}


# --- errores


class ErrorApi(Exception):
    """Error que la API devuelve con el formato único."""

    def __init__(self, estado: int, codigo: str, mensaje: str) -> None:
        self.estado, self.codigo, self.mensaje = estado, codigo, mensaje


def _error(estado: int, codigo: str, mensaje: str) -> JSONResponse:
    return JSONResponse(status_code=estado, content={"error": {"codigo": codigo, "mensaje": mensaje}})


@app.exception_handler(ErrorApi)
def _manejar_error_api(_: Request, e: ErrorApi) -> JSONResponse:
    return _error(e.estado, e.codigo, e.mensaje)


@app.exception_handler(RequestValidationError)
def _manejar_validacion(_: Request, e: RequestValidationError) -> JSONResponse:
    return _error(422, "datos_invalidos", "Revisa los datos enviados.")


@app.exception_handler(HTTPException)
def _manejar_http(_: Request, e: HTTPException) -> JSONResponse:
    if e.status_code == 404:
        return _error(404, "no_encontrado", "No encontramos esa dirección.")
    return _error(e.status_code, "error_http", "No pudimos atender este pedido.")


@app.exception_handler(Exception)
def _manejar_inesperado(_: Request, e: Exception) -> JSONResponse:
    logger.error("error inesperado: %s", type(e).__name__)
    return _error(500, "error_interno", "Algo salió mal. Inténtalo de nuevo.")


# --- modelos (spec 6)

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Salud(BaseModel):
    ok: bool
    modo: Literal["real", "respaldo"]


class NuevaSesion(BaseModel):
    ocupacion_origen: str | None


class Pregunta(BaseModel):
    n: int
    texto: str
    ejemplos: list[str]


class SesionCreada(BaseModel):
    sesion_id: str
    saludo: str
    pregunta: Pregunta


class NuevaRespuesta(BaseModel):
    n: int = Field(ge=1, le=6)
    texto: Texto


class Turno(BaseModel):
    tipo: Literal["repregunta", "siguiente", "fin"]
    reaccion: str | None
    pregunta: Pregunta | None
    cierre: str | None
    parcial_listo: bool


class SellosParciales(BaseModel):
    sellos_ganados: int
    etiquetas: list[str]


class Sello(BaseModel):
    codigo: str
    etiqueta: str
    icono: str
    evidencia: str


class Fortaleza(BaseModel):
    texto: str
    evidencia: str


class Pasaporte(BaseModel):
    sellos: list[Sello]
    fortalezas: list[Fortaleza]


class Quitar(BaseModel):
    quitar: list[str]
    quitar_fortalezas: list[int]


class Preferencias(BaseModel):
    interes: Literal["gente", "cosas", "papeles"]
    horas: Literal["1-2", "3-5", "5+"]


class Ok(BaseModel):
    ok: bool


class Curso(BaseModel):
    id: str
    nombre: str
    horas: int
    url: str
    alcance: str
    modulo: str
    se_lleva: str
    semanas: int


class Faltante(BaseModel):
    codigo: str
    etiqueta: str
    curso: Curso | None
    mensaje: str | None


class Destino(BaseModel):
    codigo: str
    nombre: str
    puntaje: float
    cobertura: float
    interes: int
    demanda: float
    tienes: list[str]
    que_harias: list[str]
    faltan: list[Faltante]
    avisos_lima: int


class Ruta(BaseModel):
    foto: str
    destinos: list[Destino]


class Aviso(BaseModel):
    id: str
    perfil: str
    titulo: str
    empresa: str
    distrito: str
    ubigeo: str
    sueldo: str | None
    publicado: str
    cierre: str
    que_piden: list[str]
    url: str
    fuente: str
    tomado: str
    nota: str | None = None


class Avisos(BaseModel):
    avisos: list[Aviso]
    mensaje: str | None


class SelloCv(BaseModel):
    etiqueta: str
    texto_simple: str
    codigos: list[str]


class Cv(BaseModel):
    resumen: str
    puesto: str | None
    anios: str | None
    sellos: list[SelloCv]
    fortalezas: list[Fortaleza]
    destino: str
    curso: Curso | None


# --- ayudas


def _sesion(sesion_id: str) -> dict[str, Any]:
    sesion = db.obtener_sesion(sesion_id)
    if sesion is None:
        raise ErrorApi(404, "sesion_no_existe", "No encontramos esta sesión.")
    return sesion


def _con_pasaporte(sesion_id: str) -> dict[str, Any]:
    sesion = _sesion(sesion_id)
    if not sesion["pasaporte"]:
        raise ErrorApi(409, "falta_pasaporte", "Primero hay que armar el pasaporte.")
    return sesion


def _con_preferencias(sesion_id: str) -> dict[str, Any]:
    sesion = _con_pasaporte(sesion_id)
    if not sesion["interes"] or not sesion["horas"]:
        raise ErrorApi(409, "faltan_preferencias", "Primero elige qué tipo de trabajo te gusta.")
    return sesion


def _destino(codigo: str) -> dict[str, Any]:
    if codigo not in OCUPACIONES:
        raise ErrorApi(422, "destino_invalido", "Ese trabajo no está en el catálogo.")
    return OCUPACIONES[codigo]


def _pregunta(n: int) -> Pregunta:
    return Pregunta(n=n, texto=config.GUION[n]["texto"], ejemplos=config.GUION[n]["ejemplos"])


def _relato(sesion_id: str, hasta: int) -> list[dict[str, Any]]:
    """Respuestas 1 a `hasta` con la forma que usa ia.py: {n, texto, repregunta}."""
    return [
        {"n": r["n"], "texto": r["texto"], "repregunta": r["respuesta_repregunta"]}
        for r in db.respuestas(sesion_id)
        if r["n"] <= hasta
    ]


def _pasaporte_visible(sesion_id: str) -> Pasaporte:
    return Pasaporte(
        sellos=[Sello(**s) for s in _sellos_visibles(sesion_id)],
        fortalezas=[Fortaleza(**f) for f in db.fortalezas(sesion_id) if not f["quitada"]],
    )


def _sellos_visibles(sesion_id: str) -> list[dict[str, Any]]:
    return [
        {k: s[k] for k in ("codigo", "etiqueta", "icono", "evidencia")}
        for s in db.sellos(sesion_id)
        if not s["quitado"]
    ]


# --- endpoints


@app.get("/api/salud", response_model=Salud)
def salud() -> Salud:
    """Indica que la API está viva y si QVAC corre en modo real o respaldo."""
    return Salud(ok=True, modo=config.QVAC_MODO)


@app.post("/api/sesiones", response_model=SesionCreada)
def crear_sesion(entrada: NuevaSesion) -> SesionCreada:
    """Crea una sesión anónima; Caja, Almacén y Limpieza fijan el origen, el resto va sin origen (HU-01)."""
    origen = entrada.ocupacion_origen
    if origen is not None and origen not in ORIGENES:
        raise ErrorApi(422, "origen_invalido", "Ese trabajo no está entre los de inicio.")
    return SesionCreada(sesion_id=db.crear_sesion(origen), saludo=config.TEXTO_SALUDO, pregunta=_pregunta(1))


@app.post("/api/sesiones/{sesion_id}/respuestas", response_model=Turno)
def responder(sesion_id: str, entrada: NuevaRespuesta) -> Turno:
    """Guarda una respuesta y devuelve la reacción con la repregunta, la siguiente pregunta o el cierre."""
    _sesion(sesion_id)
    n, texto = entrada.n, entrada.texto
    previas = db.respuestas(sesion_id)
    ultima = previas[-1] if previas else None
    pendiente = ultima is not None and ultima["repregunta"] and ultima["respuesta_repregunta"] is None
    esperado = ultima["n"] if pendiente else (ultima["n"] + 1 if ultima else 1)

    if pendiente and n == esperado:
        db.guardar_respuesta_repregunta(sesion_id, n, texto)
        reaccion = ia.revisar_respuesta(n, ultima["repregunta"], texto, ya_repregunto=True)["reaccion"]
        return _siguiente(n, reaccion)
    if n > esperado:
        raise ErrorApi(409, "fuera_de_orden", f"Ahora toca la pregunta {esperado}.")
    if n < esperado:
        db.borrar_respuestas_desde(sesion_id, n)

    if n == 6:
        db.guardar_respuesta(sesion_id, n, texto, None)
        return Turno(tipo="fin", reaccion=None, pregunta=None, cierre=config.TEXTO_CIERRE, parcial_listo=False)
    revision = ia.revisar_respuesta(n, config.GUION[n]["texto"], texto, ya_repregunto=False)
    db.guardar_respuesta(sesion_id, n, texto, revision["repregunta"])
    if revision["repregunta"]:
        return Turno(
            tipo="repregunta",
            reaccion=revision["reaccion"],
            pregunta=Pregunta(n=n, texto=revision["repregunta"], ejemplos=[]),
            cierre=None,
            parcial_listo=False,
        )
    return _siguiente(n, revision["reaccion"])


def _siguiente(n: int, reaccion: str) -> Turno:
    return Turno(
        tipo="siguiente",
        reaccion=reaccion,
        pregunta=_pregunta(n + 1),
        cierre=None,
        parcial_listo=n in (2, 3),
    )


@app.post("/api/sesiones/{sesion_id}/sellos-parciales", response_model=SellosParciales)
def sellos_parciales(sesion_id: str) -> SellosParciales:
    """Extracción parcial con las respuestas 1 a 3, solo para el contador del chat (HU-16)."""
    _sesion(sesion_id)
    parcial = ia.extraer_parcial(_relato(sesion_id, 3), datos.COMPETENCIAS)
    if parcial is None:
        raise ErrorApi(503, "parcial_no_disponible", "Todavía no podemos contar tus sellos.")
    return SellosParciales(**parcial)


@app.post("/api/sesiones/{sesion_id}/pasaporte", response_model=Pasaporte)
def armar_pasaporte(sesion_id: str) -> Pasaporte:
    """Extracción completa al terminar las 6 preguntas (spec 4 y 5)."""
    _sesion(sesion_id)
    previas = db.respuestas(sesion_id)
    completa = len(previas) == 6 and not (previas[-1]["repregunta"] and previas[-1]["respuesta_repregunta"] is None)
    if not completa:
        raise ErrorApi(409, "conversacion_incompleta", "Faltan preguntas por responder.")
    try:
        perfil = ia.extraer_perfil(_relato(sesion_id, 6), datos.COMPETENCIAS)
    except ia.ErrorExtraccion:
        raise ErrorApi(502, "relato_no_leido", config.TEXTO_ERROR_EXTRACCION) from None
    db.guardar_pasaporte(sesion_id, perfil["sellos"], perfil["fortalezas"])
    return _pasaporte_visible(sesion_id)


@app.put("/api/sesiones/{sesion_id}/pasaporte", response_model=Pasaporte)
def editar_pasaporte(sesion_id: str, entrada: Quitar) -> Pasaporte:
    """Deja quitados exactamente esos sellos (con los de su misma etiqueta) y fortalezas."""
    _con_pasaporte(sesion_id)
    guardados = db.sellos(sesion_id)
    etiquetas = {s["etiqueta"] for s in guardados if s["codigo"] in entrada.quitar}
    codigos = {s["codigo"] for s in guardados if s["etiqueta"] in etiquetas}
    db.marcar_quitados(sesion_id, codigos, set(entrada.quitar_fortalezas))
    return _pasaporte_visible(sesion_id)


@app.put("/api/sesiones/{sesion_id}/preferencias", response_model=Ok)
def guardar_preferencias(sesion_id: str, entrada: Preferencias) -> Ok:
    """Interés (pantalla de 3 botones) y horas libres (pregunta 6)."""
    _sesion(sesion_id)
    db.guardar_preferencias(sesion_id, entrada.interes, entrada.horas)
    return Ok(ok=True)


@app.get("/api/sesiones/{sesion_id}/ruta", response_model=Ruta)
def ruta(sesion_id: str) -> Ruta:
    """Hasta 3 destinos con su sustento, qué harías, lo que falta con su curso y avisos (spec 6 y 6b)."""
    sesion = _con_preferencias(sesion_id)
    sellos = {s["codigo"] for s in _sellos_visibles(sesion_id)}
    destinos = calculo.afinidad(
        sellos,
        sesion["interes"],
        sesion["origen"],
        datos.OCUPACIONES,
        datos.COMPETENCIAS,
        datos.DEMANDA["perfiles"],
    )
    for d in destinos:
        logger.info(
            "ruta %s: puntaje=%.3f cobertura=%.3f interes=%d demanda=%.2f",
            d["codigo"], d["puntaje"], d["cobertura"], d["interes"], d["demanda"],
        )
    return Ruta(
        foto=datos.DEMANDA["tomado"],
        destinos=[
            Destino(
                **d,
                que_harias=OCUPACIONES[d["codigo"]]["que_harias"],
                faltan=calculo.faltantes(sellos, d["codigo"], datos.COMPETENCIAS, datos.CURSOS, sesion["horas"]),
            )
            for d in destinos
        ],
    )


@app.get("/api/sesiones/{sesion_id}/avisos", response_model=Avisos)
def avisos(sesion_id: str, destino: str) -> Avisos:
    """Hasta 3 avisos reales del destino, o el mensaje fijo si no hay (HU-09)."""
    _sesion(sesion_id)
    _destino(destino)
    return Avisos(**calculo.avisos_para(destino, datos.AVISOS))


@app.get("/api/sesiones/{sesion_id}/cv", response_model=Cv)
def cv(sesion_id: str, destino: str) -> Cv:
    """Datos del CV; nombre y contacto los escribe la persona en la pantalla y no llegan aquí (HU-10)."""
    sesion = _con_preferencias(sesion_id)
    ocupacion = _destino(destino)
    visibles = _sellos_visibles(sesion_id)
    grupos = calculo.agrupar_sellos(visibles)
    respuesta_1 = next(r["texto"] for r in db.respuestas(sesion_id) if r["n"] == 1)
    resumen = ia.redactar_resumen(grupos, respuesta_1, datos.COMPETENCIAS)
    faltan = calculo.faltantes(
        {s["codigo"] for s in visibles}, destino, datos.COMPETENCIAS, datos.CURSOS, sesion["horas"]
    )
    origen = OCUPACIONES.get(sesion["origen"]) if sesion["origen"] else None
    return Cv(
        resumen=resumen["resumen"],
        puesto=origen["nombre_simple"] if origen else None,
        anios=resumen["anios"],
        sellos=[
            SelloCv(etiqueta=g["etiqueta"], texto_simple=TEXTO_SIMPLE[g["codigos"][0]], codigos=g["codigos"])
            for g in grupos
        ],
        fortalezas=[Fortaleza(texto=f["texto"], evidencia=f["evidencia"]) for f in db.fortalezas(sesion_id) if not f["quitada"]],
        destino=ocupacion["nombre"],
        curso=next((f["curso"] for f in faltan if f["curso"]), None),
    )


# --- pantallas (M6): el build de web/ en "/"; las rutas de React devuelven index.html


@app.get("/{ruta:path}", include_in_schema=False)
def pantallas(ruta: str) -> FileResponse:
    """Sirve un archivo de web/dist o, para cualquier otra ruta que no sea de la API, index.html."""
    dist = config.WEB_DIST.resolve()
    indice = dist / "index.html"
    if ruta.startswith("api/") or not indice.is_file():
        raise ErrorApi(404, "no_encontrado", "No encontramos esa dirección.")
    archivo = (dist / ruta).resolve()
    if not archivo.is_relative_to(dist):
        raise ErrorApi(404, "no_encontrado", "No encontramos esa dirección.")
    return FileResponse(archivo if archivo.is_file() else indice)
