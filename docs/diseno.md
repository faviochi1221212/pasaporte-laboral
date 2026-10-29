# Guía de diseño · Pasaporte Laboral

## Para quién es
Trabajadores peruanos de 25 a 55 años (cajeras, almaceneros, limpieza) que usan el celular, leen poco en pantalla y desconfían de trámites. La app debe sentirse cálida, clara, cercana y del Perú. Nada de jerga técnica.

## Principios de UX
1. Una acción principal por pantalla (botón rojo grande, ancho completo en celular).
2. Siempre se ve en qué paso va la persona (1 Cuéntanos · 2 Tu pasaporte · 3 Tus caminos · 4 Postula).
3. Mostrar con dibujos antes que con texto: usar los componentes Sello y Trabajador.
4. Cada número tiene explicación al lado (por qué, de dónde sale).
5. Textos cortos: máximo 2 líneas por párrafo en celular.
6. Celular primero: 1 columna hasta 1023 px; 2 columnas desde 1024 px; ancho máximo 1100 px centrado.

## Estilo visual (usar las variables de estilos.css)
- Color principal: var(--rojo-peru). Hover: var(--rojo-peru-oscuro). Fondos suaves: var(--rojo-peru-claro).
- Fondo de página: var(--fondo). Tarjetas: fondo blanco, borde 1px var(--borde), radio 16px, sombra 0 2px 8px rgba(16,24,40,.06), padding 20px (24px desde 1024px).
- Títulos de pantalla: 2rem en celular, 2.75rem desde 1024px, peso 800, color var(--texto).
- Subtítulos: 1.05rem, color var(--texto-2).
- Espaciado en múltiplos de 8px (8, 16, 24, 32, 48).
- Botones: alto mínimo 48px, radio 12px, peso 700. Principal: fondo rojo, texto blanco. Secundario: fondo blanco, borde 2px rojo, texto rojo.
- Animaciones cortas (150 a 250 ms) y ninguna con prefers-reduced-motion.
- Contraste mínimo AA.

## Reglas que no se rompen
- Ningún texto visible puede tener palabras que empiecen con "certific" o "competen", ni "brecha" ni "no sirves" (excepción: "competencias declaradas" solo en el CV).
- Los textos nuevos van en web/src/textos.ts.
- No cambiar la lógica, las llamadas a la API ni los datos. Solo presentación.
- No usar escudo, logo ni el texto "gob.pe".
- No agregar librerías.
