// e2e-01 a e2e-07 (docs/historias.md) en 360 y 1280 px, contra el backend en modo respaldo.
import { expect, type Page, test } from "../../web/node_modules/@playwright/test";
import {
  capturar,
  conversarComoMaria,
  guardarCaptura,
  hastaLaRuta,
  quitarYDeshacerElPrimerSello,
  RELATO_MARIA,
  responder,
  sinPalabrasProhibidas,
  tocar,
} from "./comun";

const [RESPUESTA_1, RESPUESTA_2] = RELATO_MARIA.respuestas.map((r) => r.texto ?? "");
const PLANTILLA_RESUMEN = "Experiencia práctica en:";

/** Cambia de pantalla sin recargar, para no perder la sesión que vive en memoria. */
async function irSinRecargar(page: Page, ruta: string): Promise<void> {
  await page.evaluate((destino) => {
    window.history.pushState({}, "", destino);
    window.dispatchEvent(new PopStateEvent("popstate"));
  }, ruta);
}

test("e2e-01: inicio → elegir Caja → primera pregunta", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Prototipo · no es un sitio oficial")).toBeVisible();
  await expect(page.getByText("modo sin conexión")).toBeVisible();
  await expect(page.getByText("gob.pe")).toHaveCount(0);
  await capturar(page, "01-inicio");
  await tocar(page.getByRole("button", { name: "Caja" }));
  await expect(page.getByText("Soy el asistente de empleo del Ministerio de Trabajo")).toBeVisible();
  await expect(page.getByText("¿Cuánto tiempo llevas en esto?")).toBeVisible({ timeout: 10_000 });
  await expect(page.getByRole("button", { name: "1 a 5 años" })).toBeVisible();
  await capturar(page, "01-pregunta-1");
});

test("e2e-02: chat completo con escribiendo, reacciones, repregunta y contador de sellos", async ({ page }) => {
  await page.goto("/");
  await tocar(page.getByRole("button", { name: "Caja" }));
  await expect(page.getByText("escribiendo…")).toBeVisible();
  await conversarComoMaria(page, true);
  await expect(page.getByRole("heading", { name: "¡Mira todo lo que sabes!" })).toBeVisible();
});

test("e2e-02b: reacciones del modelo grabadas y contador de sellos", async ({ page }) => {
  await page.goto("/");
  await tocar(page.getByRole("button", { name: "Caja" }));
  await responder(page, RESPUESTA_1);
  await expect(page.locator(".burbuja-asistente").nth(2)).not.toHaveText("Gracias por contarme.", { timeout: 15_000 });
  await responder(page, RESPUESTA_2);
  await expect(page.getByText(/\d+ sellos? ganados?/)).toBeVisible({ timeout: 15_000 });
});

test("e2e-02c (A13): si sellos-parciales falla, la barra no aparece y no hay error en pantalla", async ({ page }) => {
  await page.route("**/sellos-parciales", (ruta) =>
    ruta.fulfill({ status: 503, json: { error: { codigo: "parcial_no_disponible", mensaje: "x" } } }),
  );
  await page.goto("/");
  await tocar(page.getByRole("button", { name: "Caja" }));
  await responder(page, RESPUESTA_1);
  await responder(page, RESPUESTA_2);
  await expect(page.getByLabel("Tu respuesta")).toBeEnabled({ timeout: 15_000 });
  await expect(page.getByText("¿Qué te piden a ti porque lo haces bien?")).toBeVisible();
  await expect(page.getByText(/sellos? ganados?/)).toHaveCount(0);
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("e2e-03: sin dictado en el navegador, el botón del micrófono no aparece", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, "SpeechRecognition", { value: undefined });
    Object.defineProperty(window, "webkitSpeechRecognition", { value: undefined });
  });
  await page.goto("/");
  await expect(page.getByText("Puedes hablar")).toHaveCount(0);
  await tocar(page.getByRole("button", { name: "Caja" }));
  await expect(page.getByLabel("Tu respuesta")).toBeEnabled({ timeout: 15_000 });
  await expect(page.getByRole("button", { name: "Responder hablando" })).toHaveCount(0);
  await capturar(page, "03-sin-dictado");
});

test("e2e-03b: con dictado, el texto llega al campo y se puede corregir antes de enviar", async ({ page }) => {
  await page.addInitScript(() => {
    class DictadoFalso {
      lang = "";
      interimResults = false;
      onresult: ((e: { results: { transcript: string }[][] }) => void) | null = null;
      onend: (() => void) | null = null;
      onerror: (() => void) | null = null;
      start() {
        this.onresult?.({ results: [[{ transcript: "seis años en caja" }]] });
        this.onend?.();
      }
      stop() {
        this.onend?.();
      }
    }
    Object.defineProperty(window, "SpeechRecognition", { value: DictadoFalso });
  });
  await page.goto("/");
  await expect(page.getByText("Puedes hablar")).toBeVisible();
  await tocar(page.getByRole("button", { name: "Caja" }));
  const campo = page.getByLabel("Tu respuesta");
  await expect(campo).toBeEnabled({ timeout: 15_000 });
  await tocar(page.getByRole("button", { name: "Responder hablando" }));
  await expect(campo).toHaveValue("seis años en caja");
  await campo.fill("Seis años en caja, en Ate.");
  await expect(campo).toHaveValue("Seis años en caja, en Ate.");
});

test("e2e-04: pasaporte → intereses → ruta con 3 destinos", async ({ page }) => {
  await conversarComoMaria(page);
  await capturar(page, "04-pasaporte");
  await expect(page.getByText("sirve en 2 trabajos")).toBeVisible();
  await tocar(page.getByRole("button", { name: /Sello: Cuadra la caja/ }));
  await expect(page.getByText(/Lo ganaste porque dijiste/)).toBeVisible();
  await capturar(page, "04-pasaporte-frase");
  await quitarYDeshacerElPrimerSello(page);

  await tocar(page.getByRole("link", { name: "Ver a dónde te lleva" }));
  await expect(page.getByRole("heading", { name: "¿Qué tipo de trabajo te gusta más?" })).toBeVisible();
  await capturar(page, "04-intereses");
  await tocar(page.getByRole("button", { name: /Con gente/ }));
  await expect(page.getByRole("heading", { name: "Tu ruta" })).toBeVisible();
  await expect(page.getByRole("link", { name: /^Estación:/ })).toHaveCount(3);
  for (const nombre of ["Recepción de Hotel/Hostal", "Atención en Salón de Comidas y Bebidas/Eventos", "Operaciones de Almacén"]) {
    await expect(page.getByRole("link", { name: `Estación: ${nombre}` })).toBeVisible();
  }
  await expect(page.getByText("3 avisos parecidos en Lima al 27 oct")).toBeVisible();
  await capturar(page, "04-ruta");
});

test("e2e-05: detalle de un destino con los 4 bloques en orden", async ({ page }) => {
  await hastaLaRuta(page);
  await tocar(page.getByRole("link", { name: "Estación: Operaciones de Almacén" }));
  await expect(page.getByRole("heading", { name: "Operaciones de Almacén" })).toBeVisible();
  expect(await page.getByRole("heading", { level: 2 }).allInnerTexts()).toEqual([
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
  await capturar(page, "05-destino");
});

test("e2e-06: avisos de un destino con y sin avisos", async ({ page }) => {
  await hastaLaRuta(page);
  await tocar(page.getByRole("link", { name: "Estación: Recepción de Hotel/Hostal" }));
  await tocar(page.getByRole("link", { name: "Ver los avisos" }));
  await expect(page.getByRole("heading", { name: "Para postular hoy" })).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(2);
  await expect(page.getByText(/Aviso parecido/).first()).toBeVisible();
  await expect(page.getByText("Qué piden").first()).toBeVisible();
  const enlace = page.getByRole("link", { name: /Ver el aviso en Empleos Perú/ }).first();
  await expect(enlace).toHaveAttribute("href", /^https:\/\/mtpe-candidatos\.empleosperu\.gob\.pe\//);
  await expect(enlace).toHaveAttribute("target", "_blank");
  await capturar(page, "06-avisos");
  await irSinRecargar(page, "/avisos/I2555002");
  await expect(page.getByText("Hoy no hay avisos en Lima para esto")).toBeVisible();
  await expect(page.getByRole("article")).toHaveCount(0);
  await capturar(page, "06-sin-avisos");
});

test("e2e-07: CV con nombre escrito en el navegador y sin enviarlo", async ({ page }) => {
  const enviado: string[] = [];
  page.on("request", (pedido) => enviado.push(`${pedido.url()} ${pedido.postData() ?? ""}`));
  await hastaLaRuta(page);
  // Mismo destino que A8 (tests/casos_api.py): el primero de la ruta, para que el resumen calce con el fixture.
  await tocar(page.getByRole("link", { name: /^Estación:/ }).first());
  await tocar(page.getByRole("link", { name: "Mi CV" }));
  await expect(page.getByText("COMPETENCIAS DECLARADAS", { exact: true })).toBeVisible();
  await expect(
    page.getByText("Competencias declaradas por la persona, basadas en el Catálogo Nacional de Perfiles Ocupacionales del MTPE."),
  ).toBeVisible();
  await expect(page.locator(".cv-hoja")).not.toContainText(PLANTILLA_RESUMEN);

  const imprimir = page.getByRole("button", { name: "Imprimir / Guardar PDF" });
  await tocar(imprimir);
  await expect(page.getByRole("alert")).toBeVisible();

  // Desde aquí, nada de lo que se escribe en el CV puede salir del navegador ("Ate" sí va en el relato).
  enviado.length = 0;
  const datos = { nombre: "María Quispe", distrito: "Ate", telefono: "999 000 000", correo: "maria.quispe@ejemplo.pe" };
  await page.getByLabel("Tu nombre").fill(datos.nombre);
  await page.getByLabel("Distrito").fill(datos.distrito);
  await page.getByLabel("Teléfono").fill(datos.telefono);
  await page.getByLabel("Correo").fill(datos.correo);
  await expect(page.getByText("MARÍA QUISPE")).toBeVisible();
  await expect(page.getByText(`${datos.distrito} | ${datos.telefono} | ${datos.correo}`)).toBeVisible();
  await expect(page.getByText("PERFIL", { exact: true })).toBeVisible();
  await expect(page.getByText("BUSCO Y CAPACITACIÓN")).toBeVisible();
  await capturar(page, "07-cv");
  for (const valor of Object.values(datos)) {
    expect(enviado.join("\n"), `"${valor}" salió del navegador`).not.toContain(valor);
    expect(enviado.join("\n")).not.toContain(encodeURIComponent(valor));
  }

  await page.emulateMedia({ media: "print" });
  await expect(page.getByText("Prototipo · no es un sitio oficial")).toBeHidden();
  await expect(imprimir).toBeHidden();
  expect(await page.locator(".cv-hoja").evaluate((e) => getComputedStyle(e).fontFamily)).toContain("Times New Roman");
  await sinPalabrasProhibidas(page);
  await guardarCaptura(page, "07-cv-impresion");
  if (test.info().project.name === "1280") {
    await page.pdf({ path: "../tests/e2e/capturas/cv-maria.pdf", format: "A4", printBackground: true });
  }
});
