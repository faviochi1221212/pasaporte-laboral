# Checklist de implementación

Se avanza en orden. Un módulo empieza cuando el anterior cumple su "Hecho cuando". Cada tarea cita la sección de `docs/spec.md` que la define y la historia de `docs/historias.md` que la pide. Marca `[x]` al terminar.

Orden: **M0 a M5 = backend probado por su API** (se revisa en `http://127.0.0.1:8000/docs`) → **M6 = pantallas** → M7 demo → M8 verificación.

## M0 · Base del repositorio (spec 2)

- [ ] Carpetas `app/`, `fixtures/`, `tests/`, `tests/relatos/` (ya existe), `web/` vacía
- [ ] `requirements.txt` con fastapi, uvicorn, httpx, pytest (ya existe; no agregar más)
- [ ] `app/config.py` con constantes y lectura de `.env` (QVAC_TOKEN, QVAC_BASE_URL, QVAC_MODEL, QVAC_MODO)
- [ ] `app/main.py` con `GET /api/salud` que responde `{"ok": true, "modo": "real" o "respaldo"}`
- [ ] `pytest.ini` con el marcador `qvac` excluido por defecto
- [ ] Prueba `test_salud`

Hecho cuando: `uvicorn app.main:app` levanta, `pytest -q` pasa y `git grep` no encuentra el token.

## M1 · Datos (spec 3 y 6b) — casi listo

- [x] `ocupaciones.json` y `competencias.json` desde los 6 PDF (26 elementos), verificados con `scripts/verificar_textos_pdf.py`
- [x] `cursos.json` con los 2 cursos, horas, url, alcance y códigos que cubren
- [x] `demanda.json`: foto de Empleos Perú del 27 oct 2026, 19:58, con palabras clave y conteo por perfil
- [x] `avisos.json`: hasta 3 avisos reales por perfil con `que_piden` copiado del aviso
- [x] `scripts/validar_datos.py` pasa
- [ ] Revisión humana del equipo: etiquetas de los sellos, `texto_simple`, `que_harias` y tabla de cursos
- [ ] Actualizar la foto de avisos y demanda el 29 o 30 de octubre (los avisos de recepción cierran el 30 y 31)

Hecho cuando: `python scripts/validar_datos.py` dice OK y el equipo aprobó las etiquetas.

## M2 · Cálculos sin IA: `app/calculo.py` (spec 4, 6, 6b) — HU-04, 05, 06, 07, 08, 09, 13

- [ ] `normalizar()` y `evidencia_valida(frase, respuestas)`
- [ ] `otorgar_sellos(propuestas, respuestas, competencias, quitados)` con las 3 condiciones y agrupación por etiqueta
- [ ] `afinidad(sellos, interes, origen, ocupaciones, competencias, demanda)` con fórmula, descarte de 0 compartidos, desempate y máximo 3
- [ ] `faltantes()` y `curso_para(codigo, horas_libres)` con semanas redondeadas hacia arriba y alcance
- [ ] `avisos_para(perfil)` con máximo 3 y mensaje si no hay
- [ ] Registro de "tareas sin curso" para la lámina de hallazgos
- [ ] Pruebas A5, A6 y A7 con datos fijos (sin internet)

Hecho cuando: `pytest -q` pasa sin conexión y cada prueba nombra su criterio.

## M3 · Cliente de QVAC: `app/qvac.py` (spec 5 y 7) — HU-15

- [ ] `llamar_tool(nombre_tarea, mensajes, tool)` con Bearer, `enable_thinking: false`, temperatura 0, timeout y 3 reintentos
- [ ] Log de tiempo por llamada, sin token ni texto de la persona
- [ ] Modo respaldo: responde desde `fixtures/{tarea}/{clave}.json`; si no hay fixture, error claro
- [ ] Prueba con un servidor falso (sin red) de reintentos y modo respaldo

Hecho cuando: las pruebas pasan sin red y una llamada real (`pytest -m qvac`) devuelve una tool call en menos de 8 s.

## M4 · Las 3 tareas del modelo: `app/ia.py` (spec 5) — HU-02, 04, 10

- [ ] `revisar_respuesta`: tool con reaccion, suficiente, menciona_actividad y repregunta; validación de la reacción (12 palabras, sin palabras prohibidas) y respaldos (spec 5)
- [ ] `extraer_perfil`: lista cerrada de 26 elementos con `texto_simple` y `criterios_clave`, tool, validación y un reintento; versión parcial con las respuestas 1 a 3
- [ ] `redactar_resumen`: 2 frases y plantilla de respaldo
- [ ] Pruebas A1 a A4 y A12 contra QVAC real con `tests/relatos/` (marcador `qvac`); sus respuestas se graban en `fixtures/`
- [ ] Las mismas pruebas pasan en modo respaldo leyendo esos fixtures

Hecho cuando: A1 a A4 pasan dos veces seguidas contra QVAC con el mismo resultado, y en modo respaldo sin red.

## M5 · Backend: `app/db.py` y `app/main.py` (spec 6 y 9b) — HU-01, 02, 04, 05, 06, 13, 15

- [ ] SQLite con 4 tablas: sesion, respuesta, sello, fortaleza (id anónimo, sin datos personales)
- [ ] Los 9 endpoints de la spec 6 con modelos Pydantic iguales a la spec (incluye saludo, reacción, cierre y sellos-parciales)
- [ ] Guion fijo de 6 preguntas con máximo una repregunta y la regla de las preguntas 4 y 5
- [ ] Formato único de errores
- [ ] `scripts/borrar_sesiones.py` para después de la demo
- [ ] Prueba de recorrido completo de María por la API en modo respaldo (A8), y prueba de que una falla en sellos-parciales no rompe el recorrido (A13)

Hecho cuando: el recorrido de María funciona desde `/docs` y desde la prueba, en modo real y en respaldo.

## M6 · Pantallas: `web/` React + TypeScript (mockup v3) — HU-01 a HU-10, HU-14

- [ ] Proyecto Vite + React + TS estricto; FastAPI sirve el build en `/`
- [ ] Estilos: variables CSS con los colores del mockup (`docs/mockup/LEEME.md`), Roboto, 1 columna hasta 1023 px y 2 desde 1024 px
- [ ] Componentes reutilizables: `Sello`, `Trabajador`, `Pasaporte`, `BarraProgreso`, `Boton`
- [ ] Pantallas: Inicio, Conversación en formato chat (spec 5b: burbujas, "escribiendo…", texto de a poco, reacciones, contador de sellos, dictado), Espera, Pasaporte, Intereses, Ruta, Destino, Avisos, CV
- [ ] Banda "Prototipo · no es un sitio oficial" y marca de "modo sin conexión"
- [ ] Textos sin "competencia", "brecha" ni "certificado" (salvo "competencias declaradas" en el CV)
- [ ] Pruebas Playwright e2e-01 a e2e-07 en 360 y 1280 px con capturas

Hecho cuando: A10 y A11 pasan y las capturas se revisaron a ojo en los dos tamaños.

## M7 · Demo y pitch

- [ ] Relato de María ensayado y grabado en `fixtures/`
- [ ] Guion de 30 segundos: relato → sellos → 3 trabajos → por qué
- [ ] Hotspot probado en el lugar del Demo Day
- [ ] Modo respaldo probado con el wifi apagado
- [ ] Lámina "Lo que encontramos en nuestra revisión inicial": tareas sin curso, perfil vencido (Atención por teléfono), perfiles que no existen (vendedor, auxiliar administrativo)
- [ ] README final con pipeline, 3 tareas del modelo, fórmula, límites, fuentes y resultado de A1 a A13

Hecho cuando: el pitch de 3 minutos sale dos veces seguidas sin depender del wifi.

## M8 · Verificación final (spec 9)

- [ ] A1 a A13 pasan y el resultado está en el README
- [ ] Una persona que no programó hace el recorrido sola
- [ ] Revisión: ningún dato de pantalla viene del modelo sin pasar por `data/` o la regla del sello
- [ ] `git grep` no encuentra el token ni datos reales de personas
