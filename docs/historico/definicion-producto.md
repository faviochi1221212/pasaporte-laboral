> **Documento histórico (24 oct 2026).** Se conserva para contexto: KPIs, requerimientos no funcionales y modelo de datos original. Donde contradiga a `docs/spec.md` o `docs/historias.md`, mandan esos dos.

# Definición del producto (MVP)

Esta pestaña define qué construimos y cómo, para que mockup, backend y pitch partan de lo mismo. El contexto del reto y el pipeline están en la pestaña principal.

## Alcance del MVP

El MVP lleva a una persona de "no sé qué sé" a una ruta concreta (ocupación afín con evidencia, un curso y su CV) en una sola conversación, con la cajera como recorrido completo y los otros 4 perfiles con datos cargados.

| Prioridad | Funcionalidad | Por qué |
|---|---|---|
| Debe | Elegir ocupación de origen (5 perfiles + "Otro / hago de todo") | Mínimo del MTPE |
| Debe | Entrevista guiada de 6 preguntas por texto | Descubre lo que no sabe nombrar |
| Debe | Extracción y traducción a competencias del catálogo por tool calls | Sustento técnico; valor para Tether |
| Debe | Confirmación de competencias y otras fortalezas | Mecanismo de validación del MTPE |
| Debe | 3 ocupaciones afines con lo compartido, lo que falta y la demanda | Mínimo del MTPE + deseable de demanda |
| Debe | Integración visual con gob.pe | Requisito de las bases |
| Debe | README con pipeline, tools y decisiones | Revisión del repositorio por Tether |
| Debería | Respuesta por voz (Whisper) | Accesibilidad; usa más del stack de QVAC |
| Debería | Pantalla de intereses (3 botones) | El MTPE pidió considerar el perfil vocacional |
| Debería | Curso recomendado según horas libres | Primer paso formativo realista |
| Debería | CV en PDF con "competencias declaradas" | Presentarse ante un empleador |
| Podría | Perfil con DNI + clave de 4 dígitos (simulado) | Volver y ver su avance |
| Podría | Avisos afines de Empleos Perú (lista guardada) | Conectar con oportunidades reales |
| Podría | Panel de métricas para el MTPE | Medir impacto |
| Podría | App publicada con QR para el jurado | Alberto lo valora |
| No ahora | Login real con la identidad del Estado | Requiere acceso del Estado |
| No ahora | Voz de salida (texto a voz) | El servidor de QVAC no lo ofrece |
| No ahora | Avisos en tiempo real o scraping | Los portales lo bloquean; no suma al mínimo |
| No ahora | Recorrido completo de los 5 perfiles al mismo nivel | Un grupo acotado basta, según el MTPE |

## Épicas e historias de usuario

13 historias en 6 épicas. Cada una tiene su prioridad y sus criterios de aceptación; una historia está terminada solo si cumple todos.

### Épica 1 — Empezar

**HU-01 · Debe.** Como trabajador, quiero elegir mi trabajo con un toque, para empezar sin escribir.

- Dado que abro la herramienta, cuando cargo la primera pantalla, entonces veo un saludo de una línea y 6 tarjetas: 5 ocupaciones con ícono y "Otro / hago de todo".
- Dado que toco una tarjeta, cuando avanzo, entonces se crea una sesión sin pedirme datos personales.
- Dado que elijo "Otro", cuando avanzo, entonces la primera pregunta es "¿En qué trabajas o qué haces para ganar dinero?".

### Épica 2 — Descubrir lo que sabe

**HU-02 · Debe.** Como trabajador, quiero contar lo que hago respondiendo preguntas sencillas, para no llenar formularios.

- Dado que estoy en la entrevista, cuando veo una pregunta, entonces aparece sola en pantalla con 2 o 3 respuestas de ejemplo tocables y un campo de texto.
- Dado que respondo, cuando la respuesta es vaga, entonces el asistente hace como máximo una repregunta corta.
- Dado que respondo las preguntas 4 o 5, cuando menciono una actividad, entonces me pregunta "¿Y qué haces tú ahí?".
- Dado que termino las 6 preguntas, cuando avanzo, entonces veo "Paso 3 de 5".

**HU-03 · Debería.** Como trabajador, quiero responder hablando, para no tener que escribir.

- Dado que toco el micrófono, cuando termino de hablar, entonces veo mi respuesta transcrita y puedo corregirla antes de enviarla.
- Dado que el audio no se entiende, cuando falla la transcripción, entonces leo "No te escuché bien, ¿puedes repetirlo o escribirlo?".

**HU-04 · Debe.** Como trabajador, quiero ver en palabras simples lo que sé hacer, para reconocer el valor de mi experiencia.

- Dado que terminé la entrevista, cuando se procesa, entonces veo "Esto sabes hacer" con las competencias del catálogo en lenguaje simple y, aparte, "Otras fortalezas que encontramos".
- Dado que veo una competencia, cuando la toco, entonces veo la frase mía que la sustenta.
- Dado que algo no lo hago, cuando lo quito, entonces no se usa en el matching ni en el CV.
- Dado que el proceso tarda, cuando espero, entonces leo un mensaje como "Estoy revisando lo que me contaste…".

### Épica 3 — Explorar trabajos

**HU-05 · Debería.** Como trabajador, quiero decir qué tipo de trabajo me gusta, para que las opciones me calcen.

- Dado que confirmé mis competencias, cuando avanzo, entonces elijo entre 3 botones: con gente, con cosas y orden, con papeles y números.

**HU-06 · Debe.** Como trabajador, quiero ver trabajos parecidos al mío, para saber a dónde moverme sin empezar de cero.

- Dado que tengo competencias confirmadas, cuando veo mis resultados, entonces aparecen 3 ocupaciones ordenadas por cercanía, interés y demanda.
- Cada tarjeta muestra el nombre, la cercanía en puntos (por ejemplo, 7 de 10) y una etiqueta de demanda en mi región.
- Ningún dato de la tarjeta lo inventa el modelo: todo viene de `calcular_afinidad`.

**HU-07 · Debe.** Como trabajador, quiero entender por qué encajo en un trabajo, para confiar en la recomendación.

- Dado que toco una ocupación, cuando se abre el detalle, entonces veo en verde lo que ya sé y en ámbar lo que me falta, cada competencia con su código del catálogo.
- Primero se muestra lo que ya sé y después lo que me falta.

### Épica 4 — Prepararse

**HU-08 · Debería.** Como trabajador, quiero saber qué aprender sin dejar de trabajar, para dar un primer paso realista.

- Dado que elegí una ocupación, cuando indico mis horas libres (poco, algo, bastante), entonces veo 1 curso de Capacítate Perú que cubre una de mis brechas y cabe en ese tiempo, con su enlace.
- Si ningún curso calza, leo "Por ahora no encontramos un curso para esto" y la brecha queda anotada.

**HU-09 · Podría.** Como trabajador, quiero ver avisos reales afines, para saber que esos trabajos existen.

- Dado que elegí una ocupación, cuando abro avisos, entonces veo hasta 3 avisos reales de Empleos Perú con empresa y enlace, aunque el nombre del puesto sea distinto al mío.

### Épica 5 — Presentarse

**HU-10 · Debería.** Como trabajador, quiero descargar un CV con lo que sé hacer, para presentarme ante un empleador.

- Dado que llegué al final, cuando toco "Descargar mi CV", entonces obtengo un PDF de una página con mi experiencia, competencias declaradas con su código y otras fortalezas confirmadas.
- El CV dice "Competencias declaradas, basadas en el Catálogo Nacional de Perfiles Ocupacionales del MTPE" y nunca "certificado".
- Puedo compartirlo por WhatsApp sin crear cuenta.

**HU-11 · Podría.** Como trabajador, quiero guardar mi perfil, para volver otro día y ver mi avance.

- Dado que llegué al final, cuando toco "Guardar mi perfil", entonces ingreso solo DNI y una clave de 4 dígitos.
- Dado que vuelvo, cuando ingreso, entonces veo mis competencias, mis ocupaciones y mi curso.
- El DNI y la clave se guardan cifrados; si no quiero, puedo terminar sin cuenta.

### Épica 6 — Ministerio

**HU-12 · Podría.** Como MTPE, quiero ver cuántas personas completan el flujo y hacia qué ocupaciones se mueven, para medir el impacto.

- Dado que hay sesiones, cuando abro el panel, entonces veo completitud, tiempo promedio y ocupaciones más recomendadas, sin datos personales.

**HU-13 · Debe.** Como MTPE, quiero que cada recomendación tenga sustento, para poder validarla.

- Dado cualquier recomendación, cuando se guarda, entonces queda registrado qué competencias del catálogo la sustentan y qué frase del usuario respalda cada una.

## Requerimientos no funcionales

Las reglas que todo el sistema cumple, sin importar la pantalla. Las metas de tiempo son objetivos de diseño y se ajustan cuando midamos el modelo real de QVAC.

| Categoría | Requerimiento | Cómo se verifica |
|---|---|---|
| Privacidad | Ningún dato del ciudadano sale de la infraestructura del MTPE: QVAC, base de datos y backend corren en el mismo entorno. Ninguna API externa de IA. | Revisión del código: sin llamadas a servicios de IA en la nube |
| Privacidad | DNI y clave se guardan con hash; el resto del perfil se asocia a un id anónimo. | Inspección de la base de datos |
| Privacidad | Las métricas del Ministerio no incluyen datos personales. | El panel solo lee tablas agregadas |
| Privacidad | Antes de empezar, una línea explica que sus datos se quedan con el Ministerio. | Visible en la pantalla de inicio |
| Rendimiento | Cada pantalla carga en menos de 2 s con 4G. | Medición en el navegador |
| Rendimiento | Cada respuesta de la IA llega en menos de 8 s; si pasa de 15 s, se ofrece reintentar. | Log de tiempos por llamada |
| Rendimiento | Página ligera: sin videos ni imágenes pesadas. | Peso de la página menor a 1 MB |
| Accesibilidad | Funciona en un celular de 360 px de ancho. | Prueba en modo móvil |
| Accesibilidad | Texto base de 16–18 px, botones de al menos 48 px, contraste alto. | Revisión visual |
| Accesibilidad | Todo se puede hacer solo con texto o solo tocando opciones, sin voz. | Prueba sin micrófono |
| Usabilidad | Una pregunta o decisión por pantalla, con progreso visible y botón Atrás. | Revisión del mockup |
| Usabilidad | Lenguaje simple: sin "competencia", "ocupación afín" ni "brecha" en la interfaz. | Revisión de textos |
| Consistencia de la IA | Temperatura baja y `seed` fijo; guion fijo de preguntas. | Dos usuarios con las mismas respuestas obtienen el mismo resultado |
| Consistencia de la IA | Toda salida estructurada pasa por tool call y se valida con esquema; un reintento si falla. | Tasa de tool calls válidas |
| Trazabilidad | Cada competencia guarda su código de catálogo y la frase del usuario que la sustenta. | Registro en `competencia_detectada` |
| Honestidad | La interfaz y el CV dicen "competencias declaradas"; nunca "certificado". | Revisión de textos |
| Integración | Encabezado, colores y ruta de gob.pe; enlaces a Capacítate Perú y Empleos Perú. | Revisión visual |
| Mantenibilidad | Repositorio con README, diagrama del pipeline, tabla de tools y decisiones con su motivo. | Revisión del repositorio |

## KPIs

**Métrica norte: personas que salen con una ruta concreta**, es decir, que terminan la sesión con al menos una ocupación afín con evidencia, un curso recomendado y su CV. Es la medida directa de "reconocer y traducir sus competencias hacia un mejor trabajo". Las metas son propuestas iniciales para validar en las pruebas con usuarios.

| Nivel | KPI | Fórmula | Meta inicial | Fuente |
|---|---|---|---|---|
| Norte | Personas con ruta concreta | Sesiones con CV generado y ≥ 1 ocupación con evidencia / sesiones iniciadas | ≥ 60% | `sesion`, `recomendacion` |
| Activación | Inicio de entrevista | Sesiones que responden la pregunta 1 / visitas a la pantalla de inicio | ≥ 80% | `sesion`, `respuesta` |
| Completitud | Llegada a resultados | Sesiones que ven sus ocupaciones afines / sesiones iniciadas | ≥ 70% | `sesion` |
| Completitud | Abandono por pantalla | Sesiones que se detienen en cada paso / sesiones que llegaron a ese paso | Ningún paso > 15% | Eventos por paso |
| Experiencia | Tiempo hasta resultados | Mediana de minutos entre inicio y ocupaciones afines | ≤ 5 min | `sesion` |
| Experiencia | Uso sin ayuda | Personas que terminan solas en pruebas / personas probadas | ≥ 80% | Pruebas con usuarios |
| Calidad de la IA | Precisión de la extracción | Competencias confirmadas / competencias propuestas | ≥ 80% | `competencia_detectada` |
| Calidad de la IA | Tool calls válidas | Tool calls que pasan el esquema al primer intento / total | ≥ 90% | Logs del backend |
| Calidad de la IA | Latencia del modelo | Tiempo promedio de respuesta de QVAC | ≤ 8 s | Logs del backend |
| Valor percibido | Utilidad declarada | Respuestas "sí" a "¿Descubriste algo que sabes hacer y no sabías?" / respuestas | ≥ 70% | Pregunta final opcional |
| Impacto (Ministerio) | Inicio de curso | Personas que abren el curso recomendado / personas con ruta | Se mide en piloto | Clics + Capacítate Perú |
| Impacto (Ministerio) | Postulación | Personas que postulan en Empleos Perú / personas con ruta | Se mide en piloto | Empleos Perú |
| Impacto (Ministerio) | Transición laboral | Personas empleadas en una ocupación afín a los 3 y 6 meses / personas con ruta | Se mide en piloto | Seguimiento del MTPE |

En la demo mostramos los niveles de experiencia y calidad de la IA con las pruebas reales; los de impacto se presentan como lo que mediría el Ministerio en un piloto.

## Flujo de pantallas

Ocho pantallas en línea recta y seis caminos alternativos; ninguno deja a la persona sin un resultado. Es la base directa del mockup: cada caja es una pantalla o un estado de una pantalla.



Para el usuario, la barra de progreso agrupa los 8 pasos en 5: Tu trabajo (1) → Cuéntanos (2) → Lo que sabes (3–4) → Trabajos para ti (5–7) → Tu CV (8).

## Modelo de datos

Diez tablas en dos grupos: los datos de referencia se cargan una vez desde las fuentes del MTPE, y los de cada sesión se crean mientras la persona usa la herramienta.



`competencia_detectada` es la tabla clave: une lo que dijo la persona (evidencia) con el código oficial del catálogo, que es el sustento que pide el MTPE.

| Tabla | Campos | Notas |
|---|---|---|
| `ocupacion` | id, codigo, nombre, tipo (gente / cosas / papeles), demanda_por_region (JSON) | Los 5 perfiles de origen y las ocupaciones destino; demanda desde la EDO 2026 |
| `competencia` | id, codigo, ocupacion_id, descripcion, descripcion_simple, embedding | Unidades de competencia del catálogo; `descripcion_simple` es la versión que ve el usuario |
| `curso` | id, nombre, horas_semana, duracion_semanas, modalidad, url, competencias_cubre | Lista curada de Capacítate Perú |
| `aviso` | id, ocupacion_id, titulo, empresa, region, url, fecha | Muestra de avisos de Empleos Perú |
| `usuario` | id, dni_hash, clave_hash, creado_en | Opcional; nunca se guarda el DNI en claro |
| `sesion` | id, usuario_id (nulo si es anónima), ocupacion_origen, interes, horas_libres, region, paso, iniciada_en, terminada_en | Fuente principal de los KPIs |
| `respuesta` | id, sesion_id, pregunta_n, texto, via (voz o texto), creada_en | Lo que respondió en cada pregunta |
| `competencia_detectada` | id, sesion_id, competencia_id, evidencia, similitud, confirmada | La evidencia es la frase textual del usuario |
| `fortaleza` | id, sesion_id, texto, evidencia, confirmada | Lo que sale de actividades fuera del trabajo |
| `recomendacion` | id, sesion_id, ocupacion_id, puntaje, cobertura, compartidas, faltantes | Resultado de `calcular_afinidad`, guardado para auditar |

Para el MVP basta SQLite con los embeddings guardados como arreglo; en producción, PostgreSQL con pgvector dentro de la infraestructura del MTPE.

## Contrato de la API

El frontend solo habla con el backend (FastAPI); el backend es el único que llama a QVAC (`/v1/chat/completions`, `/v1/embeddings`, `/v1/audio/transcriptions`) y ejecuta las tools.

**Endpoints del backend:**

| Método | Ruta | Entrada | Salida | Historia |
|---|---|---|---|---|
| POST | `/sesiones` | `ocupacion_origen` | `sesion_id`, primera pregunta | HU-01 |
| POST | `/sesiones/{id}/respuestas` | `pregunta_n`, `texto` | siguiente pregunta o repregunta, `paso` | HU-02 |
| POST | `/sesiones/{id}/audio` | archivo de audio (multipart) | `texto` transcrito | HU-03 |
| POST | `/sesiones/{id}/extraccion` | — | `competencias[]` con código y evidencia, `fortalezas[]` | HU-04, HU-13 |
| PUT | `/sesiones/{id}/confirmacion` | ids confirmados de competencias y fortalezas | estado actualizado | HU-04 |
| PUT | `/sesiones/{id}/preferencias` | `interes`, `horas_libres`, `region` | estado actualizado | HU-05, HU-08 |
| GET | `/sesiones/{id}/recomendaciones` | — | 3 ocupaciones con `puntaje`, `compartidas[]`, `faltantes[]`, `demanda` | HU-06, HU-07 |
| GET | `/sesiones/{id}/cursos?ocupacion=` | — | 1 curso recomendado o mensaje de "sin curso" | HU-08 |
| GET | `/sesiones/{id}/avisos?ocupacion=` | — | hasta 3 avisos | HU-09 |
| GET | `/sesiones/{id}/cv` | — | PDF | HU-10 |
| POST | `/usuarios` | `dni`, `clave`, `sesion_id` | token | HU-11 |
| POST | `/usuarios/login` | `dni`, `clave` | token + última sesión | HU-11 |
| GET | `/metricas` | token del MTPE | KPIs agregados | HU-12 |

**Esquema de las tools** (el LLM las ve así en el parámetro `tools`; el backend valida cada llamada):

```
[
  {"name": "guardar_relato",
   "description": "Guarda lo que la persona hace, separando su trabajo de lo que hace fuera de él. Cada ítem lleva la frase textual que lo respalda.",
   "parameters": {"tareas": [{"texto": "string", "evidencia": "string"}],
                  "fortalezas": [{"texto": "string", "evidencia": "string"}]}},
  {"name": "buscar_competencias",
   "description": "Busca en el Catálogo Nacional de Perfiles Ocupacionales las competencias que coinciden con cada tarea.",
   "parameters": {"tareas": ["string"], "umbral": "number (0-1)"}},
  {"name": "calcular_afinidad",
   "description": "Calcula qué tan cerca está la persona de cada ocupación destino y devuelve las 3 mejores.",
   "parameters": {"competencias": ["codigo"], "interes": "gente | cosas | papeles", "region": "string"}},
  {"name": "buscar_cursos",
   "description": "Devuelve el curso de Capacítate Perú que cubre una brecha y cabe en las horas libres.",
   "parameters": {"brechas": ["codigo"], "horas_semana": "number"}},
  {"name": "buscar_avisos",
   "description": "Devuelve avisos reales de Empleos Perú para una ocupación y región.",
   "parameters": {"ocupacion": "codigo", "region": "string"}},
  {"name": "generar_cv",
   "description": "Arma el CV de una página con competencias declaradas y otras fortalezas confirmadas.",
   "parameters": {"sesion_id": "string"}}
]
```

**Cómo calcula ****calcular_afinidad**** (propuesta a ajustar con pruebas):**

```
\text{puntaje} = 0.60 \cdot \text{cobertura} + 0.25 \cdot \text{interés} + 0.15 \cdot \text{demanda}
```

Cobertura = competencias de la ocupación destino que la persona ya tiene / total de competencias de esa ocupación. Interés vale 1 si la ocupación coincide con el tipo de trabajo elegido y 0 si no. Demanda va de 0 a 1 según la EDO 2026 en su región. Las ponderaciones se publican en el README, así el resultado se puede explicar y auditar.

## Pendiente tras las entrevistas

Estas tres piezas se arman con las respuestas reales de las entrevistas, para no inventar al usuario.

- [ ] **Personas (3):** una por situación del reto (sin empleo, informal por día, en planilla pero en riesgo), cada una con frases textuales, dolores, motivaciones, tiempo libre y celular que usa.
- [ ] **Journey map AS-IS:** etapas desde que aprendió su oficio hasta que intenta cambiar, con lo que hace, piensa y siente, y los puntos de dolor.
- [ ] **Propuesta de valor:** tareas, dolores y ganancias del usuario frente a lo que alivia cada funcionalidad del MVP.
- [ ] **Revisar esta pestaña con los hallazgos:** ajustar prioridades, textos de las preguntas y metas de los KPIs.
