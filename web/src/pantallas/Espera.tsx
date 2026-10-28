import { useEffect, useRef, useState } from "react";
import { Navigate, useNavigate } from "react-router";
import { api, ErrorApi } from "../api";
import { Sello } from "../componentes/Sello";
import { useSesion } from "../sesion";
import { TEXTOS } from "../textos";

const T = TEXTOS.espera;

/** Espera (HU-04): "Armando tu pasaporte…" mientras corre la extracción completa. */
export function Espera() {
  const { sesion, actualizar } = useSesion();
  const navegar = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const pidiendo = useRef(false);

  async function armar(id: string) {
    if (pidiendo.current) return;
    pidiendo.current = true;
    setError(null);
    try {
      actualizar({ pasaporte: await api.armarPasaporte(id) });
      navegar("/pasaporte", { replace: true });
    } catch (e) {
      // Si no se pudo leer el relato, la API manda el texto fijo de la spec 5.
      setError(e instanceof ErrorApi ? e.message : TEXTOS.errorRed);
    } finally {
      pidiendo.current = false;
    }
  }

  // Una sola vez al llegar; `pidiendo` evita una segunda llamada si el efecto se repite.
  const id = sesion?.id;
  useEffect(() => {
    if (id) void armar(id);
  }, [id]);

  if (!sesion) return <Navigate to="/" replace />;

  return (
    <main className="pagina espera">
      <div className={error ? "" : "espera-sello"} aria-hidden="true">
        <Sello icono="registro" etiqueta="" color="#7A1F2B" tamano={120} />
      </div>
      {error ? (
        <>
          <h1 role="alert">{error}</h1>
          <button type="button" className="boton" onClick={() => void armar(sesion.id)}>
            {T.reintentar}
          </button>
        </>
      ) : (
        <>
          <h1 role="status">{T.titulo}</h1>
          <p className="atenuado texto">{T.detalle}</p>
        </>
      )}
    </main>
  );
}
