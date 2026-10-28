import { Link, Navigate, useParams } from "react-router";
import { Sello } from "../componentes/Sello";
import { fechaCorta } from "../fecha";
import { useSesion } from "../sesion";
import { TEXTOS } from "../textos";
import { useRuta } from "../useRuta";

const T = TEXTOS.destino;

/** Destino (HU-07): en orden, lo que ya haces y sirve, qué harías, lo que te falta y avisos (spec 6). */
export function Destino() {
  const { sesion } = useSesion();
  const { codigo } = useParams();
  const ruta = useRuta(sesion?.id);

  if (!sesion?.pasaporte) return <Navigate to="/" replace />;
  if (ruta === "error") {
    return (
      <p role="alert" className="pagina error">
        {TEXTOS.errorRed}
      </p>
    );
  }
  if (!ruta) return null;
  const destino = ruta.destinos.find((d) => d.codigo === codigo);
  if (!destino) return <Navigate to="/ruta" replace />;
  const sellos = new Map(sesion.pasaporte.sellos.map((s) => [s.codigo, s]));
  const avisos = TEXTOS.ruta.avisos(destino.avisos_lima, fechaCorta(ruta.foto), destino.avisos_parecidos);

  return (
    <main className="pagina destino">
      <Link to="/ruta" className="volver">
        ← {T.volver}
      </Link>
      <header className="destino-cabecera">
        <span className="etiqueta-chica">{T.proxima}</span>
        <h1>{destino.nombre}</h1>
        <span>{avisos}</span>
      </header>

      <div className="columnas">
        <div className="destino-columna">
          <section className="tarjeta">
            <h2>{T.yaHaces}</h2>
            <ul className="lista-sellos">
              {destino.tienes.map((c) => {
                const s = sellos.get(c);
                if (!s) return null;
                return (
                  <li key={c}>
                    <Sello icono={s.icono} etiqueta={s.etiqueta} color="#1E7A46" tamano={56} />
                    <div>
                      <strong>{s.etiqueta}</strong>
                      <q>{s.evidencia}</q>
                    </div>
                  </li>
                );
              })}
            </ul>
          </section>

          <section className="tarjeta">
            <h2>{T.queHarias}</h2>
            <ul className="lista-simple">
              {destino.que_harias.map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
          </section>
        </div>

        <div className="destino-columna">
          <section className="tarjeta">
            <h2>{T.teFalta}</h2>
            {destino.faltan.length === 0 ? (
              <p>{T.nadaFalta}</p>
            ) : (
              <>
                <p className="atenuado">{T.teFaltaDetalle}</p>
                <ul className="faltantes">
                  {destino.faltan.map((f) => (
                    <li key={f.codigo}>
                      <strong>{f.etiqueta}</strong>
                      {f.curso ? (
                        <div className="curso">
                          <span>{f.curso.nombre}</span>
                          <span className="atenuado">
                            {T.horas(f.curso.horas)} · {T.semanas(f.curso.semanas)}
                          </span>
                          <span>{f.curso.alcance === "solo_teoria" ? T.teorica(f.curso.modulo) : f.curso.se_lleva}</span>
                          <a href={f.curso.url} target="_blank" rel="noreferrer">
                            {T.verCurso}
                          </a>
                        </div>
                      ) : (
                        <span className="atenuado">{f.mensaje}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </>
            )}
          </section>

          <section className="tarjeta">
            <h2>{T.avisos}</h2>
            {destino.avisos_lima > 0 ? (
              <>
                <p>{avisos}</p>
                <Link className="boton boton-ancho" to={`/avisos/${destino.codigo}`}>
                  {T.verAvisos}
                </Link>
              </>
            ) : (
              <p>{T.sinAvisos}</p>
            )}
          </section>

          <Link className="boton boton-secundario boton-ancho" to={`/cv/${destino.codigo}`}>
            {T.miCv}
          </Link>
        </div>
      </div>
    </main>
  );
}
