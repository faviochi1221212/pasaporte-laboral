import { useEffect, useRef, useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router";
import { api, type Pregunta, type SellosParciales } from "../api";
import { BarraProgreso } from "../componentes/BarraProgreso";
import { Burbuja, Escribiendo, movimientoReducido } from "../componentes/Burbuja";
import { dictar, hayDictado, type Reconocedor } from "../dictado";
import { respuestaDeEjemplo } from "../ejemplo";
import { useSinConexion } from "../Marco";
import { useSesion } from "../sesion";
import { TEXTOS } from "../textos";

const T = TEXTOS.chat;
const PAUSA_ESCRIBIENDO_MS = 700;

interface Mensaje {
  id: number;
  de: "asistente" | "persona";
  texto: string;
  /** Número de pregunta a la que pertenece (para el botón Atrás). */
  n?: number;
  animar: boolean;
}

interface Decir {
  texto: string;
  n?: number;
}

const esperar = (ms: number) => new Promise((listo) => setTimeout(listo, ms));

/** Conversación en formato chat (spec 5b, HU-02 y HU-16). */
export function Conversacion() {
  const { sesion, actualizar } = useSesion();
  const navegar = useNavigate();
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [escribiendo, setEscribiendo] = useState(false);
  const [abierta, setAbierta] = useState<Pregunta | null>(null);
  const [enRepregunta, setEnRepregunta] = useState(false);
  const sinConexion = useSinConexion();
  const [campo, setCampo] = useState("");
  const [sellos, setSellos] = useState<SellosParciales | null>(null);
  const [error, setError] = useState(false);
  const [escuchando, setEscuchando] = useState(false);
  const contador = useRef(0);
  const finales = useRef(new Map<number, () => void>());
  const preguntas = useRef(new Map<number, Pregunta>());
  const iniciado = useRef(false);
  const reconocedor = useRef<Reconocedor | null>(null);
  const fondo = useRef<HTMLDivElement>(null);
  const reducido = movimientoReducido();

  /** El asistente dice cada texto en orden: "escribiendo…" ~700 ms y luego el texto de a poco. */
  async function decir(textos: Decir[]) {
    for (const t of textos) {
      if (!reducido) {
        setEscribiendo(true);
        await esperar(PAUSA_ESCRIBIENDO_MS);
        setEscribiendo(false);
      }
      const id = ++contador.current;
      const termino = new Promise<void>((listo) => finales.current.set(id, listo));
      setMensajes((m) => [...m, { id, de: "asistente", texto: t.texto, n: t.n, animar: !reducido }]);
      await termino;
    }
  }

  useEffect(() => {
    if (!sesion || iniciado.current) return;
    iniciado.current = true;
    const primera = sesion.primeraPregunta;
    preguntas.current.set(primera.n, primera);
    void decir([{ texto: sesion.saludo }, { texto: primera.texto, n: primera.n }]).then(() => setAbierta(primera));
  }, [sesion]);

  useEffect(() => {
    fondo.current?.scrollIntoView({ block: "end", behavior: reducido ? "auto" : "smooth" });
  }, [mensajes, escribiendo, abierta, reducido]);

  if (!sesion) return <Navigate to="/" replace />;
  const id = sesion.id;

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    const texto = campo.trim();
    if (!abierta || !texto) return;
    const pregunta = abierta;
    setAbierta(null);
    setCampo("");
    setError(false);
    const propio = ++contador.current;
    setMensajes((m) => [...m, { id: propio, de: "persona", texto, n: pregunta.n, animar: false }]);
    setEscribiendo(true);
    let turno;
    try {
      turno = await api.responder(id, pregunta.n, texto);
    } catch {
      setEscribiendo(false);
      setMensajes((m) => m.filter((x) => x.id !== propio));
      setCampo(texto);
      setError(true);
      setAbierta(pregunta);
      return;
    }
    setEscribiendo(false);
    if (turno.parcial_listo) {
      // Sin esperar: si falla, el contador no cambia y no se muestra ningún error (A13).
      api.sellosParciales(id).then(setSellos, () => undefined);
    }
    if (turno.tipo === "fin" || !turno.pregunta) {
      await decir([{ texto: turno.cierre ?? "" }]);
      actualizar({ respuesta6: texto });
      navegar("/espera");
      return;
    }
    const siguiente = turno.pregunta;
    if (turno.tipo === "siguiente") preguntas.current.set(siguiente.n, siguiente);
    // Una sola burbuja: la reacción en la primera línea y la pregunta debajo (spec 5b).
    const burbuja = turno.reaccion ? `${turno.reaccion}\n${siguiente.texto}` : siguiente.texto;
    await decir([{ texto: burbuja, n: siguiente.n }]);
    setEnRepregunta(turno.tipo === "repregunta");
    setAbierta(siguiente);
  }

  /** Atrás: vuelve a abrir la pregunta anterior; al responderla, la API borra esa respuesta y las siguientes. */
  function atras() {
    if (!abierta) return;
    const anterior = preguntas.current.get(abierta.n - 1);
    if (!anterior) {
      navegar("/");
      return;
    }
    setMensajes((m) => {
      const corte = m.findIndex((x) => x.de === "persona" && x.n === anterior.n);
      return corte < 0 ? m : m.slice(0, corte);
    });
    setEnRepregunta(false);
    setAbierta(anterior);
  }

  function agregar(texto: string) {
    setCampo((actual) => (actual.trim() ? `${actual.trim()}, ${texto}` : texto));
  }

  function hablar() {
    if (escuchando) {
      reconocedor.current?.stop();
      return;
    }
    reconocedor.current = dictar(agregar, () => setEscuchando(false));
    setEscuchando(reconocedor.current !== null);
  }

  // Solo en modo respaldo: la respuesta de María a esta pregunta o a su repregunta (spec 7).
  const ejemplo = abierta ? respuestaDeEjemplo(abierta.n, enRepregunta) : undefined;
  const actual = abierta?.n ?? Math.max(1, ...mensajes.filter((m) => m.n).map((m) => m.n ?? 1));

  return (
    <div className="chat">
      <header className="chat-cabecera">
        <button type="button" className="boton-icono" aria-label={TEXTOS.atras} onClick={atras} disabled={!abierta}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        <BarraProgreso actual={actual} />
        <span className="boton-icono" aria-hidden="true" />
      </header>

      <main className="chat-mensajes">
        {mensajes.map((m) => (
          <Burbuja
            key={m.id}
            de={m.de}
            texto={m.texto}
            animar={m.animar}
            alTerminar={() => finales.current.get(m.id)?.()}
          />
        ))}
        {escribiendo && <Escribiendo texto={T.escribiendo} />}
        {abierta && abierta.ejemplos.length > 0 && (
          <div className="ejemplos">
            {abierta.ejemplos.map((e) => (
              <button key={e} type="button" className="ejemplo" onClick={() => agregar(e)}>
                {e}
              </button>
            ))}
          </div>
        )}
        {sinConexion && ejemplo && (
          <button type="button" className="boton boton-secundario usar-ejemplo" onClick={() => setCampo(ejemplo)}>
            {T.usarEjemplo}
          </button>
        )}
        {error && (
          <p role="alert" className="error">
            {TEXTOS.errorRed}
          </p>
        )}
        <div ref={fondo} />
      </main>

      <footer className="chat-pie">
        {sellos && (
          <div className="chat-sellos" role="status">
            <span className="chat-sellos-marca" aria-hidden="true">
              {sellos.sellos_ganados}
            </span>
            <span>
              <strong>{T.sellosGanados(sellos.sellos_ganados)}</strong> · {T.sigueContando}
            </span>
          </div>
        )}
        <form className="chat-redactar" onSubmit={enviar} data-pregunta-abierta={abierta?.n}>
          <textarea
            aria-label={T.campo}
            placeholder={escuchando ? T.escuchando : T.campoEjemplo}
            value={campo}
            rows={2}
            disabled={!abierta}
            onChange={(e) => setCampo(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          {hayDictado() && (
            <button
              type="button"
              className={`boton boton-secundario boton-cuadrado${escuchando ? " escuchando" : ""}`}
              aria-label={T.hablar}
              aria-pressed={escuchando}
              onClick={hablar}
              disabled={!abierta}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <rect x="9" y="3" width="6" height="11" rx="3" />
                <path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
              </svg>
            </button>
          )}
          <button type="submit" className="boton boton-cuadrado" aria-label={T.enviar} disabled={!abierta || !campo.trim()}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </button>
        </form>
      </footer>
    </div>
  );
}
