import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
import { FECHA_FOTO, MAS_AVISOS, TAREAS, TRABAJOS } from "../cifras";
import { Sello, type Icono } from "../componentes/Sello";
import { Trabajador, type Ilustracion } from "../componentes/Trabajador";
import { hayDictado } from "../dictado";
import { TARJETAS, useSesion, type Tarjeta } from "../sesion";
import { TEXTOS } from "../textos";

const T = TEXTOS.inicio;
// Ícono y color de cada paso de "Cómo funciona" (los colores de los sellos no cambian).
const PASOS: [Icono, string][] = [
  ["atencion", "#1C5FA8"],
  ["registro", "#1E7A46"],
  ["maleta", "#5B3E96"],
];
const PERSONAJES: Ilustracion[] = ["cajera", "almacen", "limpieza", "administrativo"];

/**
 * Inicio (HU-01): bloque rojo con el título y personajes, 6 tarjetas y "¿No está tu trabajo?".
 * Al tocar se crea la sesión sin pedir datos. Debajo, "Cómo funciona", las cifras y las fuentes de data/.
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
    <main className="inicio">
      <section className="inicio-portada">
        <div className="columnas inicio-portada-contenido">
          <div className="texto">
            <h1 className="titulo-grande">{T.titulo}</h1>
            <p className="subtitulo">{T.subtitulo}</p>
            <ul className="inicio-datos">
              <li>{T.minutos}</li>
              {hayDictado() && <li>{T.puedesHablar}</li>}
            </ul>
          </div>
          <div className="inicio-personajes" aria-hidden="true">
            {PERSONAJES.map((tipo) => (
              <Trabajador key={tipo} tipo={tipo} tamano={120} />
            ))}
          </div>
        </div>
      </section>

      <div className="pagina">
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
            {T.pasos.map(([paso, frase], i) => {
              const [icono, color] = PASOS[i] ?? PASOS[0]!;
              return (
                <li key={paso}>
                  <span aria-hidden="true">
                    <Sello icono={icono} etiqueta={paso} color={color} giro={i % 2 ? 6 : -6} tamano={56} />
                  </span>
                  <div>
                    <strong>{paso}</strong>
                    <p>{frase}</p>
                  </div>
                </li>
              );
            })}
          </ol>
        </section>

        <ul className="inicio-cifras">
          <li>
            <strong>{TRABAJOS}</strong> {T.cifras.trabajos}
          </li>
          <li>
            <strong>{TAREAS}</strong> {T.cifras.tareas}
          </li>
          <li>
            <strong>{MAS_AVISOS.avisos}</strong> {T.cifras.avisos(MAS_AVISOS.nombre, FECHA_FOTO)}
          </li>
        </ul>

        <p className="inicio-fuentes">{T.fuentes(FECHA_FOTO)}</p>
      </div>
    </main>
  );
}
