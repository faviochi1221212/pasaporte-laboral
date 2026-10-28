import { useEffect, useState } from "react";
import { api, type Ruta } from "./api";

/** Pide la ruta de la sesión (GET /ruta); null mientras carga, "error" si falla. */
export function useRuta(id: string | undefined): Ruta | null | "error" {
  const [ruta, setRuta] = useState<Ruta | null | "error">(null);
  useEffect(() => {
    if (!id) return;
    api.ruta(id).then(setRuta, () => setRuta("error"));
  }, [id]);
  return ruta;
}
