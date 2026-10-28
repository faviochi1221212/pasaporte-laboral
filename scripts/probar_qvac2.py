"""
Segunda prueba de QVAC: ¿por qué el modelo responde vacío?

Sospecha: Qwen "piensa" antes de responder (modo thinking) y ese pensamiento
se come todos los tokens, así que la respuesta final queda vacía.
Este script prueba con el pensamiento APAGADO y ENCENDIDO y muestra qué devuelve.

Uso (PowerShell, con el hotspot del celular si la red de la U bloquea ngrok):
    $env:QVAC_TOKEN="tu_clave"
    python probar_qvac2.py
"""

import json
import os
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("QVAC_BASE_URL", "https://upwind-saucy-overpass.ngrok-free.dev").rstrip("/")
TOKEN = os.environ.get("QVAC_TOKEN", "").strip()
MODEL = os.environ.get("QVAC_MODEL", "qwen-38-27b").strip()

RELATO = (
    "Trabajo de cajera en un supermercado hace 6 años. Cobro en efectivo, tarjeta y Yape, "
    "y al final del día cuadro la caja; si falta plata, busco dónde está el error y lo reporto. "
    "Cuando un cliente se pica por un precio mal marcado, lo calmo y llamo al supervisor si es grave. "
    "A veces ayudo a ordenar la mercadería y reviso precios. A las chicas nuevas les enseño a usar la caja. "
    "Los fines de semana organizo los partidos de fulbito de mi barrio y cobro la cuota para la cancha."
)

TOOL = {
    "type": "function",
    "function": {
        "name": "guardar_relato",
        "description": "Guarda las tareas del trabajo y las fortalezas fuera del trabajo, cada una con la frase textual que la respalda.",
        "parameters": {
            "type": "object",
            "properties": {
                "tareas": {"type": "array", "items": {"type": "object", "properties": {
                    "texto": {"type": "string"}, "evidencia": {"type": "string"}}, "required": ["texto", "evidencia"]}},
                "fortalezas": {"type": "array", "items": {"type": "object", "properties": {
                    "texto": {"type": "string"}, "evidencia": {"type": "string"}}, "required": ["texto", "evidencia"]}},
            },
            "required": ["tareas", "fortalezas"],
        },
    },
}


def llamar(body, intentos=3):
    req_body = json.dumps(body).encode("utf-8")
    for i in range(1, intentos + 1):
        req = urllib.request.Request(
            f"{BASE_URL}/v1/chat/completions", data=req_body, method="POST",
            headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
                     "ngrok-skip-browser-warning": "true"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode("utf-8")), time.time() - t0
        except urllib.error.HTTPError as e:
            txt = e.read().decode("utf-8", errors="replace")[:300]
            if e.code < 500:
                return {"error": f"HTTP {e.code}: {txt}"}, time.time() - t0
            print(f"   intento {i} falló: HTTP {e.code} {txt}")
        except Exception as e:
            print(f"   intento {i} falló: {type(e).__name__}: {e}")
        time.sleep(3)
    return {"error": "sin respuesta"}, 0.0


def mostrar(nombre, data, seg):
    print(f"\n=== {nombre} ({seg:.1f} s) ===")
    if "error" in data:
        print("ERROR:", data["error"])
        return "ERROR"
    ch = data["choices"][0]
    msg = ch.get("message", {})
    pensamiento = msg.get("reasoning_content") or ""
    contenido = msg.get("content") or ""
    calls = msg.get("tool_calls") or []
    print("finish_reason:", ch.get("finish_reason"))
    print("tokens usados:", data.get("usage"))
    print(f"pensamiento: {len(pensamiento)} caracteres")
    print("respuesta:", repr(contenido[:300]))
    if calls:
        f = calls[0]["function"]
        print("llamó a:", f["name"])
        try:
            args = json.loads(f["arguments"]) if isinstance(f["arguments"], str) else f["arguments"]
            for t in args.get("tareas", []):
                print(f"   tarea: {t.get('texto')}  <- \"{t.get('evidencia')}\"")
            for t in args.get("fortalezas", []):
                print(f"   fortaleza: {t.get('texto')}  <- \"{t.get('evidencia')}\"")
            return f"OK tool ({len(args.get('tareas', []))} tareas, {len(args.get('fortalezas', []))} fortalezas)"
        except Exception:
            print("   argumentos no son JSON válido:", str(f["arguments"])[:300])
            return "tool con JSON inválido"
    return "texto" if contenido.strip() else "VACÍO"


def main():
    if not TOKEN:
        print("Falta QVAC_TOKEN.")
        return
    print(f"Probando {MODEL} en {BASE_URL}")
    sin_pensar = {"chat_template_kwargs": {"enable_thinking": False}}
    res = {}

    # A. Chat simple, sin pensar
    d, s = llamar({"model": MODEL, "max_tokens": 200, "temperature": 0, **sin_pensar,
                   "messages": [{"role": "user", "content": "Responde solo: conexión OK"}]})
    res["A. Chat sin pensar"] = (mostrar("A. Chat sin pensar", d, s), s)

    # B. Chat simple, pensando (con más tokens)
    d, s = llamar({"model": MODEL, "max_tokens": 2000, "temperature": 0,
                   "messages": [{"role": "user", "content": "Responde solo: conexión OK"}]})
    res["B. Chat pensando"] = (mostrar("B. Chat pensando", d, s), s)

    sistema = ("Eres un asistente del Ministerio de Trabajo del Perú. Lee el relato y llama SIEMPRE "
               "a la herramienta guardar_relato. No inventes nada que no esté en el relato.")
    base_tool = {"model": MODEL, "temperature": 0, "tools": [TOOL], "tool_choice": "auto",
                 "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": RELATO}]}

    # C. Tool calling sin pensar
    d, s = llamar({**base_tool, "max_tokens": 2000, **sin_pensar})
    res["C. Tool sin pensar"] = (mostrar("C. Tool sin pensar", d, s), s)

    # D. Tool calling pensando, con muchos tokens
    d, s = llamar({**base_tool, "max_tokens": 6000})
    res["D. Tool pensando"] = (mostrar("D. Tool pensando", d, s), s)

    print("\n" + "=" * 60 + "\nRESUMEN (pégame esto)")
    for k, (r, s) in res.items():
        print(f"  {k:22s} {s:5.1f} s  {r}")


if __name__ == "__main__":
    main()
