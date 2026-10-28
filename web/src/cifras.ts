// Cifras del Inicio, sacadas de data/ al compilar: después de actualizar data/ hay que correr npm run build.
import competencias from "../../data/competencias.json";
import demanda from "../../data/demanda.json";
import ocupaciones from "../../data/ocupaciones.json";
import { fechaConAnio } from "./fecha";

/** Fecha de la foto de Empleos Perú, como "27 oct 2026". */
export const FECHA_FOTO = fechaConAnio(demanda.tomado);

/** Número de trabajos del catálogo cargados en ocupaciones.json. */
export const TRABAJOS = ocupaciones.length;

/** Número de tareas (elementos de competencias.json) que pueden dar un sello. */
export const TAREAS = competencias.length;

/** El perfil con más avisos en Lima según demanda.json, con su nombre de ocupaciones.json. */
export const MAS_AVISOS = (() => {
  const [codigo, perfil] = Object.entries(demanda.perfiles).sort((a, b) => b[1].avisos - a[1].avisos)[0]!;
  const nombre = ocupaciones.find((o) => o.codigo === codigo)?.nombre ?? codigo;
  return { nombre, avisos: perfil.avisos };
})();
