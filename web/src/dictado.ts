// Dictado del navegador (Web Speech API, HU-03): la voz no sale del dispositivo, solo llega texto.

interface ResultadoDictado {
  results: ArrayLike<ArrayLike<{ transcript: string }>>;
}

export interface Reconocedor {
  lang: string;
  interimResults: boolean;
  onresult: ((evento: ResultadoDictado) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  start: () => void;
  stop: () => void;
}

type ConstructorReconocedor = new () => Reconocedor;

function constructorDictado(): ConstructorReconocedor | null {
  const w = window as unknown as {
    SpeechRecognition?: ConstructorReconocedor;
    webkitSpeechRecognition?: ConstructorReconocedor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

/** Si el navegador no tiene dictado, el botón del micrófono no aparece. */
export function hayDictado(): boolean {
  return constructorDictado() !== null;
}

/** Empieza a escuchar en español del Perú y entrega el texto dictado. */
export function dictar(alTexto: (texto: string) => void, alTerminar: () => void): Reconocedor | null {
  const Constructor = constructorDictado();
  if (!Constructor) return null;
  const reconocedor = new Constructor();
  reconocedor.lang = "es-PE";
  reconocedor.interimResults = false;
  reconocedor.onresult = (evento) => {
    const texto = Array.from(evento.results)
      .map((r) => r[0]?.transcript ?? "")
      .join(" ")
      .trim();
    if (texto) alTexto(texto);
  };
  reconocedor.onend = alTerminar;
  reconocedor.onerror = alTerminar;
  reconocedor.start();
  return reconocedor;
}
