# Spec técnica del MVP

Esta pestaña dice cómo se construye el MVP, sin espacio para inventar. Regla: lo que no está aquí no se programa; si falta algo, primero se agrega aquí. Parte de "Definición del producto" y la ajusta con lo aprendido el 27 oct (pruebas de QVAC, catálogo del MTPE, Empleos Perú y CAPACITA-T).

## 1. Decisiones que cambian la pestaña anterior

| Antes | Ahora | Por qué |
|---|---|---|
| 6 tools que llama el modelo | El modelo hace solo 3 cosas: revisar una respuesta, extraer el perfil y redactar el resumen del CV. Afinidad, cursos y avisos son funciones normales del backend. | Menos llamadas, menos errores y todo lo calculado se puede auditar |
| buscar_competencias con embeddings | El modelo elige códigos de una lista cerrada del catálogo y el código verifica | El servidor de QVAC no tiene /v1/embeddings (HTTP 501) |
| Voz con Whisper de QVAC | Dictado del navegador (Web Speech API de Chrome); al backend solo llega texto | El modelo no acepta audio (HTTP 501) |
| Demanda desde la EDO 2026 | Número de avisos de Empleos Perú en Lima para cada destino | Dato real y verificable hoy; la EDO se suma si llega a tiempo |
| Cursos de "Capacítate Perú" con semanas | Cursos de CAPACITA-T con horas oficiales | Las semanas eran inventadas |
| Login con DNI | Fuera del MVP | No suma al mínimo del MTPE |

## 2. Stack y estructura

- Python 3.10, FastAPI, SQLite con el módulo sqlite3 (sin ORM), httpx para llamar a QVAC y pytest para las pruebas. Sin otras dependencias.
- Frontend: React + TypeScript con Vite, CSS propio "primero celular" (una columna en 360 px, dos columnas desde 1024 px) con los colores del mockup v3. Cada pantalla del mockup es una ruta y Sello, Trabajador y Pasaporte son componentes reutilizables. El build lo sirve el mismo FastAPI. Pruebas de pantalla con Playwright en 360 y 1280 px. Orden de construcción: primero todo el backend probado por su API (M0 a M5) y después las pantallas (M6).
- Un solo proceso y un solo repositorio:

```
app/
  main.py          rutas HTTP
  qvac.py          cliente de QVAC + modo respaldo
  ia.py            las 3 tareas del modelo (prompts y esquemas)
  calculo.py       afinidad, cursos, avisos (sin IA)
  db.py            SQLite
  config.py        constantes: pesos, horas por semana, máximos y textos fijos
  datos.py         carga data/*.json una vez al iniciar
data/              catálogo, cursos, avisos (JSON, se cargan al iniciar)
fixtures/          respuestas grabadas de QVAC para el modo respaldo
web/               pantallas (React + TypeScript)
scripts/           validar datos, verificar textos de PDF, probar QVAC
docs/              spec, historias, checklist, fuentes y mockup
tests/             pruebas
.env               QVAC_TOKEN, QVAC_BASE_URL, QVAC_MODEL, QVAC_MODO y QVAC_GRABAR (solo pruebas: graba fixtures) (no se sube)
```

## 3. Datos de referencia

Todo dato que ve el usuario viene de estos archivos. Cada registro guarda su fuente y la fecha en que se tomó.

**ocupaciones.json** · perfiles del Catálogo Nacional de Perfiles Ocupacionales (CNPO), cada uno con su tipo de trabajo (gente, cosas o papeles) para el interés:

| Perfil del CNPO | Código | Puesto que se usa | Origen | Tipo | Sellos | Vence |
|---|---|---|---|---|---|---|
| Caja en Establecimientos Comerciales | G2347002 | Cajero/a | Sí, recorrido completo | gente | 3 | 2029 |
| Operaciones de Almacén | H2452001 | Almacenero/Operario de almacén | Sí | cosas | 3 | 2027 |
| Servicios de Limpieza | M2981001 | Operario/a de limpieza | Sí | cosas | 3 | 2030 |
| Recepción de Hotel/Hostal | I2555001 | Recepcionista | No | gente | 7 | 2027 |
| Operaciones de Housekeeping | I2555002 | Operario/a de housekeeping | No | cosas | 6 | 2028 |
| Atención en Salón de Comidas y Bebidas/Eventos | I2556002 | Ayudante de mozo y mozo/a | No | gente | 4 | 2029 |

Los 6 pueden ser destino, menos el de origen de la persona; la ruta muestra los 3 con mayor puntaje. Solo se usan perfiles vigentes: Atención al Usuario por Teléfono (M2982001) se descartó porque venció el 30/08/2026. El tipo es una propuesta del equipo. Cada perfil guarda además "qué harías ahí": 3 tareas en palabras simples, escritas a partir de sus elementos de competencia, que se muestran en la tarjeta del destino.

En el CNPO no hay perfil de vendedor ni de auxiliar administrativo. Sin un documento oficial para ellos no se cargan; esas tarjetas del inicio llevan a la entrevista igual que "Otro". Si el MTPE entrega el mapa funcional de auxiliares administrativos que menciona su PPT, se agrega como origen y destino.

Cambio en el mockup: los destinos de la ruta salen del cálculo entre estos 6 perfiles (para la cajera se espera Recepción de hotel, Mozo/a y Almacén). "Asistente administrativo" sale de la ruta mientras no haya documento oficial, y los "sellos que faltan" pasan a ser elementos del perfil destino, no cursos sueltos como Excel.

**competencias.json** · una fila por elemento de competencia de los estándares de puestos operativos (se excluyen los de supervisor, jefe o administrador): 26 elementos en total. Campos: codigo (código oficial del estándar + número del elemento según el orden del PDF, por ejemplo G2347002-1.E3), perfil, texto_oficial (copia literal del PDF), criterios_clave (fragmentos literales de los criterios de desempeño, para que el modelo reconozca la tarea), texto_simple y sello (ícono y etiqueta de 2 a 3 palabras). texto_simple y sello los escribe el equipo y los revisa una persona. Un script comprueba que texto_oficial y criterios_clave aparezcan tal cual en el PDF; Recepción de Hotel es un PDF escaneado y se transcribió a mano.

**cursos.json** · cursos de CAPACITA-T revisados el 27 oct 2026: nombre, horas, certificador, url y los códigos de competencia que cubre (lo decide el equipo). Lista final en la sección 6b: Logística 360° (20 h) y Orientación al cliente – Fidelización (4 h).

**avisos.json** · avisos de Empleos Perú de Lima del 27 oct 2026: id, titulo, empresa, distrito, sueldo, cierre, url, el perfil destino al que se asocian (lo decide el equipo) y que_piden: 1 o 2 funciones copiadas de la descripción del propio aviso.

**demanda** · por perfil destino, número de avisos en Lima en avisos.json; puntaje = avisos del destino / avisos del destino con más avisos.

## 4. Regla del sello

Un sello es un elemento de competencia de competencias.json, es decir, una tarea concreta de un puesto operativo (por ejemplo, "Ejecutar el arqueo y cuadre de caja" → sello "Cuadre de caja"). Una persona puede ganar sellos de cualquiera de los 6 perfiles, no solo del suyo: así se ve qué de lo que ya hace sirve en otro trabajo. Se otorga solo si se cumplen las tres condiciones:

1. El modelo la propone con un código que existe en competencias.json.
2. La evidencia es una frase que aparece tal cual en lo que escribió la persona (comparando sin mayúsculas, tildes, signos ni espacios dobles).
3. La persona no la quitó en la pantalla del pasaporte.

Si falla 1 o 2, la propuesta se descarta en silencio y queda en el log. Una unidad da un solo sello, aunque tenga varias evidencias. Lo que viene de fuera del trabajo (preguntas 4 y 5) va a "otras fortalezas": se muestra y va al CV, pero no da sellos ni cuenta para la afinidad.

## 5. Lo que hace el modelo

Siempre con el modo pensar apagado (chat_template_kwargs.enable_thinking = false), temperatura 0, salida por tool call validada contra el esquema y un solo reintento. Si el reintento falla, se usa la regla de respaldo indicada.

| Tarea | Cuándo | Entrada | Salida (tool) | Respaldo |
|---|---|---|---|---|
| revisar_respuesta | Después de cada respuesta a las preguntas 1 a 5 | pregunta y respuesta | reaccion (máx. 12 palabras, sobre lo que dijo la persona), suficiente (sí/no), menciona_actividad (sí/no), repregunta (máx. 15 palabras) | Reacción fija "Gracias por contarme."; repregunta fija "¿Me das un ejemplo de algo que hiciste esta semana?" en las preguntas 2 a 5 si la respuesta tiene menos de 6 palabras |
| extraer_perfil (parcial) | En segundo plano, después de cerrar las preguntas 2 y 3 | respuestas de las preguntas 1 a 3 + lista cerrada | igual que la completa | Si falla, el contador no cambia y la conversación sigue |
| extraer_perfil (completa) | Al terminar la pregunta 6 | todas las respuestas + lista cerrada de competencias (código, texto_simple y criterios_clave) | competencias: código y evidencia; fortalezas: texto y evidencia | Pantalla "No pudimos leer tu relato, inténtalo de nuevo" |
| redactar_resumen | Al pedir el CV | sellos confirmados y años de experiencia | 2 frases de perfil para el CV | Plantilla fija con los sellos |

Reglas de la conversación, en código y no en el modelo:

- Las 6 preguntas son fijas, en el orden de la pantalla "Guion".
- Máximo una repregunta por pregunta.
- En las preguntas 4 y 5 la repregunta es siempre "¿Y qué haces tú ahí?", si revisar_respuesta dice que mencionó una actividad.
- La reacción se valida en código: máximo 12 palabras y sin las palabras prohibidas ("certificado", "competente", "competencia", "brecha", "no sirves"). Si no pasa, se usa la reacción fija. A la pregunta 6 se responde siempre con el texto fijo de cierre.
- Los sellos parciales solo sirven para el contador del chat; el pasaporte usa siempre la extracción completa.

### 5b. Experiencia de conversación

Para que se sienta como hablar con alguien (pedido en la mentoría con Tether, 26 oct) sin engañar a nadie:

- **Formato chat:** burbujas del asistente a la izquierda y de la persona a la derecha; el historial queda visible arriba y siempre hay una sola pregunta abierta. Los ejemplos tocables y el campo de texto van debajo de la última pregunta.
- **Ritmo:** antes de cada burbuja del asistente se ve "escribiendo…" unos 700 ms y el texto aparece de a poco (máximo 1,5 s por burbuja). Tocar la burbuja la muestra completa. Con `prefers-reduced-motion` todo aparece de inmediato.
- **Saludo fijo, igual para todos:** "¡Hola! 👋 Soy el asistente de empleo del Ministerio de Trabajo. Te haré 6 preguntas cortas sobre lo que haces. No hay respuestas buenas ni malas." Luego va la pregunta 1.
- **Reacción:** después de cada respuesta, la burbuja de reacción del modelo (por ejemplo "¡6 años es harta experiencia!") y luego la siguiente pregunta o la repregunta.
- **Cierre fijo:** "¡Gracias! Con lo que me contaste estoy armando tu pasaporte…" y se pasa a la pantalla de espera.
- **Sellos mientras conversa:** una barra fija abajo dice "N sellos ganados · Sigue contándonos", alimentada por la extracción parcial. Nunca bloquea el chat.
- **Honestidad:** el asistente se presenta como asistente y no tiene nombre de persona ni foto. No finge ser humano.

Prompt de sistema de extraer_perfil, al que se le pega la lista de competencias:

> Eres un asistente del Ministerio de Trabajo del Perú. Lee lo que contó la persona y llama a extraer_perfil. Usa solo códigos de la lista. Para cada competencia, copia como evidencia la frase exacta que la persona escribió; si no hay frase exacta, no la incluyas. Lo que hace fuera de su trabajo va en fortalezas, nunca en competencias. No inventes nada.

## 6. Endpoints

| Método y ruta | Entrada | Salida |
|---|---|---|
| POST /api/sesiones | {ocupacion_origen} | {sesion_id, saludo, pregunta: {n, texto, ejemplos[]}} |
| POST /api/sesiones/{id}/respuestas | {n, texto} | {tipo: "repregunta" o "siguiente" o "fin", reaccion, pregunta (null si es fin), cierre (solo si es fin), parcial_listo: sí/no} |
| POST /api/sesiones/{id}/sellos-parciales | — | {sellos_ganados: n, etiquetas: [texto]} (extracción parcial con las respuestas 1 a 3; la pantalla la llama sin esperar cuando parcial_listo es sí) |
| POST /api/sesiones/{id}/pasaporte | — | {sellos: [{codigo, etiqueta, icono, evidencia}], fortalezas: [{texto, evidencia}]} |
| PUT /api/sesiones/{id}/pasaporte | {quitar: [codigos], quitar_fortalezas: [i]} | igual que arriba |
| PUT /api/sesiones/{id}/preferencias | {interes: gente o cosas o papeles, horas: 1-2 o 3-5 o 5+} | {ok} |
| GET /api/sesiones/{id}/ruta | — | {destinos: [{codigo, nombre, puntaje, tienes: [codigo], que_harias: [3 textos], faltan: [{codigo, etiqueta, curso o null}], avisos_lima}]} (3, de mayor a menor puntaje) |
| GET /api/sesiones/{id}/avisos?destino= | — | hasta 3 avisos de avisos.json, cada uno con su que_piden |
| GET /api/sesiones/{id}/cv | — | Página HTML lista para imprimir o guardar como PDF |

Afinidad (en calculo.py, con pruebas): puntaje = 0,60 × cobertura + 0,25 × interés + 0,15 × demanda, donde cobertura = sellos de la persona que son elementos del destino / elementos del destino, e interés = 1 si el tipo del destino coincide con el elegido y 0 si no. El perfil de origen nunca aparece como destino. Los "sellos que faltan" de un destino son sus elementos que la persona no tiene.

De dónde sale cada preferencia: las horas libres, de la pregunta 6; el interés, de una pantalla de 3 botones (con gente, con cosas y orden, con papeles y números) que se agrega al mockup v3 entre el pasaporte y la ruta, tomada de la pantalla Intereses del v2.

Cómo se explica cada destino (el corazón del reto: que la persona diga "ahora entiendo"). La tarjeta muestra, en este orden y sin texto libre del modelo:

1. "Lo que ya haces y aquí también sirve": cada sello compartido con la frase de la persona que lo respalda.
2. "Qué harías ahí": las 3 tareas del perfil destino.
3. "Lo que te falta": los elementos del destino que no tiene, cada uno con su curso de CAPACITA-T o "Todavía sin curso gratis del MTPE".
4. "Avisos hoy en Lima": el número de avisos y el acceso a los 3 más cercanos.

## 6b. Los 5 casos que ve el jurado, definidos

**1. Qué produce cada sello.** Un sello = un código de competencias.json que pasó las 3 condiciones de la sección 4, con su etiqueta, ícono y la frase de la persona. Puede venir de cualquiera de los 6 perfiles. Si dos sellos tienen la misma etiqueta (por ejemplo "Organiza la limpieza" en Limpieza y en Housekeeping), el pasaporte muestra uno solo con la nota "sirve en 2 trabajos"; por dentro se guardan los dos códigos.

**2. Cómo se ordenan los 3 trabajos.** Se calcula el puntaje de la sección 6 para los 5 perfiles distintos del origen. Se descartan los que tienen 0 sellos compartidos, porque no se pueden explicar. Se ordena por puntaje; si empatan, gana la mayor cobertura y luego la mayor demanda. Se muestran hasta 3; si quedan menos, se muestran los que haya y la frase "Cuéntanos un poco más para encontrar otros caminos", que vuelve a la entrevista.

**3. De dónde sale la demanda.** De una foto de Empleos Perú (departamento de Lima) guardada en data/demanda.json con su fecha y hora, contando avisos cuyo título coincide con las palabras clave de cada perfil. Foto del 27 oct 2026, 600 avisos en Lima:

| Perfil | Palabras clave en el título | Avisos | Demanda (0 a 1) |
|---|---|---|---|
| Operaciones de Almacén | almacén, reponedor, despacho | 83 | 1,00 |
| Servicios de Limpieza | limpieza | 42 | 0,51 |
| Caja | cajero/a | 8 | 0,10 |
| Atención en Salón | mozo, mesero/a, azafata, salón | 8 | 0,10 |
| Recepción de Hotel | recepción, recepcionista | 3 | 0,04 |
| Housekeeping | housekeeping, camarera, habitación | 0 en Lima | 0,00 |

Demanda = avisos del perfil / avisos del perfil con más avisos. La foto se toma una vez antes de la demo y no cambia durante ella; la tarjeta dice "83 avisos en Lima al 27 oct". Los avisos de recepcionista no son todos de hotel; la tarjeta dice "avisos parecidos".

**4. Cómo se calcula "lo que te falta".** Faltan = elementos del perfil destino cuyo código no está entre los sellos confirmados de la persona. Si no falta ninguno, la tarjeta dice "Ya haces todo lo que pide este trabajo".

**5. Qué pasa si no hay curso.** Cada faltante busca en cursos.json un curso que lo cubra; si hay varios, el de menos horas. Con las horas libres de la pregunta 6 (1-2 h → 1,5 h; 3-5 h → 4 h; más de 5 h → 6 h por semana) se muestra "unas N semanas con tu tiempo" (horas del curso / horas por semana, redondeado hacia arriba). Si no hay curso, dice "Todavía sin curso gratis del MTPE" y ese faltante se cuenta en el log, para el dato de "cursos que faltan" del pitch. Si un destino no tiene avisos, dice "Hoy no hay avisos en Lima para esto".

Qué curso cubre qué, revisado contra el temario publicado de cada curso el 27 oct. Solo se enlaza un curso a una tarea si un módulo del temario la enseña; si no, la tarea queda sin curso:

| Lo que falta (sello) | Curso de CAPACITA-T | Qué parte cubre (módulo del temario) | Horas | Qué se lleva la persona |
|---|---|---|---|---|
| Ordena mercadería (H2452001-1.E2) | Logística 360°. Claves para una gestión moderna y eficiente | Solo la teoría: "Gestión de inventarios y almacenamiento" (tipos de inventario, diseño básico de almacenes y flujos) | 20 | Entender cómo se organiza un almacén; no reemplaza la práctica |
| Despacha pedidos (H2452001-1.E3) | Logística 360° | Solo la teoría: "Transporte y distribución" | 20 | Entender el camino de un pedido hasta el cliente |
| Atiende reclamos (I2555001-2.E1) | Orientación al cliente – Fidelización | "Administrar las crisis con los clientes" (quejas y reclamos) | 4 | Saber recibir y resolver un reclamo |
| Trata bien al cliente (I2555002-3.E1) | Orientación al cliente – Fidelización | "Comunicación" (empatía y asertividad) y "Fidelización" | 4 | Atender con empatía según el tipo de cliente |

La tarjeta muestra el curso con su alcance tal cual: "Te ayuda con la parte teórica de…" cuando solo cubre teoría. Logística 360° está pensado para gestión logística, así que se presenta como complemento, no como "el curso para ser almacenero".

Las otras 22 tareas no tienen curso en CAPACITA-T: dicen "No encontramos un curso gratuito del MTPE que cubra esto". Se descartaron Excel básico, Word básico y Prevención de riesgos laborales porque no enseñan ninguna tarea de estos 6 perfiles. En el pitch esto se presenta como "en nuestra revisión inicial encontramos…", no como una conclusión definitiva sobre la oferta del MTPE.

Etiquetas de los sellos (revisadas: acción que se puede ver, sin palabras del catálogo, comprensibles sin conocer el perfil). Cuando dos elementos de perfiles distintos describen la misma acción, comparten etiqueta y el pasaporte los junta con "sirve en 2 trabajos":

| Etiqueta | Elementos |
|---|---|
| Abre la caja · Cobra y da vuelto | G2347002-1.E1 · E2 |
| Cuadra la caja | G2347002-1.E3 y I2555001-2.E4 (sirve en 2 trabajos) |
| Recibe mercadería · Ordena mercadería · Despacha pedidos | H2452001-1.E1 · E2 · E3 |
| Organiza la limpieza | M2981001-1.E1 y I2555002-1.E1 (sirve en 2 trabajos) |
| Limpia áreas | M2981001-1.E2 y I2555002-1.E2 (sirve en 2 trabajos) |
| Revisa y reporta daños | M2981001-1.E3 |
| Recibe huéspedes · Entrega encargos · Da información | I2555001-1.E1 · E2 · E3 |
| Atiende reclamos · Registra llegadas · Cierra cuentas | I2555001-2.E1 · E2 · E3 |
| Planifica habitaciones · Deja lista la habitación | I2555002-2.E1 · E2 |
| Trata bien al cliente · Atiende pedidos del cliente | I2555002-3.E1 · E2 |
| Prepara platos y cubiertos · Arma mesas | I2556002-1.E1 · E2 |
| Toma pedidos · Sirve y cobra | I2556002-2.E1 · E2 |

## 7. Real y simulado en la demo

| Real | Simulado o fijo |
|---|---|
| El modelo Qwen de QVAC conversando y extrayendo | Los avisos y cursos son una foto del 27 oct, no se consultan en vivo |
| Los códigos y textos del catálogo del MTPE | María Quispe y su relato son inventados; nunca se usan datos reales porque Tether ve los prompts |
| Los cálculos de afinidad | Si QVAC no responde, QVAC_MODO=respaldo usa respuestas grabadas de una corrida real y la pantalla lo indica con una marca pequeña |

## 8. Fuera del MVP

- Login, DNI y cuentas.
- Voz con QVAC y voz de salida.
- Panel del Ministerio.
- Postular de verdad: el botón abre el aviso en Empleos Perú.
- Consultas en vivo a Empleos Perú o CAPACITA-T.
- Vendedor y auxiliar administrativo con datos propios.
- Cualquier pantalla que no esté en el mockup v3, salvo la de intereses.

## 9. Criterios de aceptación

El MVP está listo cuando pasa todo esto, no cuando "parece funcionar".

| # | Prueba | Se cumple si |
|---|---|---|
| A1 | Relato de cajera (María) | Recibe sellos de al menos la mitad de los de G2347002, el fulbito queda en fortalezas y toda evidencia es textual |
| A2 | Relato de almacén | Recibe sellos de al menos la mitad de los de H2452001 y ninguno sin evidencia |
| A3 | Relato de limpieza | Recibe sellos de al menos la mitad de los de M2981001 |
| A4 | Respuesta vaga ("de todo un poco") | Hay una repregunta y nunca una segunda |
| A5 | Evidencia inventada (prueba con salida falsa) | El sello se descarta |
| A6 | Afinidad | Con datos fijos de prueba, el orden y los puntajes coinciden con el cálculo a mano |
| A7 | Destino sin curso | Muestra "Todavía sin curso gratis del MTPE" |
| A8 | QVAC apagado | Con QVAC_MODO=respaldo el recorrido completo funciona |
| A9 | Tiempos | Cada respuesta del modelo en menos de 8 s (hoy mide 2 a 4 s) |
| A10 | Celular | Todo el recorrido se hace en 360 px de ancho y solo tocando |
| A11 | Computadora | Todo el recorrido funciona en 1280 px con el diseño de 2 columnas del mockup de escritorio; Playwright guarda capturas de cada pantalla en 360 y 1280 px |
| A12 | Reacción del asistente | Con una salida falsa de más de 12 palabras o con una palabra prohibida, se usa la reacción fija; con QVAC real, las reacciones de los relatos A1 a A3 cumplen el límite |
| A13 | Sellos parciales | Si la extracción parcial falla o tarda, el chat sigue sin esperar y el pasaporte final no depende de ella |

Las pruebas A1 a A3 se corren contra QVAC real y sus respuestas se guardan en fixtures/ (de ahí sale el modo respaldo). A5 a A8 son automáticas y no llaman a QVAC.

## 9b. Límites, equidad y datos

La herramienta no debe:

- Certificar ni validar competencias. La interfaz y el CV dicen "lo que contaste que haces" y "competencias declaradas", nunca "eres competente" ni "certificado".
- Prometer empleo ni decir que alguien "no sirve" para un trabajo. Lo que falta se presenta como siguiente paso.
- Decidir por la persona: siempre ve los 3 destinos y elige.
- Inventar competencias, cursos ni avisos: todo sale de los archivos de data/ y se puede rastrear a su fuente.
- Mostrar una recomendación sin su explicación.

Equidad: la app no pregunta edad, género, discapacidad, nivel educativo ni lugar de nacimiento, y la afinidad solo usa sellos, interés y demanda. Así esos datos no pueden influir en la recomendación. El único dato de lugar es el distrito, y solo para ordenar avisos.

Datos en el MVP:

| Qué | ¿Se guarda? | Cuánto tiempo |
|---|---|---|
| Respuestas escritas | Sí, en SQLite, ligadas a un id anónimo | Hasta borrar la sesión; en la demo se borra todo al final |
| Voz | No: el dictado ocurre en el navegador y solo llega texto | — |
| Nombre para el CV | Solo en el navegador de la persona, no en el servidor | — |
| DNI, teléfono, correo | No se piden | — |

Nada se usa para entrenar modelos. En la demo solo hay relatos inventados, porque los prompts del servidor de Tether no son privados; en producción QVAC correría dentro de la infraestructura del MTPE.

Flujo mínimo para el jurado (30 segundos): relato → sellos con su frase → 3 trabajos posibles → por qué. Cursos, avisos y CV vienen después y son el plus.

## 10. Orden de construcción

1. data/: catálogo copiado de los PDF y revisado a mano, cursos y avisos. Hecho el 27 oct: ocupaciones.json y competencias.json armados desde los 6 PDF; falta que una persona revise texto_simple, sello y qué harías.
2. calculo.py y sus pruebas (A6, A7).
3. qvac.py e ia.py con las pruebas A1 a A5; se graban los fixtures.
4. Endpoints.
5. Pantallas.
6. README con el pipeline, las 3 tareas del modelo, la fórmula y estas decisiones.
