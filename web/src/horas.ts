import type { Horas } from "./api";

/**
 * Horas libres por semana a partir de la respuesta a la pregunta 6 (spec 6): "1 a 2 h" → 1-2,
 * "3 a 5 h" → 3-5, "Más de 5 h" → 5+. Con texto libre se usa el número mayor que diga la persona;
 * si no dice ninguno, 1-2 (así las semanas del curso nunca se quedan cortas).
 */
export function horasDeRespuesta(texto: string): Horas {
  const normal = texto.toLowerCase().normalize("NFD").replace(/\p{Mn}/gu, "");
  if (/mas de\s*5|5\s*\+/.test(normal)) return "5+";
  const numeros = (normal.match(/\d+/g) ?? []).map(Number);
  if (numeros.length === 0) return "1-2";
  const mayor = Math.max(...numeros);
  if (mayor <= 2) return "1-2";
  return mayor <= 5 ? "3-5" : "5+";
}
