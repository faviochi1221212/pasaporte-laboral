import { Link, Navigate } from "react-router";
import { fechaCorta } from "../fecha";
import { useSesion } from "../sesion";
import { TEXTOS } from "../textos";
import { useRuta } from "../useRuta";

const T = TEXTOS.ruta;
const COLORES_LINEA = ["#1E7A46", "#1C5FA8", "#5B3E96"];

/** Ruta (HU-06): hasta 3 destinos de mayor a menor puntaje; cada parada es un sello que falta. */
export function Ruta() {
  const { sesion } = useSesion();
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
  const fecha = fechaCorta(ruta.foto);

  return (
    <main className="pagina">
      <h1 className="titulo-grande">{T.titulo}</h1>
      <p className="subtitulo">{T.detalle}</p>
      <div className="columnas">
        <section className="mapa" aria-label={T.titulo}>
          <div className="mapa-origen">
            <span className="mapa-punto" aria-hidden="true" />
            <div>
              <span className="etiqueta-chica">{T.estasAqui}</span>
              <strong>{sesion.tarjeta.nombre}</strong>
            </div>
          </div>
          {ruta.destinos.map((d, i) => {
            const color = COLORES_LINEA[i % COLORES_LINEA.length];
            const total = d.tienes.length + d.faltan.length;
            return (
              <div key={d.codigo} className="mapa-linea" style={{ borderColor: color }}>
                <ol className="mapa-paradas" aria-hidden="true">
                  {d.faltan.map((f) => (
                    <li key={f.codigo} style={{ borderColor: color }} />
                  ))}
                </ol>
                <Link
                  to={`/destino/${d.codigo}`}
                  className={`estacion${i === 0 ? " estacion-primera" : ""}`}
                  style={{ borderColor: color }}
                  aria-label={T.estacion(d.nombre)}
                >
                  <strong>{d.nombre}</strong>
                  <span>{T.tienes(d.tienes.length, total)}</span>
                  <span style={{ color }}>{d.faltan.length ? T.faltan(d.faltan.length) : TEXTOS.destino.nadaFalta}</span>
                  <span className="atenuado">{T.avisos(d.avisos_lima, fecha)}</span>
                </Link>
              </div>
            );
          })}
          {ruta.destinos.length < 3 && (
            <div className="tarjeta">
              <p>{T.pocos}</p>
              <Link className="boton boton-secundario" to="/conversacion">
                {T.volverAContar}
              </Link>
            </div>
          )}
        </section>
        <aside className="tarjeta texto">
          <h2>{T.porQueTitulo}</h2>
          <p>{T.porQue}</p>
          <p className="nota">{T.fuentes}</p>
        </aside>
      </div>
    </main>
  );
}
