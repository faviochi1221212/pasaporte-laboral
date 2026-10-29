# Kallpa

**Tu experiencia ya es un oficio.** Aplicación del MTPE con IA local sobre QVAC para reconocer lo que una persona sabe hacer y conectarla con oficios con demanda sin dejar de ganar.

## Estructura de carpetas

- `data/`: Datos de referencia (catálogos, cursos, avisos).
- `countries/pe/`: Configuración y datos específicos de Perú.
- `packages/core/`: Lógica de negocio y tipos compartidos.
- `server/`: Backend Express.
- `connectors/`: Conectores a fuentes externas.
- `apps/web/`: Frontend React.
- `tests/`: Pruebas de código.

## Comandos

```bash
# Instalar dependencias
npm install

# Correr el frontend en modo desarrollo
npm run dev

# Correr el servidor backend
npm run server

# Ejecutar pruebas
npm run test

# Validar datos
npm run validar-datos
```
