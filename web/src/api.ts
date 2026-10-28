// Cliente tipado de la API (spec 6). Los tipos son iguales a los modelos Pydantic de app/main.py.
import type { Icono } from "./componentes/Sello";

export interface Salud {
  ok: boolean;
  modo: "real" | "respaldo";
}

export interface Pregunta {
  n: number;
  texto: string;
  ejemplos: string[];
}

export interface SesionCreada {
  sesion_id: string;
  saludo: string;
  pregunta: Pregunta;
}

export interface Turno {
  tipo: "repregunta" | "siguiente" | "fin";
  reaccion: string | null;
  pregunta: Pregunta | null;
  cierre: string | null;
  parcial_listo: boolean;
}

export interface SellosParciales {
  sellos_ganados: number;
  etiquetas: string[];
}

export interface Sello {
  codigo: string;
  etiqueta: string;
  icono: Icono;
  evidencia: string;
}

export interface Fortaleza {
  texto: string;
  evidencia: string;
}

export interface Pasaporte {
  sellos: Sello[];
  fortalezas: Fortaleza[];
}

export type Interes = "gente" | "cosas" | "papeles";
export type Horas = "1-2" | "3-5" | "5+";

export interface Curso {
  id: string;
  nombre: string;
  horas: number;
  url: string;
  alcance: string;
  modulo: string;
  se_lleva: string;
  semanas: number;
}

export interface Faltante {
  codigo: string;
  etiqueta: string;
  curso: Curso | null;
  mensaje: string | null;
}

export interface Destino {
  codigo: string;
  nombre: string;
  puntaje: number;
  cobertura: number;
  interes: number;
  demanda: number;
  tienes: string[];
  que_harias: string[];
  faltan: Faltante[];
  avisos_lima: number;
}

export interface Ruta {
  foto: string;
  destinos: Destino[];
}

export interface Aviso {
  id: string;
  perfil: string;
  titulo: string;
  empresa: string;
  distrito: string;
  ubigeo: string;
  sueldo: string | null;
  publicado: string;
  cierre: string;
  que_piden: string[];
  url: string;
  fuente: string;
  tomado: string;
  nota: string | null;
}

export interface Avisos {
  avisos: Aviso[];
  mensaje: string | null;
}

export interface SelloCv {
  etiqueta: string;
  texto_simple: string;
  codigos: string[];
}

export interface Cv {
  resumen: string;
  puesto: string | null;
  anios: string | null;
  sellos: SelloCv[];
  fortalezas: Fortaleza[];
  destino: string;
  curso: Curso | null;
}

/** Error con el formato único de la API: {"error": {"codigo", "mensaje"}}. */
export class ErrorApi extends Error {
  constructor(
    readonly estado: number,
    readonly codigo: string,
    mensaje: string,
  ) {
    super(mensaje);
  }
}

async function pedir<T>(metodo: "GET" | "POST" | "PUT", ruta: string, cuerpo?: unknown): Promise<T> {
  const respuesta = await fetch(`/api${ruta}`, {
    method: metodo,
    headers: cuerpo === undefined ? undefined : { "Content-Type": "application/json" },
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
  });
  const datos: unknown = await respuesta.json();
  if (!respuesta.ok) {
    const error = (datos as { error?: { codigo?: string; mensaje?: string } }).error;
    throw new ErrorApi(respuesta.status, error?.codigo ?? "error", error?.mensaje ?? "Algo salió mal.");
  }
  return datos as T;
}

const sesion = (id: string) => `/sesiones/${encodeURIComponent(id)}`;

export const api = {
  salud: () => pedir<Salud>("GET", "/salud"),
  crearSesion: (ocupacion_origen: string | null) =>
    pedir<SesionCreada>("POST", "/sesiones", { ocupacion_origen }),
  responder: (id: string, n: number, texto: string) =>
    pedir<Turno>("POST", `${sesion(id)}/respuestas`, { n, texto }),
  sellosParciales: (id: string) => pedir<SellosParciales>("POST", `${sesion(id)}/sellos-parciales`),
  armarPasaporte: (id: string) => pedir<Pasaporte>("POST", `${sesion(id)}/pasaporte`),
  editarPasaporte: (id: string, quitar: string[], quitar_fortalezas: number[]) =>
    pedir<Pasaporte>("PUT", `${sesion(id)}/pasaporte`, { quitar, quitar_fortalezas }),
  guardarPreferencias: (id: string, interes: Interes, horas: Horas) =>
    pedir<{ ok: boolean }>("PUT", `${sesion(id)}/preferencias`, { interes, horas }),
  ruta: (id: string) => pedir<Ruta>("GET", `${sesion(id)}/ruta`),
  avisos: (id: string, destino: string) =>
    pedir<Avisos>("GET", `${sesion(id)}/avisos?destino=${encodeURIComponent(destino)}`),
  cv: (id: string, destino: string) =>
    pedir<Cv>("GET", `${sesion(id)}/cv?destino=${encodeURIComponent(destino)}`),
};
