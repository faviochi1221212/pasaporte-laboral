# Mockup v3 · referencia visual

Mockup completo e interactivo: https://claude.ai/artifact/L82ipFspaTfnKapcaVwxok (página "Versión 3 · Pasaporte y ruta").

Los archivos `.dc.html` de esta carpeta son las pantallas del mockup. Úsalos para copiar estructura, estilos y los SVG de `Sello` y `Trabajador`. **No copies sus textos ni números:** algunos están desactualizados (por ejemplo "Asistente administrativo" en la ruta o cursos de Excel). Los datos reales salen siempre de `data/`.

| Archivo | Pantalla de la app |
|---|---|
| V3Inicio, V3EscritorioInicio | Inicio (celular y computadora) |
| V3Conversacion, V3Guion | Conversación y guion de las 6 preguntas |
| V3Pasaporte, V3EscritorioPasaporte | Pasaporte |
| V3Ruta, V3Escritorio | Ruta (celular y computadora) |
| V3Estacion | Detalle de un destino |
| V3Avisos | Avisos |
| V3CV | CV |
| Sello, Trabajador | Componentes reutilizables (SVG) |

Falta en el mockup y se agrega en la app: pantalla de Intereses (3 botones) y pantalla de Espera ("Armando tu pasaporte…").

## Colores (variables CSS)

```css
:root {
  --rojo-gob: #C8102E;      /* logo gob.pe, acentos */
  --rojo-peru: #D91023;     /* color principal (solo en la app): botones principales, títulos destacados, barra de sellos y bloque superior del Inicio; blanco encima 5,2:1, sobre --fondo 4,7:1 (AA) */
  --rojo-peru-oscuro: #A50D1B; /* hover de los botones; blanco encima 7,9:1 */
  --rojo-peru-claro: #FDF0F1;  /* fondo de chips y hover de botones secundarios; rojo encima 4,6:1 */
  --azul: #1C5FA8;          /* solo enlaces (en la app los botones van en --rojo-peru) */
  --azul-oscuro: #123F73;   /* hover */
  --fondo: #F2F5F9;
  --blanco: #FFFFFF;
  --texto: #1F2430;
  --texto-2: #3A4352;
  --texto-3: #5F6B7A;
  --borde: #E3E8EF;
  --borde-2: #DCE3EC;
  --borde-input: #A9B3C1;
  --verde: #1E7A46;         /* ruta almacén, "ya tienes" */
  --verde-oscuro: #155C34;
  --verde-claro: #EAF6EF;
  --morado: #5B3E96;
  --ambar: #B45309;         /* "te falta" */
  --cian: #0E7490;
  --granate: #7A1F2B;       /* cabecera del pasaporte */
  --papel: #FBF8F1;         /* hoja del pasaporte */
  --dorado: #F3E3B8;        /* texto sobre granate */
  --aviso-fondo: #FFF4E5;   /* marca "modo sin conexión" */
  --aviso-texto: #7A4300;
}
```

Tipografía: Roboto (400, 500, 700, 900). Texto base 16 a 18 px. Botones de al menos 48 px de alto. **Cambio en la app:** no hay banda superior; un pie pequeño en todas las pantallas dice "Prototipo para la Innovathon ULima x Tether 2026 · No es un servicio oficial del MTPE", y arriba solo aparece la marca "modo sin conexión" en modo respaldo. Sin logos, escudo ni la palabra "gob.pe", y sin copiar la cabecera de gob.pe ni de Empleos Perú.
