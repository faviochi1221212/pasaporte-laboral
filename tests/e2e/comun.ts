// Las pruebas viven fuera de web/ (CLAUDE.md): @playwright/test se importa desde web/node_modules.
import { expect, type Locator, type Page, test } from "../../web/node_modules/@playwright/test";
import maria from "../relatos/maria_cajera.json";

export const RELATO_MARIA = maria;

const RAICES = ["certific", "competen", "brecha", "no sirves"];
const FRASE_CV = /competencias declaradas/gi;
const TOCABLES = "button, a.boton, a.volver, a.estacion, input, textarea";

/** Igual que calculo.normalizar: minúsculas, sin tildes, sin signos ni espacios dobles. */
function normalizar(texto: string): string {
  return texto
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Mn}/gu, "")
    .replace(/[^\p{L}\p{N}\s]|_/gu, " ")
    .split(/\s+/)
    .filter(Boolean)
    .join(" ");
}

/** A10: en celular (360) todo se hace tocando; en computadora (1280), con clic. */
export async function tocar(elemento: Locator): Promise<void> {
  if (test.info().project.name === "360") await elemento.tap();
  else await elemento.click();
}

/** Regla 5: ninguna palabra prohibida en pantalla; "competencias declaradas" solo vale en /cv. */
export async function sinPalabrasProhibidas(pagina: Page): Promise<void> {
  let texto = await pagina.locator("body").innerText();
  if (new URL(pagina.url()).pathname.startsWith("/cv")) texto = texto.replace(FRASE_CV, "");
  const normal = ` ${normalizar(texto)}`;
  for (const raiz of RAICES) expect(normal, `"${raiz}" en ${pagina.url()}`).not.toContain(` ${raiz}`);
}

/** HU-14: sin scroll horizontal y todo lo que se toca mide al menos 48 px de alto. */
async function usableEnCelular(pagina: Page): Promise<void> {
  const sobra = await pagina.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(sobra, `scroll horizontal en ${pagina.url()}`).toBeLessThanOrEqual(0);
  const bajos = await pagina.locator(TOCABLES).evaluateAll((elementos) =>
    elementos
      .filter((e) => (e as HTMLElement).offsetParent !== null && e.getBoundingClientRect().height < 47.5)
      .map((e) => `${e.tagName} "${(e.textContent ?? "").trim().slice(0, 30)}" ${Math.round(e.getBoundingClientRect().height)} px`),
  );
  expect(bajos, `menos de 48 px en ${pagina.url()}`).toEqual([]);
}

/** A11: en computadora (1280 y 1920), las pantallas con columnas muestran 2. */
async function dosColumnasEnComputadora(pagina: Page): Promise<void> {
  if (test.info().project.name === "360") return;
  for (const columnas of await pagina.locator(".columnas").all()) {
    const pistas = await columnas.evaluate((e) => getComputedStyle(e).gridTemplateColumns.split(" ").length);
    expect(pistas, `columnas en ${pagina.url()}`).toBe(2);
  }
}

/** En 1920, el contenido va centrado: no queda pegado a la izquierda con la derecha vacía. */
async function centradoEnPantallaAncha(pagina: Page): Promise<void> {
  if (test.info().project.name !== "1920") return;
  const [izquierda, derecha] = await pagina.locator("main").evaluate((main) => {
    const cajas = [...main.children].map((hijo) => hijo.getBoundingClientRect()).filter((c) => c.width > 0);
    const desde = Math.min(...cajas.map((c) => c.left));
    const hasta = Math.max(...cajas.map((c) => c.right));
    return [desde, window.innerWidth - hasta];
  });
  expect(Math.abs(izquierda - derecha), `contenido descentrado en ${pagina.url()}`).toBeLessThanOrEqual(48);
}

export const BLANCO = "rgb(255, 255, 255)";
const ROJO_PERU = "rgb(217, 16, 35)";
const ROJO_PERU_OSCURO = "rgb(165, 13, 27)"; // hover: el mouse puede quedar encima después de un clic
const AZUL = "rgb(28, 95, 168)";
const PIE = "Prototipo para la Innovathon ULima x Tether 2026 · No es un servicio oficial del MTPE";

/** Pie de página pequeño y visible en todas las pantallas. */
async function conPie(pagina: Page): Promise<void> {
  await expect(pagina.locator(".pie"), `pie en ${pagina.url()}`).toHaveText(PIE);
  await expect(pagina.locator(".pie")).toBeVisible();
}

/** Color principal: los botones principales van en rojo con texto blanco (AA) y ningún botón usa el azul. */
async function botonesEnRojo(pagina: Page): Promise<void> {
  const estilos = await pagina.locator("button, a.boton").evaluateAll((elementos) =>
    elementos
      .filter((e) => (e as HTMLElement).offsetParent !== null)
      .map((e) => {
        const s = getComputedStyle(e);
        const principal = e.classList.contains("boton") && !e.classList.contains("boton-secundario");
        const nombre = `${e.tagName} "${(e.textContent || e.getAttribute("aria-label") || "").trim().slice(0, 30)}"`;
        return { nombre, principal, fondo: s.backgroundColor, texto: s.color, borde: s.borderTopColor };
      }),
  );
  for (const b of estilos) {
    expect([b.fondo, b.texto, b.borde], `${b.nombre} usa el azul en ${pagina.url()}`).not.toContain(AZUL);
    if (!b.principal) continue;
    expect([ROJO_PERU, ROJO_PERU_OSCURO], `${b.nombre} en ${pagina.url()}`).toContain(b.fondo);
    expect(contraste(b.texto, b.fondo), `${b.nombre} en ${pagina.url()}`).toBeGreaterThanOrEqual(4.5);
  }
}

/** Luminancia relativa de WCAG de un color "rgb(r, g, b)". */
function luminancia(rgb: string): number {
  const [r, g, b] = (rgb.match(/\d+/g) ?? []).slice(0, 3).map((v) => {
    const c = Number(v) / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * (r ?? 0) + 0.7152 * (g ?? 0) + 0.0722 * (b ?? 0);
}

/** Contraste WCAG entre dos colores "rgb(r, g, b)" (AA para texto: 4,5 o más). */
export function contraste(a: string, b: string): number {
  const [claro, oscuro] = [luminancia(a), luminancia(b)].sort((x, y) => y - x);
  return ((claro ?? 0) + 0.05) / ((oscuro ?? 0) + 0.05);
}

/** Revisa la pantalla (regla 5, A10, A11, 1920, pie y color principal) y guarda una captura completa en tests/e2e/capturas/. */
export async function capturar(pagina: Page, nombre: string): Promise<void> {
  await sinPalabrasProhibidas(pagina);
  await usableEnCelular(pagina);
  await dosColumnasEnComputadora(pagina);
  await centradoEnPantallaAncha(pagina);
  await conPie(pagina);
  await botonesEnRojo(pagina);
  await guardarCaptura(pagina, nombre);
}

export async function guardarCaptura(pagina: Page, nombre: string): Promise<void> {
  const proyecto = test.info().project.name;
  await pagina.screenshot({ path: `../tests/e2e/capturas/${nombre}-${proyecto}.png`, fullPage: true });
}

/**
 * Inicio → Caja → las 6 preguntas de María como tests/casos_api.py, hasta el pasaporte.
 * Con `capturas`, guarda la conversación y la espera.
 */
export async function conversarComoMaria(pagina: Page, capturas = false): Promise<void> {
  await conversarHastaElFin(pagina, capturas);
  await expect(pagina).toHaveURL(/\/pasaporte$/, { timeout: 30_000 });
}

/** Responde las 6 preguntas de María; la pantalla queda en la Espera (o en lo que siga). */
export async function conversarHastaElFin(pagina: Page, capturas = false): Promise<void> {
  if (capturas) {
    // Demora el pasaporte para alcanzar a capturar la pantalla de Espera.
    await pagina.route("**/pasaporte", async (ruta) => {
      await new Promise((listo) => setTimeout(listo, 1500));
      await ruta.continue();
    });
  }
  await pagina.goto("/");
  await tocar(pagina.getByRole("button", { name: "Caja" }));
  for (const respuesta of maria.respuestas) {
    await responder(pagina, respuesta.texto);
    if (await esRepregunta(pagina, respuesta.n)) {
      const repregunta = "repregunta" in respuesta ? respuesta.repregunta : undefined;
      expect(repregunta, `el modelo repreguntó en la ${respuesta.n} y el relato de María no trae respuesta`).toBeTruthy();
      await responder(pagina, repregunta ?? "");
    }
    if (respuesta.n === 3 && capturas) await capturar(pagina, "02-conversacion");
  }
  if (capturas) {
    await expect(pagina.getByText("Armando tu pasaporte…")).toBeVisible({ timeout: 15_000 });
    await capturar(pagina, "03-espera");
  }
}

/** Como A8: quita el primer sello del pasaporte y lo deshace, para que la ruta use el pasaporte completo. */
export async function quitarYDeshacerElPrimerSello(pagina: Page): Promise<void> {
  const primero = pagina.locator(".libreta-sello").first();
  const nombre = (await primero.getAttribute("aria-label")) ?? "";
  await tocar(primero);
  await tocar(pagina.getByRole("button", { name: "Quitar este sello" }));
  await expect(pagina.getByRole("button", { name: nombre, exact: true })).toHaveCount(0);
  await tocar(pagina.getByRole("button", { name: /^Deshacer/ }).first());
  await expect(pagina.getByRole("button", { name: nombre, exact: true })).toBeVisible();
}

/** Recorrido de A8 hasta la ruta: conversa, quita y deshace un sello y elige "Con gente". */
export async function hastaLaRuta(pagina: Page): Promise<void> {
  await conversarComoMaria(pagina);
  await quitarYDeshacerElPrimerSello(pagina);
  await tocar(pagina.getByRole("link", { name: "Ver a dónde te lleva" }));
  await tocar(pagina.getByRole("button", { name: /Con gente/ }));
  await expect(pagina.getByRole("heading", { name: "Tu ruta" })).toBeVisible();
}

export async function responder(pagina: Page, texto: string): Promise<void> {
  const campo = pagina.getByLabel("Tu respuesta");
  await expect(campo).toBeEnabled({ timeout: 15_000 });
  await campo.fill(texto);
  await tocar(pagina.getByRole("button", { name: "Enviar" }));
  await expect(campo).toBeDisabled();
}

/** Espera a que el asistente termine de hablar; true si lo último fue una repregunta (sigue la misma n). */
async function esRepregunta(pagina: Page, n: number): Promise<boolean> {
  if (n === 6) return false;
  await expect(pagina.getByLabel("Tu respuesta")).toBeEnabled({ timeout: 15_000 });
  return (await pagina.locator("[data-pregunta-abierta]").getAttribute("data-pregunta-abierta")) === `${n}`;
}
