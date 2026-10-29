import { Link, Navigate } from "react-router";
import competencias from "../../data/competencias.json";
import { fechaCorta } from "../fecha";
import { useSesion } from "../sesion";
import { TEXTOS } from "../textos";
import { useRuta } from "../useRuta";
import { Sello, type Icono } from "../componentes/Sello";

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

  function sellosDeDestino(codigosTienes: string[], faltan: { codigo: string; etiqueta: string }[]) {
    const vistos = new Set<string>();
    const sellos: { icono: Icono; etiqueta: string; falta: boolean }[] = [];

    for (const codigo of codigosTienes) {
      const sello = sesion.pasaporte?.sellos.find((s) => s.codigo === codigo);
      if (sello && !vistos.has(sello.etiqueta)) {
        vistos.add(sello.etiqueta);
        sellos.push({ icono: sello.icono as Icono, etiqueta: sello.etiqueta, falta: false });
      }
    }

    for (const f of faltan) {
      if (vistos.has(f.etiqueta)) continue;
      vistos.add(f.etiqueta);
      const comp = competencias.find((c) => c.codigo === f.codigo);
      sellos.push({ icono: (comp?.sello.icono ?? "caja") as Icono, etiqueta: f.etiqueta, falta: true });
    }

    return sellos;
  }

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
                  {i === 0 && <span className="etiqueta-mejor">{T.mejorOpcion}</span>}
                  <strong>{d.nombre}</strong>
                  <span>{T.tienes(d.tienes.length, total)}</span>
                  <div className="fila-sellos">
                    {sellosDeDestino(d.tienes, d.faltan).map((s) => (
                      <Sello key={s.etiqueta} icono={s.icono} etiqueta={s.etiqueta} falta={s.falta} tamano={44} />
                    ))}
                  </div>
                  <span style={{ color }}>{d.faltan.length ? T.faltan(d.faltan.length) : TEXTOS.destino.nadaFalta}</span>
                  <span className="atenuado">{T.avisos(d.avisos_lima, fecha, d.avisos_parecidos)}</span>
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
          {ruta.destinos[0] && (
            <div className="explicacion-primero">
              <h3>{T.porQuePrimero(ruta.destinos[0].nombre)}</h3>
              {[
                { etiqueta: T.barraSellos, valor: Math.round(ruta.destinos[0].cobertura * 60), max: 60 },
                { etiqueta: T.barraInteres, valor: Math.round(ruta.destinos[0].interes * 25), max: 25 },
                { etiqueta: T.barraAvisos, valor: Math.round(ruta.destinos[0].demanda * 15), max: 15 },
              ].map((b) => (
                <div key={b.etiqueta} className="barra-item">
                  <div className="barra-cabecera">
                    <span>{b.etiqueta}</span>
                    <span>{b.valor} de {b.max}</span>
                  </div>
                  <div className="barra-fondo" role="progressbar" aria-valuenow={b.valor} aria-valuemin={0} aria-valuemax={b.max}>
                    <div className="barra-relleno" style={{ width: `${(b.valor / b.max) * 100}%` }} />
                  </div>
                </div>
              ))}
              <p className="barra-total">{T.total(Math.round(ruta.destinos[0].cobertura * 60 + ruta.destinos[0].interes * 25 + ruta.destinos[0].demanda * 15))}</p>
            </div>
          )}
          <p className="nota">{T.fuentes}</p>
        </aside>
      </div>
    </main>
  );
}
