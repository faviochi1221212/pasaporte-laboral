import { useState } from "react";
import { Link, Navigate } from "react-router";
import { api, type Pasaporte as PasaporteApi } from "../api";
import { agrupar, Pasaporte } from "../componentes/Pasaporte";
import { useSesion } from "../sesion";
import { TEXTOS } from "../textos";

const T = TEXTOS.pasaporte;

/** Compara dos textos sin mayúsculas, sin espacios al inicio/final y sin punto final. */
function mismos(a: string, b: string): boolean {
  const n = (s: string) => s.trim().toLowerCase().replace(/\.$/, "");
  return n(a) === n(b);
}

/** Pasaporte (HU-04): sellos agrupados, la frase al tocar, quitar y deshacer con PUT /pasaporte. */
export function PantallaPasaporte() {
  const { sesion } = useSesion();
  const original = sesion?.pasaporte ?? null;
  const [visible, setVisible] = useState<PasaporteApi | null>(original);
  const [quitados, setQuitados] = useState<string[]>([]);
  const [fortalezasQuitadas, setFortalezasQuitadas] = useState<number[]>([]);
  const [elegido, setElegido] = useState<string | null>(null);
  const [error, setError] = useState(false);

  if (!sesion || !original || !visible) return <Navigate to="/" replace />;
  const id = sesion.id;

  /** PUT con la lista completa de lo quitado: así quitar se puede deshacer (spec 6). */
  async function guardar(codigos: string[], indices: number[]) {
    setError(false);
    try {
      setVisible(await api.editarPasaporte(id, codigos, indices));
      setQuitados(codigos);
      setFortalezasQuitadas(indices);
    } catch {
      setError(true);
    }
  }

  const grupos = agrupar(visible.sellos);
  const visibles = new Set(visible.sellos.map((s) => s.codigo));
  const gruposQuitados = agrupar(original.sellos.filter((s) => !visibles.has(s.codigo)));
  const seleccion = grupos.find((g) => g.etiqueta === elegido) ?? grupos[0] ?? null;

  if (original.sellos.length === 0) {
    return (
      <main className="pagina">
        <h1>{T.titulo}</h1>
        <p className="texto">{T.sinSellos}</p>
        <Link className="boton" to="/">
          {T.empezar}
        </Link>
      </main>
    );
  }

  return (
    <main className="pagina">
      <div className="columnas">
        <Pasaporte
          titular={sesion.tarjeta.nombre}
          ilustracion={sesion.tarjeta.ilustracion}
          grupos={grupos}
          elegido={seleccion?.etiqueta ?? null}
          alElegir={setElegido}
        />

        <section className="pasaporte-detalle">
          <h1 className="titulo-grande">{T.titulo}</h1>
          <p className="subtitulo">{T.resumen(grupos.length)}</p>

          {seleccion && (
            <div className="tarjeta frase">
              <span className="atenuado">{T.porQue(seleccion.etiqueta)}</span>
              <q>{seleccion.evidencia}</q>
              <button
                type="button"
                className="boton boton-secundario"
                onClick={() => void guardar([...quitados, ...seleccion.codigos], fortalezasQuitadas)}
              >
                {T.quitarSello}
              </button>
            </div>
          )}

          {gruposQuitados.length > 0 && (
            <div className="quitados">
              <span className="atenuado">{T.quitados}</span>
              {gruposQuitados.map((g) => (
                <button
                  key={g.etiqueta}
                  type="button"
                  className="boton boton-secundario"
                  onClick={() => void guardar(quitados.filter((c) => !g.codigos.includes(c)), fortalezasQuitadas)}
                >
                  {T.deshacer(g.etiqueta)}
                </button>
              ))}
            </div>
          )}

          {original.fortalezas.length > 0 && (
            <div className="tarjeta">
              <h2>{T.fortalezas}</h2>
              <p className="atenuado">{T.fortalezasDetalle}</p>
              <ul className="fortalezas">
                {original.fortalezas.map((f, i) =>
                  fortalezasQuitadas.includes(i) ? (
                    <li key={i} className="quitada">
                      <span>{f.texto}</span>
                      <button
                        type="button"
                        className="boton boton-secundario"
                        onClick={() => void guardar(quitados, fortalezasQuitadas.filter((x) => x !== i))}
                      >
                        {T.deshacer(f.texto)}
                      </button>
                    </li>
                  ) : (
                    <li key={i}>
                      <span>
                        {f.texto}
                        {!mismos(f.texto, f.evidencia) && <> · <q>{f.evidencia}</q></>}
                      </span>
                      <button
                        type="button"
                        className="boton boton-secundario"
                        onClick={() => void guardar(quitados, [...fortalezasQuitadas, i])}
                      >
                        {T.quitar}
                      </button>
                    </li>
                  ),
                )}
              </ul>
            </div>
          )}

          {error && (
            <p role="alert" className="error">
              {TEXTOS.errorRed}
            </p>
          )}

          <Link className="boton boton-ancho" to="/intereses">
            {T.siguiente}
          </Link>
          <p className="nota">{T.pie}</p>
        </section>
      </div>
    </main>
  );
}
