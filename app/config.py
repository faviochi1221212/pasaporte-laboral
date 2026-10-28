"""Configuración y constantes de la app (spec 2). Todo valor fijo vive aquí."""
import os
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parent.parent
MODOS = ("real", "respaldo")


def cargar_env(ruta: Path) -> None:
    """Pasa las variables de un archivo .env a os.environ.

    Ignora líneas vacías y comentarios, y no sobrescribe variables que ya existen.
    """
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip())


def normalizar_modo(valor: str | None) -> str:
    """Devuelve el modo de QVAC; cualquier valor no válido cae en "respaldo"."""
    return valor if valor in MODOS else "respaldo"


cargar_env(RAIZ / ".env")

# QVAC (spec 2). El token nunca se imprime ni se registra.
QVAC_TOKEN: str = os.environ.get("QVAC_TOKEN", "")
QVAC_BASE_URL: str = os.environ.get("QVAC_BASE_URL", "")
QVAC_MODEL: str = os.environ.get("QVAC_MODEL", "")
QVAC_MODO: str = normalizar_modo(os.environ.get("QVAC_MODO"))
QVAC_GRABAR: bool = os.environ.get("QVAC_GRABAR", "0") == "1"
QVAC_INTENTOS = 3
QVAC_TIMEOUT = 20.0  # segundos de espera por intento
QVAC_PAUSA = 1.0  # segundos entre intentos
QVAC_MAX_TOKENS = 2000

# Base de datos local (spec 9b): sin datos personales.
DB_RUTA = RAIZ / "pasaporte.db"

# Build de las pantallas (M6), servido por FastAPI en "/".
WEB_DIST = RAIZ / "web" / "dist"

# Afinidad (spec 6): 0,60 × cobertura + 0,25 × interés + 0,15 × demanda.
PESO_COBERTURA = 0.60
PESO_INTERES = 0.25
PESO_DEMANDA = 0.15

# Horas libres por semana según la pregunta 6 (spec 6b, caso 5).
HORAS_POR_SEMANA: dict[str, float] = {"1-2": 1.5, "3-5": 4, "5+": 6}

MAX_DESTINOS = 3
MAX_AVISOS = 3
MIN_PALABRAS = 6
MAX_PALABRAS_REACCION = 12
MAX_PALABRAS_REPREGUNTA = 15
MAX_SELLOS_RESUMEN = 3

# Inicios prohibidos en textos que ve el usuario (spec 5): bloquean toda palabra que empiece así,
# comparando sin mayúsculas ni tildes (certificada, certificación, competente, competencia…).
PALABRAS_PROHIBIDAS = ("certific", "competen", "brecha", "no sirves")

# Textos fijos que ve el usuario (spec 5, 5b, 6b y 7).
TEXTO_SALUDO = (
    "¡Hola! 👋 Soy el asistente de empleo del Ministerio de Trabajo. "
    "Te haré 6 preguntas cortas sobre lo que haces. No hay respuestas buenas ni malas."
)
TEXTO_REACCION_FIJA = "Gracias por contarme."
TEXTO_REPREGUNTA_FIJA = "¿Me das un ejemplo de algo que hiciste esta semana?"
TEXTO_REPREGUNTA_FUERA_DEL_TRABAJO = "¿Y qué haces tú ahí?"
TEXTO_CIERRE = "¡Gracias! Con lo que me contaste estoy armando tu pasaporte…"
TEXTO_ERROR_EXTRACCION = "No pudimos leer tu relato, inténtalo de nuevo"
TEXTO_SIN_CURSO = "No encontramos un curso gratuito del MTPE que cubra esto"
TEXTO_SIN_AVISOS = "Hoy no hay avisos en Lima para esto"
TEXTO_SELLOS_GANADOS = "{n} sellos ganados · Sigue contándonos"
TEXTO_SEMANAS_CURSO = "unas {n} semanas con tu tiempo"
TEXTO_MODO_SIN_CONEXION = "modo sin conexión"
TEXTO_RESUMEN_PLANTILLA = "Experiencia práctica en: {tareas}."

# Guion de las 6 preguntas, copiado de docs/mockup/V3Guion.dc.html (spec 5). Los textos de las
# preguntas 1 a 5 forman parte de los mensajes al modelo: si cambian, hay que volver a grabar fixtures.
GUION: dict[int, dict[str, Any]] = {
    1: {"texto": "¿Cuánto tiempo llevas en esto?", "ejemplos": ["Menos de 1 año", "1 a 5 años", "Más de 5"]},
    2: {"texto": "¿Qué haces en un día normal?", "ejemplos": ["Cobro", "Cuadro la caja", "Ordeno productos"]},
    3: {
        "texto": "¿Qué te piden a ti porque lo haces bien?",
        "ejemplos": ["Cuadrar la caja", "Enseñar a nuevos", "Calmar clientes"],
    },
    4: {
        "texto": "¿Haces algo más aparte de tu trabajo?",
        "ejemplos": ["Un negocio", "Cachuelos", "Ayudo en mi barrio"],
    },
    5: {
        "texto": "¿Qué te gusta hacer en tu tiempo libre?",
        "ejemplos": ["Deporte", "Cocinar", "Arreglar cosas"],
    },
    6: {"texto": "¿Cuánto tiempo tienes para aprender?", "ejemplos": ["1 a 2 h", "3 a 5 h", "Más de 5 h"]},
}
