import { useEffect, useRef, useState } from "react";
import { Link, Navigate, useParams } from "react-router";
import { api, type Cv as CvApi } from "../api";
import { useSesion } from "../sesion";
import { TEXTOS, TEXTOS_CV as T } from "../textos";

interface Contacto {
  nombre: string;
  distrito: string;
  telefono: string;
  correo: string;
}

/**
 * CV (HU-10, docs/mockup/cv_plantilla.md). Nombre y contacto viven solo en este estado de React:
 * nunca se envían a la API ni se guardan en el navegador.
 */
export function Cv() {
  const { sesion } = useSesion();
  const { codigo = "" } = useParams();
  const [cv, setCv] = useState<CvApi | "error" | null>(null);
  const [contacto, setContacto] = useState<Contacto>({ nombre: "", distrito: "", telefono: "", correo: "" });
  const [faltaNombre, setFaltaNombre] = useState(false);
  const campoNombre = useRef<HTMLInputElement>(null);
  const id = sesion?.id;

  useEffect(() => {
    if (!id) return;
    api.cv(id, codigo).then(setCv, () => setCv("error"));
  }, [id, codigo]);

  if (!sesion?.pasaporte) return <Navigate to="/" replace />;
  if (cv === "error") {
    return (
      <p role="alert" className="pagina error">
        {TEXTOS.errorRed}
      </p>
    );
  }
  if (!cv) return null;

  function cambiar(campo: keyof Contacto, valor: string) {
    setContacto((c) => ({ ...c, [campo]: valor }));
    if (campo === "nombre" && valor.trim()) setFaltaNombre(false);
  }

  function imprimir() {
    if (!contacto.nombre.trim()) {
      setFaltaNombre(true);
      campoNombre.current?.focus();
      return;
    }
    window.print();
  }

  const lineaContacto = [contacto.distrito, contacto.telefono, contacto.correo]
    .map((x) => x.trim())
    .filter(Boolean)
    .join(" | ");

  return (
    <main className="pagina pagina-cv">
      <div className="columnas">
        <section className="cv-datos no-imprimir">
          <Link to={`/destino/${codigo}`} className="volver">
            ← {T.volver}
          </Link>
          <h1 className="titulo-grande">{T.titulo}</h1>
          <p className="subtitulo">{T.detalle}</p>
          <form className="cv-formulario" onSubmit={(e) => e.preventDefault()}>
            <label>
              <span>
                {T.nombre} <span className="atenuado">{T.obligatorio}</span>
              </span>
              <input
                ref={campoNombre}
                value={contacto.nombre}
                autoComplete="off"
                aria-invalid={faltaNombre}
                onChange={(e) => cambiar("nombre", e.target.value)}
              />
            </label>
            {(["distrito", "telefono", "correo"] as const).map((campo) => (
              <label key={campo}>
                <span>
                  {T[campo]} <span className="atenuado">{T.opcional}</span>
                </span>
                <input
                  value={contacto[campo]}
                  autoComplete="off"
                  type={campo === "correo" ? "email" : campo === "telefono" ? "tel" : "text"}
                  onChange={(e) => cambiar(campo, e.target.value)}
                />
              </label>
            ))}
          </form>
          {faltaNombre && (
            <p role="alert" className="error">
              {T.faltaNombre}
            </p>
          )}
          <div className="tarjeta no-imprimir">
            <h2>{T.presentacionTitulo}</h2>
            <p>
              Hola, soy {contacto.nombre.trim() || "tu nombre"}. Tengo {cv.anios || "experiencia"} trabajando como{" "}
              {cv.puesto || "trabajador"}. Sé {cv.sellos.slice(0, 3).map((s) => s.etiqueta.toLowerCase()).join(", ")}
              {cv.curso ? ` y estoy por llevar el curso «${cv.curso.nombre}».` : "."} Quiero trabajar en {cv.destino}
              porque ya hago varias de las cosas que pide el puesto.
            </p>
            <button
              type="button"
              className="boton boton-secundario"
              onClick={() => {
                const texto = `Hola, soy ${contacto.nombre.trim() || "tu nombre"}. Tengo ${cv.anios || "experiencia"} trabajando como ${cv.puesto || "trabajador"}. Sé ${cv.sellos.slice(0, 3).map((s) => s.etiqueta.toLowerCase()).join(", ")}${cv.curso ? ` y estoy por llevar el curso «${cv.curso.nombre}».` : "."} Quiero trabajar en ${cv.destino} porque ya hago varias de las cosas que pide el puesto.`;
                navigator.clipboard.writeText(texto);
              }}
            >
              {T.copiar}
            </button>
          </div>
          <button type="button" className="boton boton-ancho" onClick={imprimir}>
            {T.imprimir}
          </button>
        </section>

        <article className="cv-hoja" aria-label={T.titulo}>
          <h2 className="cv-nombre">{contacto.nombre.trim().toUpperCase() || T.nombreVacio}</h2>
          {lineaContacto && <p className="cv-contacto">{lineaContacto}</p>}

          <h3>{T.tituloPerfil}</h3>
          <p>{cv.resumen}</p>

          <h3>{T.tituloExperiencia}</h3>
          {(cv.puesto || cv.anios) && (
            <p className="cv-puesto">
              <strong>{cv.puesto}</strong>
              <span>{cv.anios}</span>
            </p>
          )}
          <ul>
            {cv.sellos.map((s) => (
              <li key={s.etiqueta}>{s.texto_simple}</li>
            ))}
          </ul>

          <h3>{T.tituloSellos}</h3>
          <table className="cv-tabla">
            <tbody>
              {cv.sellos.map((s) => (
                <tr key={s.etiqueta}>
                  <th scope="row">{s.etiqueta}</th>
                  <td>{s.codigos.join(" · ")}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {cv.fortalezas.length > 0 && (
            <>
              <h3>{T.tituloFortalezas}</h3>
              <ul>
                {cv.fortalezas.map((f) => (
                  <li key={f.texto}>{f.texto}</li>
                ))}
              </ul>
            </>
          )}

          <h3>{T.tituloBusco}</h3>
          <p className="cv-busco">
            {T.busco(cv.destino)}
            {cv.curso && (
              <>
                <br />
                {T.curso(cv.curso.nombre, cv.curso.horas)}
              </>
            )}
          </p>

          <p className="cv-pie">{T.pie}</p>
        </article>
      </div>
    </main>
  );
}
