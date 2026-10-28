import { TEXTOS } from "../textos";

/** 6 segmentos, uno por pregunta (HU-02). */
export function BarraProgreso({ actual }: { actual: number }) {
  return (
    <div className="barra-progreso" role="img" aria-label={TEXTOS.chat.progreso(actual)}>
      {[1, 2, 3, 4, 5, 6].map((n) => (
        <span key={n} className={n <= actual ? "lleno" : ""} />
      ))}
    </div>
  );
}
