import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
// La fecha de la foto se lee al compilar: después de actualizar data/ hay que correr npm run build.
import demanda from "../../../data/demanda.json";
import { Sello, type Icono } from "../componentes/Sello";
import { Trabajador } from "../componentes/Trabajador";
import { hayDictado } from "../dictado";
import { fechaConAnio } from "../fecha";
import { TARJETAS, useSesion, type Tarjeta } from "../sesion";
import { TEXTOS } from "../textos";

const T = TEXTOS.inicio;
// Ícono y color de cada paso de "Cómo funciona", con los mismos colores que los sellos de la portada.
const PASOS: [Icono, string][] = [
  ["atencion", "#1C5FA8"],
  ["registro", "#1E7A46"],
  ["maleta", "#5B3E96"],
];

/**
 * Inicio (HU-01): 6 tarjetas y "¿No está tu trabajo?". Al tocar se crea la sesión sin pedir datos.
 * Debajo, "Cómo funciona" en 3 pasos y las fuentes de los datos.
 */
export function Inicio() {
  const { iniciar } = useSesion();
  const navegar = useNavigate();
  const [otro, setOtro] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState(false);

  async function elegir(tarjeta: Tarjeta) {
    setOcupado(true);
    setError(false);
    try {
      await iniciar(tarjeta);
      navegar("/conversacion");
    } catch {
      setError(true);
      setOcupado(false);
    }
  }

  function continuarConOtro(evento: FormEvent) {
    evento.preventDefault();
    if (otro.trim()) void elegir({ nombre: otro.trim(), origen: null, ilustracion: "todo" });
  }

  return (
    <main className="pagina inicio">
      <section className="columnas inicio-portada">
        <div className="texto">
          <h1 className="titulo-grande">{T.titulo}</h1>
          <p className="subtitulo">{T.subtitulo}</p>
          <ul className="inicio-datos">
            <li>{T.minutos}</li>
            {hayDictado() && <li>{T.puedesHablar}</li>}
          </ul>
        </div>
        <div className="inicio-sellos" aria-hidden="true">
          <Sello icono="caja" etiqueta={T.sellosDecorativos[0] ?? ""} color="#1C5FA8" giro={-10} tamano={110} />
          <Sello icono="atencion" etiqueta={T.sellosDecorativos[1] ?? ""} color="#1E7A46" giro={8} tamano={110} />
          <Sello icono="mercaderia" etiqueta={T.sellosDecorativos[2] ?? ""} color="#5B3E96" giro={-4} tamano={110} />
        </div>
      </section>

      <section className="inicio-elegir">
        <h2>{T.pregunta}</h2>
        <div className="tarjetas">
          {TARJETAS.map((t) => (
            <button key={t.nombre} type="button" className="tarjeta-trabajo" disabled={ocupado} onClick={() => void elegir(t)}>
              <Trabajador tipo={t.ilustracion} tamano={84} />
              <span>{t.nombre}</span>
            </button>
          ))}
        </div>
        <form className="inicio-otro" onSubmit={continuarConOtro}>
          <label htmlFor="otro">{T.otro}</label>
          <div className="campo-con-boton">
            <input
              id="otro"
              value={otro}
              placeholder={T.otroEjemplo}
              onChange={(e) => setOtro(e.target.value)}
              disabled={ocupado}
            />
            <button type="submit" className="boton boton-cuadrado" aria-label={T.otroContinuar} disabled={ocupado || !otro.trim()}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </button>
          </div>
        </form>
        {error && <p role="alert" className="error">{TEXTOS.errorRed}</p>}
      </section>

      <section className="como-funciona">
        <h2>{T.comoFunciona}</h2>
        <ol>
          {T.pasos.map((paso, i) => {
            const [icono, color] = PASOS[i] ?? PASOS[0]!;
            return (
              <li key={paso}>
                <span aria-hidden="true">
                  <Sello icono={icono} etiqueta={paso} color={color} giro={i % 2 ? 6 : -6} tamano={56} />
                </span>
                {paso}
              </li>
            );
          })}
        </ol>
      </section>

      <p className="inicio-fuentes">{T.fuentes(fechaConAnio(demanda.tomado))}</p>
    </main>
  );
}
