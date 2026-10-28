import type { Sello as SelloApi } from "../api";
import { TEXTOS } from "../textos";
import { Sello, type Icono } from "./Sello";
import { Trabajador, type Ilustracion } from "./Trabajador";

const COLORES = ["#1C5FA8", "#C8102E", "#1E7A46", "#5B3E96", "#B45309", "#0E7490"];
const GIROS = [-8, 6, -3, 9, -6, 5];

/** Sellos con la misma etiqueta, que se muestran juntos ("sirve en N trabajos", spec 6b caso 1). */
export interface GrupoSellos {
  etiqueta: string;
  icono: Icono;
  evidencia: string;
  codigos: string[];
}

/** Agrupa por etiqueta, en el orden en que llegaron. */
export function agrupar(sellos: SelloApi[]): GrupoSellos[] {
  const grupos = new Map<string, GrupoSellos>();
  for (const s of sellos) {
    const grupo = grupos.get(s.etiqueta);
    if (grupo) grupo.codigos.push(s.codigo);
    else grupos.set(s.etiqueta, { etiqueta: s.etiqueta, icono: s.icono, evidencia: s.evidencia, codigos: [s.codigo] });
  }
  return [...grupos.values()];
}

interface PasaporteProps {
  titular: string;
  ilustracion: Ilustracion;
  grupos: GrupoSellos[];
  elegido: string | null;
  alElegir: (etiqueta: string) => void;
}

/** Libreta del pasaporte: cabecera granate, titular y la grilla de sellos que se pueden tocar. */
export function Pasaporte({ titular, ilustracion, grupos, elegido, alElegir }: PasaporteProps) {
  const T = TEXTOS.pasaporte;
  return (
    <section className="libreta" aria-label={T.cabecera}>
      <div className="libreta-cabecera">
        <span>{T.cabecera}</span>
        <span>{T.pais}</span>
      </div>
      <div className="libreta-titular">
        <div className="libreta-foto">
          <Trabajador tipo={ilustracion} tamano={56} />
        </div>
        <div>
          <strong>{titular}</strong>
          <span>{T.loQueHaces}</span>
        </div>
      </div>
      <div className="libreta-sellos">
        {grupos.map((g, i) => {
          const varios = g.codigos.length > 1;
          return (
            <button
              key={g.etiqueta}
              type="button"
              className={`libreta-sello${g.etiqueta === elegido ? " elegido" : ""}`}
              aria-label={`Sello: ${g.etiqueta}${varios ? `, ${T.sirveEn(g.codigos.length)}` : ""}`}
              aria-pressed={g.etiqueta === elegido}
              onClick={() => alElegir(g.etiqueta)}
            >
              <Sello
                icono={g.icono}
                etiqueta={g.etiqueta}
                color={COLORES[i % COLORES.length]}
                giro={GIROS[i % GIROS.length]}
                tamano={100}
              />
              {varios && <span className="sirve-en">{T.sirveEn(g.codigos.length)}</span>}
            </button>
          );
        })}
      </div>
    </section>
  );
}
