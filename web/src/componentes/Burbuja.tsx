import { useEffect, useRef, useState } from "react";

const MS_POR_LETRA = 35;
const MAXIMO_MS = 1500;
const PASO_MS = 30;

/** true si el sistema pide menos movimiento (spec 5b: entonces todo aparece de inmediato). */
export function movimientoReducido(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

interface BurbujaProps {
  de: "asistente" | "persona";
  texto: string;
  /** Si es true, el texto aparece de a poco (máx. 1,5 s) y tocar la burbuja lo muestra completo. */
  animar?: boolean;
  alTerminar?: () => void;
}

/** Burbuja del chat: asistente a la izquierda, persona a la derecha (spec 5b). */
export function Burbuja({ de, texto, animar = false, alTerminar }: BurbujaProps) {
  const [visibles, setVisibles] = useState(animar ? 0 : texto.length);
  const avisado = useRef(false);
  const completo = visibles >= texto.length;

  useEffect(() => {
    if (completo) return;
    const pasos = Math.max(1, Math.min(texto.length * MS_POR_LETRA, MAXIMO_MS) / PASO_MS);
    const porPaso = Math.ceil(texto.length / pasos);
    const intervalo = setInterval(() => setVisibles((v) => Math.min(texto.length, v + porPaso)), PASO_MS);
    return () => clearInterval(intervalo);
  }, [texto, completo]);

  useEffect(() => {
    if (visibles >= texto.length && !avisado.current) {
      avisado.current = true;
      alTerminar?.();
    }
  }, [visibles, texto.length, alTerminar]);

  return (
    <div
      className={`burbuja burbuja-${de}`}
      onClick={() => setVisibles(texto.length)}
      aria-live={de === "asistente" ? "polite" : undefined}
    >
      {texto.slice(0, visibles)}
    </div>
  );
}

export function Escribiendo({ texto }: { texto: string }) {
  return (
    <div className="burbuja burbuja-asistente burbuja-escribiendo" role="status">
      {texto}
    </div>
  );
}
