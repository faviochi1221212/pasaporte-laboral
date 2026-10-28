# Plantilla del CV (versión de impresión)

Referencia para M6. El CV se arma en el navegador con el JSON de `GET /api/sesiones/{id}/cv?destino=CODIGO` (spec 6) y lo que la persona escribe en la pantalla. En pantalla puede verse como pasaporte; esta es la versión de impresión (`@media print`, botón que llama a `window.print()`).

## Formato

- Hoja A4, una sola página, en blanco y negro.
- Letra Times (serif) en todo el documento.
- **Nombre** centrado, en mayúsculas.
- **Línea de contacto** centrada, debajo del nombre: distrito, teléfono y correo separados por `" | "`. Solo los que la persona escribió; si no escribió ninguno, la línea no aparece.
- **Títulos de sección** en mayúsculas, con una línea horizontal debajo.
- Nunca dice "certificado" ni ninguna palabra que empiece con "certific" o "competen", salvo el título y el pie de "competencias declaradas".

## Qué escribe la persona en la pantalla (nunca se envía al servidor)

| Campo | Obligatorio |
|---|---|
| Nombre | Sí |
| Distrito | No |
| Teléfono | No |
| Correo | No |

## Secciones, en este orden

| Sección | Contenido | Viene de |
|---|---|---|
| PERFIL | Las 2 frases del resumen | `resumen` |
| EXPERIENCIA | Puesto a la izquierda y años a la derecha en la misma línea; debajo, una viñeta por sello con su texto_simple. Si `puesto` es null, la línea dice solo los años; si `anios` es null, solo el puesto | `puesto`, `anios`, `sellos[].texto_simple` |
| COMPETENCIAS DECLARADAS | Tabla de 2 columnas: etiqueta en negrita \| códigos separados por " · " | `sellos[].etiqueta`, `sellos[].codigos` |
| OTRAS FORTALEZAS | Una viñeta por fortaleza. Si no hay, la sección no aparece | `fortalezas[].texto` |
| BUSCO Y CAPACITACIÓN | El trabajo que busca y, si hay, el curso con sus horas | `destino`, `curso` |

**Pie** (al final de la página, letra pequeña):

> Competencias declaradas por la persona, basadas en el Catálogo Nacional de Perfiles Ocupacionales del MTPE.

## Ejemplo con María (relato inventado: María Quispe no existe)

Datos de ejemplo: María eligió Operaciones de Almacén como destino. Teléfono y correo son inventados.

```
                              MARÍA QUISPE
              Ate, Lima | 999 000 000 | maria.quispe@ejemplo.pe

PERFIL
───────────────────────────────────────────────────────────────────────
Cajera con 6 años de experiencia en supermercado. Abre, cobra y cuadra
la caja, y atiende los reclamos de los clientes.

EXPERIENCIA
───────────────────────────────────────────────────────────────────────
Cajero/a                                                         6 años
  • Abrir la caja: revisar el fondo de dinero y que los equipos funcionen
  • Cobrar en efectivo, con tarjeta o con Yape y entregar lo comprado
  • Cuadrar la caja al final del día
  • Atender pedidos y quejas de los clientes
  • Ordenar y guardar la mercadería en su lugar

COMPETENCIAS DECLARADAS
───────────────────────────────────────────────────────────────────────
  Abre la caja          G2347002-1.E1
  Cobra y da vuelto     G2347002-1.E2
  Cuadra la caja        G2347002-1.E3 · I2555001-2.E4
  Atiende reclamos      I2555001-2.E1
  Ordena mercadería     H2452001-1.E2

OTRAS FORTALEZAS
───────────────────────────────────────────────────────────────────────
  • Organiza los partidos de fulbito de su barrio
  • Enseña a las compañeras nuevas a usar la caja

BUSCO Y CAPACITACIÓN
───────────────────────────────────────────────────────────────────────
Busco: Operaciones de Almacén
Curso: Logística 360°. Claves para una gestión moderna y eficiente
(CAPACITA-T, 20 h)


   Competencias declaradas por la persona, basadas en el Catálogo
            Nacional de Perfiles Ocupacionales del MTPE.
```

En el ejemplo, las etiquetas de la tabla van en negrita. La línea "Curso" muestra el nombre y las horas que trae el JSON; si `curso` es null, esa línea no aparece.
