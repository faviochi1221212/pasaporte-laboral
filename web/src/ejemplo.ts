// Solo en modo respaldo (spec 7): el relato de María, que es el que tiene respuestas grabadas.
import maria from "../../tests/relatos/maria_cajera.json";

/** Origen del ejemplo (Caja), para "Empezar con el ejemplo". */
export const ORIGEN_EJEMPLO = maria.ocupacion_origen;

/** La respuesta de María a la pregunta n, o a su repregunta; undefined si el relato no la trae. */
export function respuestaDeEjemplo(n: number, repregunta: boolean): string | undefined {
  const respuesta = maria.respuestas.find((r) => r.n === n);
  if (!respuesta) return undefined;
  return repregunta ? ("repregunta" in respuesta ? respuesta.repregunta : undefined) : respuesta.texto;
}
