"""
Prueba rápida de la API de QVAC (Tether) para la Innovathon ULima x Tether.

Responde 4 preguntas antes de construir el MVP:
  1. Conexión: ¿el token y la URL funcionan? ¿qué modelos hay?
  2. Tool calling: ¿el modelo llama bien a `guardar_relato` con un relato de cajera?
  3. Embeddings y voz: ¿el servidor tiene /v1/embeddings y /v1/audio/transcriptions?
  4. Tiempo: ¿cuántos segundos tarda cada llamada?

Uso (no necesita instalar nada, solo Python 3.8+):
  Mac/Linux:
    export QVAC_TOKEN="tu_clave_del_correo"
    python3 probar_qvac.py
  Windows (PowerShell):
    $env:QVAC_TOKEN="tu_clave_del_correo"
    python probar_qvac.py

Opcional:
  QVAC_BASE_URL  -> por defecto la URL pública de ngrok del PDF de Tether.
                    Si usas Holesail: http://127.0.0.1:8989
  QVAC_MODEL     -> si /v1/models no lista modelos, pon aquí el nombre que te den.

Nunca subas tu token a GitHub: guárdalo en un .env que esté en el .gitignore.
"""

import io
import json
import os
import struct
import sys
import time
import urllib.error
import urllib.request
import uuid
import wave

BASE_URL = os.environ.get(
    "QVAC_BASE_URL", "https://upwind-saucy-overpass.ngrok-free.dev"
).rstrip("/")
TOKEN = os.environ.get("QVAC_TOKEN", "").strip()
MODEL = os.environ.get("QVAC_MODEL", "").strip()
RETRIES = 5          # Tether avisa que la conexión falla a veces: reintentamos
TIMEOUT = 120        # segundos por llamada

RESULTADOS = []      # (prueba, ok, detalle, segundos)


# ----------------------------------------------------------------- utilidades

def headers(extra=None):
    h = {
        "Authorization": f"Bearer {TOKEN}",
        # ngrok gratis muestra una página de aviso si no se envía este header
        "ngrok-skip-browser-warning": "true",
    }
    if extra:
        h.update(extra)
    return h


def llamar(method, path, body=None, content_type="application/json"):
    """Hace la petición con reintentos. Devuelve (status, data, segundos)."""
    url = f"{BASE_URL}{path}"
    if body is not None and content_type == "application/json":
        body = json.dumps(body).encode("utf-8")
    ultimo_error = None
    for intento in range(1, RETRIES + 1):
        req = urllib.request.Request(
            url, data=body, method=method,
            headers=headers({"Content-Type": content_type} if body is not None else None),
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                raw = r.read().decode("utf-8", errors="replace")
                seg = time.time() - t0
                try:
                    return r.status, json.loads(raw), seg
                except json.JSONDecodeError:
                    return r.status, raw, seg
        except urllib.error.HTTPError as e:
            seg = time.time() - t0
            raw = e.read().decode("utf-8", errors="replace")
            # 4xx = respuesta real del servidor (no reintentar). 5xx/502 = reintentar
            if e.code < 500:
                return e.code, raw, seg
            ultimo_error = f"HTTP {e.code}: {raw[:200]}"
        except Exception as e:  # conexión caída, timeout, etc.
            ultimo_error = f"{type(e).__name__}: {e}"
        print(f"   intento {intento}/{RETRIES} falló ({ultimo_error}); reintentando…")
        time.sleep(min(2 * intento, 8))
    return None, ultimo_error, 0.0


def registrar(prueba, ok, detalle, seg=0.0):
    RESULTADOS.append((prueba, ok, detalle, seg))
    marca = "OK " if ok else "NO "
    t = f" ({seg:.1f} s)" if seg else ""
    print(f"[{marca}] {prueba}{t}: {detalle}\n")


# ---------------------------------------------------------------- las pruebas

def prueba_modelos():
    global MODEL
    print("1a. Listando modelos (/v1/models)…")
    status, data, seg = llamar("GET", "/v1/models")
    if status == 200 and isinstance(data, dict) and data.get("data"):
        ids = [m.get("id") for m in data["data"]]
        if not MODEL:
            MODEL = ids[0]
        registrar("Modelos disponibles", True, ", ".join(map(str, ids)), seg)
    else:
        registrar("Modelos disponibles", False,
                  f"status={status}. Se usará QVAC_MODEL='{MODEL or '(vacío)'}'. Detalle: {str(data)[:200]}", seg)


def prueba_conexion():
    print("1b. Probando una respuesta simple (/v1/chat/completions)…")
    body = {
        "messages": [{"role": "user", "content": "Responde solo: 'conexión OK'."}],
        "max_tokens": 20,
        "temperature": 0,
    }
    if MODEL:
        body["model"] = MODEL
    status, data, seg = llamar("POST", "/v1/chat/completions", body)
    if status == 200 and isinstance(data, dict):
        texto = data["choices"][0]["message"].get("content", "")
        registrar("Conexión y chat", True, f"respondió: {texto.strip()[:80]!r}", seg)
        return True
    registrar("Conexión y chat", False, f"status={status}. {str(data)[:300]}", seg)
    return False


RELATO_CAJERA = (
    "Trabajo de cajera en un supermercado hace 6 años. Cobro en efectivo, tarjeta y Yape, "
    "y al final del día cuadro la caja; si falta plata, busco dónde está el error y lo reporto. "
    "Cuando un cliente se pica por un precio mal marcado, lo calmo y llamo al supervisor si es grave. "
    "A veces ayudo a ordenar la mercadería y reviso precios. A las chicas nuevas les enseño a usar la caja. "
    "Los fines de semana organizo los partidos de fulbito de mi barrio y cobro la cuota para la cancha."
)

TOOL_GUARDAR_RELATO = {
    "type": "function",
    "function": {
        "name": "guardar_relato",
        "description": (
            "Guarda lo que la persona hace, separando las tareas de su trabajo de las fortalezas "
            "que muestra fuera de él. Cada ítem lleva la frase textual que lo respalda."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "tareas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "texto": {"type": "string", "description": "Tarea concreta, en una frase corta"},
                            "evidencia": {"type": "string", "description": "Frase textual del relato"},
                        },
                        "required": ["texto", "evidencia"],
                    },
                },
                "fortalezas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "texto": {"type": "string"},
                            "evidencia": {"type": "string"},
                        },
                        "required": ["texto", "evidencia"],
                    },
                },
            },
            "required": ["tareas", "fortalezas"],
        },
    },
}


def prueba_tool_calling():
    print("2. Probando tool calling con el relato de una cajera…")
    body = {
        "messages": [
            {"role": "system", "content": (
                "Eres un asistente del Ministerio de Trabajo del Perú. Lee el relato y llama SIEMPRE "
                "a la herramienta guardar_relato. No inventes nada que no esté en el relato."
            )},
            {"role": "user", "content": RELATO_CAJERA},
        ],
        "tools": [TOOL_GUARDAR_RELATO],
        "tool_choice": "auto",
        "temperature": 0,
        "max_tokens": 1500,
    }
    if MODEL:
        body["model"] = MODEL
    status, data, seg = llamar("POST", "/v1/chat/completions", body)
    if status != 200 or not isinstance(data, dict):
        registrar("Tool calling", False, f"status={status}. {str(data)[:300]}", seg)
        return
    msg = data["choices"][0]["message"]
    calls = msg.get("tool_calls") or []
    if not calls:
        registrar("Tool calling", False,
                  f"el modelo respondió texto en vez de llamar a la tool: {str(msg.get('content'))[:200]!r}", seg)
        return
    call = calls[0]["function"]
    try:
        args = json.loads(call["arguments"]) if isinstance(call["arguments"], str) else call["arguments"]
    except json.JSONDecodeError:
        registrar("Tool calling", False, f"llamó a {call['name']} pero el JSON es inválido: {call['arguments'][:200]}", seg)
        return
    tareas, fortalezas = args.get("tareas", []), args.get("fortalezas", [])
    sin_evidencia = [t for t in tareas + fortalezas if t.get("evidencia", "") not in RELATO_CAJERA]
    print("   Tareas extraídas:")
    for t in tareas:
        print(f"    - {t.get('texto')}   <- \"{t.get('evidencia')}\"")
    print("   Otras fortalezas:")
    for f in fortalezas:
        print(f"    - {f.get('texto')}   <- \"{f.get('evidencia')}\"")
    ok = call["name"] == "guardar_relato" and len(tareas) >= 3 and len(fortalezas) >= 1
    detalle = f"{len(tareas)} tareas, {len(fortalezas)} fortalezas"
    if sin_evidencia:
        detalle += f"; {len(sin_evidencia)} evidencias no son textuales (revisar prompt)"
    registrar("Tool calling", ok, detalle, seg)


def prueba_embeddings():
    print("3a. Probando embeddings (/v1/embeddings)…")
    body = {"input": ["cuadro la caja al final del día", "Realizar el arqueo de caja"]}
    if MODEL:
        body["model"] = MODEL
    status, data, seg = llamar("POST", "/v1/embeddings", body)
    if status == 200 and isinstance(data, dict) and data.get("data"):
        a, b = data["data"][0]["embedding"], data["data"][1]["embedding"]
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(y * y for y in b) ** 0.5
        sim = dot / (na * nb) if na and nb else 0
        registrar("Embeddings", True, f"dimensión {len(a)}, similitud caja/arqueo = {sim:.2f}", seg)
    else:
        registrar("Embeddings", False,
                  f"no disponible (status={status}). Plan B: embeddings con el SDK de QVAC en el backend.", seg)


def audio_silencio():
    """Genera 1 segundo de silencio en WAV para probar si el endpoint existe."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(struct.pack("<h", 0) * 16000)
    return buf.getvalue()


def prueba_transcripcion():
    print("3b. Probando voz a texto (/v1/audio/transcriptions)…")
    boundary = uuid.uuid4().hex
    partes = []
    campos = {"response_format": "json"}
    if MODEL:
        campos["model"] = MODEL
    for k, v in campos.items():
        partes.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    partes.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"prueba.wav\"\r\n"
        f"Content-Type: audio/wav\r\n\r\n".encode() + audio_silencio() + b"\r\n"
    )
    partes.append(f"--{boundary}--\r\n".encode())
    status, data, seg = llamar(
        "POST", "/v1/audio/transcriptions", b"".join(partes),
        content_type=f"multipart/form-data; boundary={boundary}",
    )
    if status == 200:
        registrar("Voz a texto", True, f"endpoint disponible. Respuesta: {str(data)[:120]}", seg)
    elif status in (400, 422):
        registrar("Voz a texto", True,
                  f"el endpoint existe (status={status}), pero pide otro modelo o parámetro: {str(data)[:150]}", seg)
    else:
        registrar("Voz a texto", False,
                  f"no disponible (status={status}). Plan B: Whisper con el SDK de QVAC en el backend.", seg)


# ---------------------------------------------------------------------- main

def main():
    if not TOKEN:
        print("Falta el token. Ejecuta primero:  export QVAC_TOKEN=\"tu_clave\"  (o $env:QVAC_TOKEN en Windows)")
        sys.exit(1)
    print(f"Probando QVAC en {BASE_URL}\n")
    prueba_modelos()
    if not prueba_conexion():
        print("Sin conexión no tiene sentido seguir. Revisa el token, la URL o prueba con Holesail.")
    else:
        prueba_tool_calling()
        prueba_embeddings()
        prueba_transcripcion()

    print("=" * 60)
    print("RESUMEN")
    for prueba, ok, detalle, seg in RESULTADOS:
        t = f"{seg:5.1f} s" if seg else "   -   "
        print(f"  {'OK' if ok else 'NO'}  {t}  {prueba}: {detalle[:90]}")
    tiempos = [s for _, ok, _, s in RESULTADOS if ok and s]
    if tiempos:
        print(f"\n  Tiempo promedio por llamada exitosa: {sum(tiempos) / len(tiempos):.1f} s")


if __name__ == "__main__":
    main()
