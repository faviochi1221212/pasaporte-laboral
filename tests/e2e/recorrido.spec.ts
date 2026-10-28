import { expect, test } from "../../web/node_modules/@playwright/test";
import { capturar, conversarComoMaria, RELATO_MARIA, sinScrollHorizontal } from "./comun";

const [RESPUESTA_1, RESPUESTA_2] = RELATO_MARIA.respuestas.map((r) => r.texto);

test("e2e-01: inicio → elegir Caja → primera pregunta", async ({ page }, info) => {
  await page.goto("/");
  await expect(page.getByText("Prototipo · no es un sitio oficial")).toBeVisible();
  await expect(page.getByText("modo sin conexión")).toBeVisible();
  await expect(page.getByText("gob.pe")).toHaveCount(0);
  await sinScrollHorizontal(page);
  await capturar(page, info, "01-inicio");
  await page.getByRole("button", { name: "Caja" }).click();
  await expect(page.getByText("Soy el asistente de empleo del Ministerio de Trabajo")).toBeVisible();
  await expect(page.getByText("¿Cuánto tiempo llevas en esto?")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByRole("button", { name: "1 a 5 años" })).toBeVisible();
  await sinScrollHorizontal(page);
  await capturar(page, info, "01-pregunta-1");
});

test("e2e-02: chat completo con escribiendo, reacciones, repregunta y contador de sellos", async ({ page }, info) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Caja" }).click();
  await expect(page.getByText("escribiendo…")).toBeVisible();
  await conversarComoMaria(page, info);
  await expect(page.getByRole("heading", { name: "¡Mira todo lo que sabes!" })).toBeVisible();
});

test("e2e-02b: la conversación muestra reacciones del modelo y el contador de sellos", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Caja" }).click();
  const campo = page.getByLabel("Tu respuesta");
  await expect(campo).toBeEnabled({ timeout: 15_000 });
  await campo.fill(RESPUESTA_1);
  await page.getByRole("button", { name: "Enviar" }).click();
  await expect(page.locator(".burbuja-asistente").nth(2)).not.toHaveText("Gracias por contarme.", { timeout: 15_000 });
  await expect(campo).toBeEnabled({ timeout: 15_000 });
  await campo.fill(
    RESPUESTA_2,
  );
  await page.getByRole("button", { name: "Enviar" }).click();
  await expect(page.getByText(/\d+ sellos? ganados?/)).toBeVisible({ timeout: 15_000 });
});

test("e2e-02c (A13): si sellos-parciales falla, la barra no aparece y no hay error en pantalla", async ({ page }) => {
  await page.route("**/sellos-parciales", (ruta) =>
    ruta.fulfill({ status: 503, json: { error: { codigo: "parcial_no_disponible", mensaje: "x" } } }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Caja" }).click();
  const campo = page.getByLabel("Tu respuesta");
  for (const texto of [
    RESPUESTA_1,
    RESPUESTA_2,
  ]) {
    await expect(campo).toBeEnabled({ timeout: 15_000 });
    await campo.fill(texto);
    await page.getByRole("button", { name: "Enviar" }).click();
    await expect(campo).toBeDisabled();
  }
  await expect(campo).toBeEnabled({ timeout: 15_000 });
  await expect(page.getByText("¿Qué te piden a ti porque lo haces bien?")).toBeVisible();
  await expect(page.getByText(/sellos? ganados?/)).toHaveCount(0);
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("e2e-04 (parte 1): pasaporte con sellos agrupados, frase al tocar, quitar y deshacer", async ({ page }, info) => {
  await conversarComoMaria(page);
  await sinScrollHorizontal(page);
  await capturar(page, info, "04-pasaporte");
  await expect(page.getByText("sirve en 2 trabajos")).toBeVisible();
  await page.getByRole("button", { name: /Sello: Cuadra la caja/ }).click();
  await expect(page.getByText(/Lo ganaste porque dijiste/)).toBeVisible();
  await capturar(page, info, "04-pasaporte-frase");
  await page.getByRole("button", { name: "Quitar este sello" }).click();
  await expect(page.getByRole("button", { name: /Sello: Cuadra la caja/ })).toHaveCount(0);
  await page.getByRole("button", { name: /Deshacer/ }).first().click();
  await expect(page.getByRole("button", { name: /Sello: Cuadra la caja/ })).toBeVisible();
});

test("e2e-04: pasaporte → intereses → ruta con 3 destinos", async ({ page }, info) => {
  await conversarComoMaria(page);
  await page.getByRole("link", { name: "Ver a dónde te lleva" }).click();
  await expect(page.getByRole("heading", { name: "¿Qué tipo de trabajo te gusta más?" })).toBeVisible();
  await sinScrollHorizontal(page);
  await capturar(page, info, "04-intereses");
  await page.getByRole("button", { name: /Con gente/ }).click();
  await expect(page.getByRole("heading", { name: "Tu ruta" })).toBeVisible();
  const estaciones = page.getByRole("link", { name: /^Estación:/ });
  await expect(estaciones).toHaveCount(3);
  for (const nombre of ["Recepción de Hotel/Hostal", "Atención en Salón de Comidas y Bebidas/Eventos", "Operaciones de Almacén"]) {
    await expect(page.getByRole("link", { name: `Estación: ${nombre}` })).toBeVisible();
  }
  await expect(page.getByText(/avisos en Lima al 27 oct/).first()).toBeVisible();
  await sinScrollHorizontal(page);
  await capturar(page, info, "04-ruta");
});

test("e2e-05: detalle de un destino con los 4 bloques en orden", async ({ page }, info) => {
  await conversarComoMaria(page);
  await page.getByRole("link", { name: "Ver a dónde te lleva" }).click();
  await page.getByRole("button", { name: /Con gente/ }).click();
  await page.getByRole("link", { name: "Estación: Operaciones de Almacén" }).click();
  await expect(page.getByRole("heading", { name: "Operaciones de Almacén" })).toBeVisible();
  const bloques = await page.getByRole("heading", { level: 2 }).allInnerTexts();
  expect(bloques).toEqual([
    "Lo que ya haces y aquí también sirve",
    "Qué harías ahí",
    "Lo que te falta",
    "Avisos hoy en Lima",
  ]);
  const yaHaces = page.locator("section").filter({ has: page.getByRole("heading", { name: "Lo que ya haces y aquí también sirve" }) });
  await expect(yaHaces.locator("q").first()).not.toBeEmpty();
  await expect(page.getByText("No encontramos un curso gratuito del MTPE que cubra esto")).toBeVisible();
  await expect(page.getByText(/unas \d+ semanas con tu tiempo/)).toBeVisible();
  await expect(page.getByText(/Te ayuda con la parte teórica de/)).toBeVisible();
  await sinScrollHorizontal(page);
  await capturar(page, info, "05-destino");
});
