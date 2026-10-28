const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "set", "oct", "nov", "dic"];

/** "2026-10-27T19:58-05:00" → "27 oct" (fecha de la foto de Empleos Perú). */
export function fechaCorta(iso: string): string {
  const [, mes, dia] = iso.slice(0, 10).split("-").map(Number);
  return `${dia} ${MESES[(mes ?? 1) - 1]}`;
}

/** "2026-10-27T19:58-05:00" → "27 oct 2026". */
export function fechaConAnio(iso: string): string {
  return `${fechaCorta(iso)} ${iso.slice(0, 4)}`;
}
