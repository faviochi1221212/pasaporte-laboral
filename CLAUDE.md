# CLAUDE.md — Pasaporte Laboral

Instrucciones para Claude Code. Léelas completas antes de cada tarea.

## Qué es este proyecto

MVP para la Innovathon ULima x Tether (reto del Ministerio de Trabajo, MTPE). Una persona cuenta en 6 preguntas lo que hace en su trabajo; la app le muestra un "pasaporte" con sellos (tareas reales del Catálogo Nacional de Perfiles Ocupacionales), 3 trabajos parecidos con la explicación de por qué encaja, lo que le falta, cursos gratuitos del MTPE, avisos reales y un CV. La IA corre en QVAC (Tether).

Demo Day: 30 de octubre de 2026. Prioridad: que el recorrido central funcione y se pueda explicar.

## Documentos que mandan (léelos antes de programar)

| Archivo | Qué contiene |
|---|---|
| `docs/spec.md` | La especificación técnica. **Es la fuente de verdad.** |
| `docs/historias.md` | Historias de usuario con criterios de aceptación, módulo y prueba. |
| `docs/checklist.md` | Tareas por módulo (M0 a M8) y su condición de "Hecho cuando". |
| `prompts/Mx.md` | El encargo de cada módulo. |
| `data/*.json` | Datos de referencia ya verificados. No se inventan datos nuevos. |
| `docs/mockup/` | Pantallas de referencia visual (formato .dc.html). Copia estilos y SVG; los textos y números de esos archivos pueden estar desactualizados: los reales vienen de `data/`. |

## Reglas de oro

1. **Si no está en la spec, no se programa.** Si una tarea necesita algo que la spec no dice, detente y pregunta. No agregues funciones, pantallas, endpoints, dependencias ni opciones "por si acaso".
2. **El modelo conversa, extrae y redacta; el código calcula.** Ningún número, ocupación, curso ni aviso que ve el usuario sale del modelo: sale de `data/` o de `app/calculo.py`.
3. **Un sello solo se da con evidencia textual** (spec sección 4). Si el código no existe o la frase no está en lo que escribió la persona, se descarta.
4. **El asistente es amable pero no finge ser humano:** se presenta como asistente del Ministerio, sin nombre de persona ni foto (spec 5b).
5. **Nunca** escribas en textos que ve el usuario palabras que empiecen con "certific" o "competen" (certificado, certificada, certificación, competente, competencia…), ni "brecha" ni "no sirves", sin importar mayúsculas ni tildes. La única excepción es "competencias declaradas", solo en el CV. Usa "lo que contaste que haces" y "lo que te falta".
6. **Datos personales:** no se piden DNI, edad, género, discapacidad ni nivel educativo. Nombre, distrito, teléfono y correo se escriben solo en la pantalla del CV, se quedan en el navegador y nunca se envían al servidor ni se guardan en la base.
7. **Secretos:** el token de QVAC solo en `.env`. Nunca en código, pruebas, fixtures, logs ni commits. Antes de cada commit, revisa que no se cuele.
8. **Prompts de Tether no son privados:** en pruebas y fixtures solo relatos inventados (`tests/relatos/`).

## Stack (no cambiar sin aprobación)

- Backend: Python 3.10, FastAPI, uvicorn, SQLite con el módulo `sqlite3` (sin ORM), httpx para QVAC, pytest. Nada más en `requirements.txt` salvo que la spec lo diga.
- Frontend (solo desde M6): React + TypeScript con Vite, CSS propio primero celular (1 columna hasta 1023 px, 2 columnas desde 1024 px), React Router. Pruebas de pantalla con Playwright en 360 y 1280 px. Sin librerías de componentes ni CSS frameworks.
- QVAC: `POST {QVAC_BASE_URL}/v1/chat/completions` con `Authorization: Bearer`, cabecera `ngrok-skip-browser-warning: true`, `model = qwen-38-27b`, `temperature: 0`, `chat_template_kwargs: {"enable_thinking": false}`, salidas por tool call. El servidor **no** tiene embeddings ni audio.

## Estructura

```
app/            backend (main.py, qvac.py, ia.py, calculo.py, db.py, config.py, datos.py)
data/           JSON de referencia (catálogo, cursos, avisos, demanda) — solo lectura en la app
fixtures/       respuestas grabadas de QVAC para el modo respaldo
web/            frontend React + TS (desde M6)
tests/          pruebas de pytest; tests/relatos/ con los relatos inventados; tests/e2e/ Playwright
scripts/        utilidades (validar datos, verificar textos de PDF, probar QVAC)
docs/           spec, historias, checklist, fuentes (PDF del MTPE) y mockup
prompts/        encargo de cada módulo para Claude Code
```

## Cómo se trabaja (siempre en este orden)

1. Lee `prompts/Mx.md`, la sección de la spec que cita y las historias del módulo.
2. Escribe primero las pruebas que prueban los criterios de aceptación. Córrelas y confirma que fallan.
3. Escribe el código mínimo para que pasen.
4. Corre **todas** las pruebas: `pytest -q`. No sigas si algo falla.
5. Revisa tu propio cambio contra las reglas de oro y las buenas prácticas.
6. Actualiza `docs/checklist.md` (marca la tarea) y, si cambió algo visible, el `README.md`.
7. Propón el mensaje de un commit pequeño, en español: `M2: afinidad con desempate (A6)`. **Claude Code nunca hace `git commit` ni `git push`:** solo propone el mensaje y el commit lo hace la persona.

No empieces un módulo hasta que el anterior cumpla su "Hecho cuando" del checklist.

## Buenas prácticas de código

- Español en nombres de dominio (`sello`, `afinidad`, `faltantes`), docstrings y comentarios. Inglés solo en nombres técnicos estándar.
- Funciones cortas y puras en `calculo.py`: reciben datos, devuelven datos, sin leer archivos ni llamar a la red. Eso las hace fáciles de probar.
- Constantes en un solo lugar (`app/config.py`): pesos 0.60 / 0.25 / 0.15, horas por semana (1.5 / 4 / 6), máximo de destinos (3), máximo de avisos (3), mínimo de palabras (6), textos fijos que ve el usuario.
- Tipos en todas las funciones (type hints en Python, TypeScript estricto en el frontend). Modelos Pydantic para entrada y salida de cada endpoint, iguales a la spec sección 6.
- Errores de la API con un solo formato: `{"error": {"codigo": "...", "mensaje": "..."}}` y el código HTTP correcto. Nunca exponer trazas.
- Logs: tiempo de cada llamada a QVAC y descartes de sellos (código y motivo). Nunca el token ni el texto completo de la persona.
- Nada de código muerto, comentado o "para después". Si no se usa, no existe.
- Cada prueba nombra el criterio que prueba: `test_a6_ordena_por_puntaje_y_desempata`.

## Comandos

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                     # y pon tu token en .env
python scripts/validar_datos.py                          # datos coherentes
pytest -q                                                # todas las pruebas (sin internet)
pytest -q -m qvac                                        # solo pruebas contra QVAC real (requiere token y hotspot)
uvicorn app.main:app --reload                            # API en http://127.0.0.1:8000/docs
```

Las pruebas que llaman a QVAC real se marcan con `@pytest.mark.qvac` y no corren por defecto. La red de la ULima bloquea ngrok: usa el hotspot del celular.

## Modo respaldo

`QVAC_MODO=respaldo` hace que `app/qvac.py` responda con lo grabado en `fixtures/` en vez de llamar a la red. Las pruebas por defecto usan este modo. La interfaz muestra una marca pequeña "modo sin conexión" cuando está activo.
