# Historias de usuario del MVP (versión 27 oct 2026)

Reemplazan las de `docs/historico/definicion-producto.md`. Cada historia dice en qué módulo se construye y con qué prueba se comprueba. **Una tarea de código que no responda a una historia no se hace.** Una historia está terminada solo si cumple todos sus criterios.

Estados: **Debe** (sin esto no hay demo) · **Debería** (se hace después de todos los Debe) · **Fuera** (no se programa).

| HU | Estado | Como trabajador quiero… | Criterios de aceptación | Módulos | Prueba |
|---|---|---|---|---|---|
| HU-01 | Debe | Elegir mi trabajo con un toque | 1) Inicio con 6 tarjetas (Caja, Ventas, Limpieza, Almacén, Oficina, De todo) y el campo "¿No está tu trabajo?". 2) Al tocar se crea la sesión sin pedir datos personales. 3) Caja, Almacén y Limpieza fijan su perfil de origen; Ventas, Oficina, De todo y Otro no tienen perfil oficial: origen nulo y los 6 perfiles cuentan como destino. | M5, M6 | e2e-01 |
| HU-02 | Debe | Contar lo que hago respondiendo preguntas sencillas | 1) 6 preguntas fijas (pantalla Guion), una por pantalla, con 2 o 3 ejemplos tocables y campo de texto. 2) Barra de progreso y botón Atrás. 3) Máximo una repregunta por pregunta. 4) En las preguntas 4 y 5 la repregunta es "¿Y qué haces tú ahí?". | M4, M5, M6 | A4, e2e-02 |
| HU-03 | Debería | Responder hablando | 1) El micrófono usa el dictado del navegador; la voz no sale del dispositivo. 2) El texto se puede corregir antes de enviar. 3) Si el navegador no tiene dictado, el botón no aparece. | M6 | e2e-03 |
| HU-04 | Debe | Ver en un pasaporte lo que sé hacer | 1) Mientras procesa: "Armando tu pasaporte…". 2) Cada sello muestra su etiqueta y, al tocarlo, mi frase. 3) Puedo quitar un sello y no se usa después. 4) Sellos con la misma etiqueta se juntan con "sirve en 2 trabajos". 5) Otras fortalezas aparte, sin sello. 6) Nunca dice "certificado". | M2, M4, M5, M6 | A1, A2, A3, A5 |
| HU-05 | Debe | Decir qué tipo de trabajo me gusta | 1) 3 botones: con gente, con cosas y orden, con papeles y números. 2) La elección cambia el orden de los trabajos según la fórmula. | M2, M5, M6 | A6 |
| HU-06 | Debe | Ver trabajos parecidos al mío | 1) Hasta 3 destinos ordenados por puntaje, con desempate por cobertura y demanda. 2) Cada uno dice cuántos de mis sellos sirven ahí y cuántos avisos hay en Lima, con la fecha de la foto. 3) Ningún destino con 0 sellos en común. 4) Si hay menos de 3: "Cuéntanos un poco más para encontrar otros caminos". 5) Ningún número viene del modelo. | M2, M5, M6 | A6, e2e-04 |
| HU-07 | Debe | Entender por qué encajo | 1) El detalle muestra en orden: lo que ya hago y aquí sirve (con mi frase), qué haría ahí, lo que me falta, avisos. 2) Lo que falta se presenta como siguiente paso. 3) Si no falta nada: "Ya haces todo lo que pide este trabajo". | M2, M6 | e2e-05 |
| HU-08 | Debería | Saber qué aprender sin dejar de trabajar | 1) Cada cosa que falta muestra su curso de CAPACITA-T con lo que cubre, horas y "unas N semanas con tu tiempo". 2) Si el curso solo cubre teoría: "Te ayuda con la parte teórica de…". 3) Sin curso: "No encontramos un curso gratuito del MTPE que cubra esto". | M2, M6 | A7 |
| HU-09 | Debería | Ver avisos reales para postular | 1) Hasta 3 avisos de Empleos Perú con empresa, distrito, sueldo si lo publica, cierre y "qué piden". 2) El botón abre el aviso real. 3) Sin avisos: "Hoy no hay avisos en Lima para esto". 4) Si el aviso es parecido y no exacto, lo dice. | M1, M2, M6 | e2e-06 |
| HU-10 | Debería | Llevarme un CV con lo que sé hacer | 1) Página lista para imprimir o guardar como PDF. 2) Mi nombre lo escribo en el navegador y no se envía al servidor. 3) Dice "Competencias declaradas, basadas en el Catálogo Nacional de Perfiles Ocupacionales del MTPE" con sus códigos. 4) Incluye otras fortalezas confirmadas. | M4, M5, M6 | e2e-07 |
| HU-11 | Fuera | Guardar mi perfil con DNI | — | — | — |
| HU-12 | Fuera | Panel de métricas del MTPE | Se reemplaza por el log de "tareas sin curso" que alimenta la lámina de hallazgos del pitch. | M2 | — |
| HU-13 | Debe | (MTPE) Que cada recomendación tenga sustento | 1) Cada sello guarda su código y la frase textual. 2) Cada recomendación guarda cobertura, interés, demanda y puntaje. | M2, M5 | A5, A6 |
| HU-14 | Debe | Usarla bien en celular y en computadora | 1) En 360 px todo cabe en una columna, sin scroll horizontal, botones de al menos 48 px. 2) En 1280 px usa 2 columnas como el mockup de escritorio y el texto tiene ancho máximo. 3) Mismas funciones en los dos. | M6 | A10, A11 |
| HU-15 | Debe | (Equipo) Que la demo no se caiga | 1) Con `QVAC_MODO=respaldo` el recorrido completo funciona sin internet. 2) Se ve una marca pequeña "modo sin conexión". | M3, M5, M6 | A8 |

## Pruebas citadas

- **A1 a A11:** criterios de aceptación de `docs/spec.md` sección 9.
- **e2e-01 a e2e-07:** recorridos de Playwright en `tests/e2e/`, cada uno en 360 y 1280 px, que guardan una captura por pantalla en `tests/e2e/capturas/`:
  - e2e-01: inicio → elegir Caja → primera pregunta.
  - e2e-02: responder las 6 preguntas con una repregunta.
  - e2e-03: sin dictado disponible, el botón de micrófono no aparece.
  - e2e-04: pasaporte → intereses → ruta con 3 destinos.
  - e2e-05: detalle de un destino con los 4 bloques en orden.
  - e2e-06: avisos de un destino con y sin avisos.
  - e2e-07: CV con nombre escrito en el navegador y sin "certificado".
