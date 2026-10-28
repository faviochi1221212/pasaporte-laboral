// Las pruebas viven fuera de web/ (CLAUDE.md): @playwright/test se importa desde web/node_modules.
import { expect, type Page, type TestInfo } from "../../web/node_modules/@playwright/test";
import maria from "../relatos/maria_cajera.json";

export const RELATO_MARIA = maria;

// Igual que tests/casos_api.py, para que los mensajes calcen con los fixtures grabados.
export const RESPUESTA_A_REPREGUNTA_SIN_RELATO = "Preparo el almuerzo del domingo.";
export const SELLO_A_QUITAR = "H2452001-1.E2";

const RAICES = ["certific", "competen", "brecha", "no sirves"];
const FRASE_CV = /competencias declaradas/gi;

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

/** Regla 5: ninguna palabra prohibida en pantalla; "competencias declaradas" solo vale en /cv. */
export async function sinPalabrasProhibidas(pagina: Page): Promise<void> {
  let texto = await pagina.locator("body").innerText();
  if (new URL(pagina.url()).pathname.startsWith("/cv")) texto = texto.replace(FRASE_CV, "");
  const normal = ` ${normalizar(texto)}`;
  for (const raiz of RAICES) expect(normal, `"${raiz}" en ${pagina.url()}`).not.toContain(` ${raiz}`);
}

/** Captura de página completa en tests/e2e/capturas/, con el ancho en el nombre. */
export async function capturar(pagina: Page, info: TestInfo, nombre: string): Promise<void> {
  await sinPalabrasProhibidas(pagina);
  await pagina.screenshot({ path: `../tests/e2e/capturas/${nombre}-${info.project.name}.png`, fullPage: true });
}

/** Sin scroll horizontal (HU-14). */
export async function sinScrollHorizontal(pagina: Page): Promise<void> {
  const ancho = await pagina.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  expect(ancho).toBeLessThanOrEqual(0);
}

/** Inicio → Caja → responde las 6 preguntas de María como tests/casos_api.py, hasta el pasaporte. */
export async function conversarComoMaria(pagina: Page, info?: TestInfo): Promise<void> {
  if (info) {
    // Demora el pasaporte para alcanzar a capturar la pantalla de Espera.
    await pagina.route("**/pasaporte", async (ruta) => {
      await new Promise((listo) => setTimeout(listo, 1500));
      await ruta.continue();
    });
  }
  await pagina.goto("/");
  await pagina.getByRole("button", { name: "Caja" }).click();
  for (const respuesta of maria.respuestas) {
    await responder(pagina, respuesta.texto);
    const repregunta = await esperarTurno(pagina, respuesta.n);
    if (repregunta) await responder(pagina, ("repregunta" in respuesta && respuesta.repregunta) || RESPUESTA_A_REPREGUNTA_SIN_RELATO);
    if (respuesta.n === 3 && info) await capturar(pagina, info, "02-conversacion");
  }
  if (info) {
    await expect(pagina.getByText("Armando tu pasaporte…")).toBeVisible({ timeout: 15_000 });
    await capturar(pagina, info, "03-espera");
  }
  await expect(pagina).toHaveURL(/\/pasaporte$/, { timeout: 30_000 });
}

async function responder(pagina: Page, texto: string): Promise<void> {
  const campo = pagina.getByLabel("Tu respuesta");
  await expect(campo).toBeEnabled({ timeout: 15_000 });
  await campo.fill(texto);
  await pagina.getByRole("button", { name: "Enviar" }).click();
  await expect(campo).toBeDisabled();
}

/** Espera a que el asistente termine de hablar; devuelve true si lo último fue una repregunta. */
async function esperarTurno(pagina: Page, n: number): Promise<boolean> {
  if (n === 6) return false;
  const campo = pagina.getByLabel("Tu respuesta");
  await expect(campo).toBeEnabled({ timeout: 15_000 });
  return (await pagina.locator("[data-pregunta-abierta]").getAttribute("data-pregunta-abierta")) === `${n}`;
}
