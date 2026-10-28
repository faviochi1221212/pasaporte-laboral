import { useEffect, useRef, useState } from "react";
import { Navigate, useNavigate } from "react-router";
import { api, ErrorApi } from "../api";
import { Sello } from "../componentes/Sello";
import { ORIGEN_EJEMPLO } from "../ejemplo";
import { useSinConexion } from "../Marco";
import { TARJETAS, useSesion } from "../sesion";
import { TEXTOS } from "../textos";

const T = TEXTOS.espera;

/** Espera (HU-04): "Armando tu pasaporte…" mientras corre la extracción completa. */
export function Espera() {
  const { sesion, actualizar, iniciar } = useSesion();
  const navegar = useNavigate();
  const sinConexion = useSinConexion();
  const [error, setError] = useState<{ mensaje: string; relatoNoLeido: boolean } | null>(null);
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
      const fallo = e instanceof ErrorApi ? e : null;
      setError({ mensaje: fallo?.message ?? TEXTOS.errorRed, relatoNoLeido: fallo?.codigo === "relato_no_leido" });
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

  /** Solo en respaldo (spec 7): sin conexión, el único relato con respuestas grabadas es el de María. */
  async function empezarConElEjemplo() {
    const tarjeta = TARJETAS.find((t) => t.origen === ORIGEN_EJEMPLO);
    if (!tarjeta) return;
    try {
      await iniciar(tarjeta);
      navegar("/conversacion", { replace: true });
    } catch {
      setError({ mensaje: TEXTOS.errorRed, relatoNoLeido: false });
    }
  }
  const soloEjemplo = sinConexion && error?.relatoNoLeido;

  return (
    <main className="pagina espera">
      <div className={error ? "" : "espera-sello"} aria-hidden="true">
        <Sello icono="registro" etiqueta="" color="#7A1F2B" tamano={120} />
      </div>
      {soloEjemplo ? (
        <>
          <h1 role="alert">{T.soloEjemplo}</h1>
          <button type="button" className="boton" onClick={() => void empezarConElEjemplo()}>
            {T.empezarEjemplo}
          </button>
        </>
      ) : error ? (
        <>
          <h1 role="alert">{error.mensaje}</h1>
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
