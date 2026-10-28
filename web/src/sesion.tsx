import { createContext, useContext, useState, type ReactNode } from "react";
import { api, type Pasaporte, type Pregunta } from "./api";
import type { Ilustracion } from "./componentes/Trabajador";
import { TEXTOS } from "./textos";

/** Tarjetas de Inicio (HU-01): Caja, Almacén y Limpieza fijan su perfil de origen; el resto va sin origen. */
export interface Tarjeta {
  nombre: string;
  origen: string | null;
  ilustracion: Ilustracion;
}

const T = TEXTOS.inicio.tarjetas;
export const TARJETAS: Tarjeta[] = [
  { nombre: T.caja, origen: "G2347002", ilustracion: "cajera" },
  { nombre: T.ventas, origen: null, ilustracion: "vendedor" },
  { nombre: T.limpieza, origen: "M2981001", ilustracion: "limpieza" },
  { nombre: T.almacen, origen: "H2452001", ilustracion: "almacen" },
  { nombre: T.oficina, origen: null, ilustracion: "administrativo" },
  { nombre: T.todo, origen: null, ilustracion: "todo" },
];

/** Lo que la pantalla recuerda de la sesión. Vive solo en memoria: al recargar se vuelve a Inicio. */
export interface Sesion {
  id: string;
  tarjeta: Tarjeta;
  saludo: string;
  primeraPregunta: Pregunta;
  /** Respuesta a la pregunta 6: de ahí salen las horas libres (spec 6). */
  respuesta6: string | null;
  /** Pasaporte tal como lo devolvió POST /pasaporte; los índices de fortalezas son los de esta lista. */
  pasaporte: Pasaporte | null;
}

interface Contexto {
  sesion: Sesion | null;
  iniciar: (tarjeta: Tarjeta) => Promise<void>;
  actualizar: (cambios: Partial<Sesion>) => void;
}

const ContextoSesion = createContext<Contexto | null>(null);

export function ProveedorSesion({ children }: { children: ReactNode }) {
  const [sesion, setSesion] = useState<Sesion | null>(null);

  async function iniciar(tarjeta: Tarjeta) {
    const creada = await api.crearSesion(tarjeta.origen);
    setSesion({
      id: creada.sesion_id,
      tarjeta,
      saludo: creada.saludo,
      primeraPregunta: creada.pregunta,
      respuesta6: null,
      pasaporte: null,
    });
  }

  function actualizar(cambios: Partial<Sesion>) {
    setSesion((actual) => (actual ? { ...actual, ...cambios } : actual));
  }

  return <ContextoSesion.Provider value={{ sesion, iniciar, actualizar }}>{children}</ContextoSesion.Provider>;
}

export function useSesion(): Contexto {
  const contexto = useContext(ContextoSesion);
  if (!contexto) throw new Error("useSesion fuera de ProveedorSesion");
  return contexto;
}
