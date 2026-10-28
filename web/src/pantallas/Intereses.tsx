import { useState } from "react";
import { Navigate, useNavigate } from "react-router";
import { api, type Interes } from "../api";
import { horasDeRespuesta } from "../horas";
import { useSesion } from "../sesion";
import { TEXTOS } from "../textos";

const T = TEXTOS.intereses;
const ORDEN: Interes[] = ["gente", "cosas", "papeles"];

/** Intereses (HU-05): 3 botones; con las horas de la pregunta 6 se guardan las preferencias. */
export function Intereses() {
  const { sesion } = useSesion();
  const navegar = useNavigate();
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState(false);

  if (!sesion?.pasaporte) return <Navigate to="/" replace />;
  const { id, respuesta6 } = sesion;

  async function elegir(interes: Interes) {
    setOcupado(true);
    setError(false);
    try {
      await api.guardarPreferencias(id, interes, horasDeRespuesta(respuesta6 ?? ""));
      navegar("/ruta");
    } catch {
      setError(true);
      setOcupado(false);
    }
  }

  return (
    <main className="pagina">
      <div className="texto intereses">
        <h1 className="titulo-grande">{T.titulo}</h1>
        <p className="subtitulo">{T.detalle}</p>
        <div className="intereses-opciones">
          {ORDEN.map((interes) => {
            const [nombre, ejemplo] = T.opciones[interes];
            return (
              <button key={interes} type="button" className="interes" disabled={ocupado} onClick={() => void elegir(interes)}>
                <strong>{nombre}</strong>
                <span>{ejemplo}</span>
              </button>
            );
          })}
        </div>
        {error && (
          <p role="alert" className="error">
            {TEXTOS.errorRed}
          </p>
        )}
      </div>
    </main>
  );
}
