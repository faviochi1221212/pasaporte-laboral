import { useEffect, useState } from "react";
import { Link, Navigate, useParams } from "react-router";
import { api, type Avisos as AvisosApi } from "../api";
import { fechaCorta } from "../fecha";
import { useSesion } from "../sesion";
import { TEXTOS } from "../textos";
import { useRuta } from "../useRuta";

const T = TEXTOS.avisos;

/** Avisos (HU-09): hasta 3 avisos reales; el botón abre el aviso en Empleos Perú. */
export function Avisos() {
  const { sesion } = useSesion();
  const { codigo = "" } = useParams();
  const ruta = useRuta(sesion?.id);
  const [avisos, setAvisos] = useState<AvisosApi | "error" | null>(null);
  const id = sesion?.id;

  useEffect(() => {
    if (!id) return;
    setAvisos(null);
    api.avisos(id, codigo).then(setAvisos, () => setAvisos("error"));
  }, [id, codigo]);

  if (!sesion?.pasaporte) return <Navigate to="/" replace />;
  if (avisos === "error") {
    return (
      <p role="alert" className="pagina error">
        {TEXTOS.errorRed}
      </p>
    );
  }
  if (!avisos) return null;
  const destino = ruta && ruta !== "error" ? ruta.destinos.find((d) => d.codigo === codigo) : undefined;
  const foto = ruta && ruta !== "error" ? fechaCorta(ruta.foto) : null;

  return (
    <main className="pagina">
      <Link to={destino ? `/destino/${codigo}` : "/ruta"} className="volver">
        ← {destino ? T.volver : TEXTOS.destino.volver}
      </Link>
      <h1 className="titulo-grande">{T.titulo}</h1>
      {destino && <p className="subtitulo">{destino.nombre}</p>}

      {avisos.mensaje ? (
        <p className="tarjeta">{avisos.mensaje}</p>
      ) : (
        <div className="avisos">
          {avisos.avisos.map((a) => (
            <article key={a.id} className="tarjeta aviso">
              <h2>{a.titulo}</h2>
              <p className="aviso-empresa">
                {a.empresa} · {a.distrito}
              </p>
              {a.nota && <p className="aviso-nota">{a.nota}</p>}
              <p className="aviso-datos">
                <span>{a.sueldo ? `${T.sueldo}: ${a.sueldo}` : T.sinSueldo}</span>
                <span>{T.cierre(fechaCorta(a.cierre))}</span>
              </p>
              <h3>{T.quePiden}</h3>
              <ul className="lista-simple">
                {a.que_piden.map((q) => (
                  <li key={q}>{q}</li>
                ))}
              </ul>
              <a className="boton boton-ancho" href={a.url} target="_blank" rel="noreferrer">
                {T.ver} <span className="solo-lector">{T.abreEnOtra}</span>
              </a>
            </article>
          ))}
        </div>
      )}
      {foto && <p className="nota">{T.fuente(foto)}</p>}

      {destino && (
        <section className="tarjeta otros-portales">
          <h2>{T.otrosPortales}</h2>
          <div className="fila-botones">
            {(() => {
              const q = destino.nombre.toLowerCase().replace(/\s+/g, "-");
              const qEnc = encodeURIComponent(destino.nombre.toLowerCase());
              return (
                <>
                  <a className="boton boton-secundario" href={`https://pe.computrabajo.com/trabajo-de-${q}`} target="_blank" rel="noopener">
                    Computrabajo
                  </a>
                  <a className="boton boton-secundario" href={`https://www.bumeran.com.pe/empleos-busqueda-${q}.html`} target="_blank" rel="noopener">
                    Bumeran
                  </a>
                  <a className="boton boton-secundario" href={`https://www.linkedin.com/jobs/search/?keywords=${qEnc}&location=Lima`} target="_blank" rel="noopener">
                    LinkedIn
                  </a>
                </>
              );
            })()}
          </div>
        </section>
      )}
    </main>
  );
}
