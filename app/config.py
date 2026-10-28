"""Configuración y constantes de la app (spec 2). Todo valor fijo vive aquí."""
import os
from pathlib import Path

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

# Palabras que nunca aparecen en textos del asistente (spec 5).
PALABRAS_PROHIBIDAS = ("certificado", "competente", "competencia", "brecha", "no sirves")

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
TEXTO_SIN_CURSO = "Todavía sin curso gratis del MTPE"
TEXTO_SIN_AVISOS = "Hoy no hay avisos en Lima para esto"
TEXTO_SELLOS_GANADOS = "{n} sellos ganados · Sigue contándonos"
TEXTO_SEMANAS_CURSO = "unas {n} semanas con tu tiempo"
TEXTO_MODO_SIN_CONEXION = "modo sin conexión"
