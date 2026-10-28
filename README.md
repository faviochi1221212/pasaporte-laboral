# Pasaporte Laboral

**Sabes más de lo que crees.** Una persona que aprendió su oficio trabajando cuenta en 6 preguntas lo que hace. La app le muestra un pasaporte con sellos (tareas reales del Catálogo Nacional de Perfiles Ocupacionales del MTPE), 3 trabajos a los que puede moverse con la explicación de por qué encaja, lo que le falta, cursos gratuitos del MTPE, avisos reales de Empleos Perú y un CV.

Prototipo para la Innovathon ULima x Tether 2026 · Reto del Ministerio de Trabajo y Promoción del Empleo. **No es un sitio oficial.**

> Estado: base de datos y documentación listas. El código se construye por módulos (M0 a M8), ver `docs/checklist.md`.

## Cómo funciona

```
Persona ──6 preguntas──▶ Backend (FastAPI) ──tool calls──▶ QVAC (Qwen 3.8 27B, Tether)
                              │
                              ├─ regla del sello: código del catálogo + frase textual de la persona
                              ├─ afinidad = 0,60 cobertura + 0,25 interés + 0,15 demanda
                              └─ cursos, avisos y demanda desde data/ (fuentes oficiales)
```

**El modelo conversa, extrae y redacta; el código calcula.** Ningún número, ocupación, curso ni aviso que ve la persona sale del modelo.

| El modelo hace | El código hace |
|---|---|
| Revisar si una respuesta es vaga y repreguntar | Guion fijo de 6 preguntas |
| Proponer qué tareas del catálogo aparecen en el relato, con la frase exacta | Verificar código y frase; descartar lo inventado |
| Redactar 2 frases del CV | Afinidad, ranking, faltantes, cursos, avisos, demanda |

## Fuentes de datos (`data/`)

| Archivo | Fuente | Fecha |
|---|---|---|
| `ocupaciones.json`, `competencias.json` | 6 perfiles del Catálogo Nacional de Perfiles Ocupacionales (PDF en `docs/fuentes/`) | 27 oct 2026 |
| `cursos.json` | CAPACITA-T del MTPE (temario de cada curso) | 27 oct 2026 |
| `avisos.json`, `demanda.json` | Empleos Perú (MTPE), avisos de Lima | 27 oct 2026, 19:58 |

## Empezar (Windows, VS Code)

1. Instala [Python 3.10+](https://www.python.org/downloads/), [Git](https://git-scm.com/) y [Node.js 20+](https://nodejs.org/) (Node solo para el módulo M6).
2. Abre esta carpeta en VS Code y abre la terminal (Ctrl + ñ).
3. Crea el entorno y las dependencias:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   ```
4. Abre `.env` y pega tu token de QVAC en `QVAC_TOKEN=`. **Nunca subas `.env`.**
5. Comprueba los datos: `python scripts/validar_datos.py`
6. Prueba QVAC (con el hotspot del celular, la red de la ULima bloquea ngrok): `python scripts/probar_qvac2.py`
7. Pantallas (M6): arma el build y FastAPI lo sirve en http://127.0.0.1:8000
   ```powershell
   cd web; npm install; npm run build; cd ..
   uvicorn app.main:app
   ```
8. Pruebas de pantalla (Playwright, en 360 y 1280 px, contra el backend en modo respaldo; las capturas quedan en `tests/e2e/capturas/`):
   ```powershell
   cd web; npx playwright install chromium; npm run build; npm run e2e
   ```

## Subir a GitHub (primera vez)

```powershell
git init
git add .
git commit -m "M1: datos verificados y documentación"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
git push -u origin main
```

Antes de cada push, comprueba que el token no esté en ningún archivo: `git grep -nE "QVAC_TOKEN=[A-Za-z0-9]"` no debe mostrar nada.

## Trabajar con Claude Code

1. Instala la extensión **Claude Code** en VS Code e inicia sesión.
2. Claude Code lee `CLAUDE.md` automáticamente: ahí están el stack, las reglas y las buenas prácticas.
3. Para cada módulo, pega el contenido de `prompts/M0.md`, luego `M1.md`, y así. Cada prompt pide plan → pruebas → código → resumen, y espera tu revisión antes del commit.
4. No pases al siguiente módulo hasta cumplir su "Hecho cuando" en `docs/checklist.md`.

## Documentación

| Documento | Para qué |
|---|---|
| `docs/spec.md` | Especificación técnica: la fuente de verdad |
| `docs/historias.md` | 16 historias de usuario con criterios de aceptación |
| `docs/checklist.md` | Tareas por módulo |
| `docs/mockup/` | Pantallas de referencia y colores |
| `docs/fuentes/` | PDF oficiales de los 6 perfiles del MTPE |
| `docs/historico/` | Definición del producto original (24 oct) |

## Límites

La herramienta orienta; no certifica competencias, no promete empleo y no decide por la persona. No pide DNI, edad, género, discapacidad ni nivel educativo. Nombre, distrito, teléfono y correo se escriben solo en la pantalla del CV, se quedan en el navegador y nunca se envían al servidor ni se guardan en la base. Los relatos de prueba son inventados.
