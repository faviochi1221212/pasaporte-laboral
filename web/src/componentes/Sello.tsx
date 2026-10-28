import type { ReactElement } from "react";

/** Íconos válidos de los sellos (spec 3). */
export type Icono =
  | "caja"
  | "cobro"
  | "mercaderia"
  | "limpieza"
  | "revision"
  | "maleta"
  | "atencion"
  | "registro"
  | "habitacion"
  | "mesa";

// Trazos de 24 × 24. caja, cobro, mercaderia (inventario), atencion (reclamo) y registro (kardex)
// vienen de docs/mockup/Sello.dc.html; revision (lupa), limpieza, maleta, habitacion y mesa siguen
// el mismo estilo porque el mockup no los tiene.
const TRAZOS: Record<Icono, ReactElement> = {
  caja: (
    <g>
      <rect x="3" y="10" width="18" height="10" rx="1.5" />
      <rect x="6" y="4" width="9" height="6" rx="1" />
      <path d="M7 14h2M11 14h2M15 14h2M7 17h10" />
    </g>
  ),
  cobro: (
    <g>
      <ellipse cx="9" cy="7" rx="6" ry="3" />
      <path d="M3 7v4c0 1.7 2.7 3 6 3s6-1.3 6-3V7" />
      <path d="M9 14v3c0 1.7 2.7 3 6 3s6-1.3 6-3v-4c0-1.6-2.4-2.9-5.5-3" />
    </g>
  ),
  mercaderia: (
    <g>
      <path d="M3 9l9-5 9 5-9 5z" />
      <path d="M3 9v7l9 5 9-5V9M12 14v7" />
    </g>
  ),
  atencion: (
    <g>
      <path d="M4 5h16v11H9l-5 4z" />
      <path d="M9 10.5c1 1.3 5 1.3 6 0" />
    </g>
  ),
  registro: (
    <g>
      <rect x="5" y="4" width="14" height="17" rx="1.5" />
      <path d="M9 3h6v3H9zM8 11h2M12 11h4M8 15h2M12 15h4" />
    </g>
  ),
  revision: (
    <g>
      <circle cx="10" cy="10" r="6" />
      <path d="M14.5 14.5L21 21M7.5 10l1.8 1.8 3.2-3.3" />
    </g>
  ),
  limpieza: (
    <g>
      <path d="M8 21h8l1-10H7z" />
      <path d="M9 11V8h6v3M12 8V4h4" />
      <path d="M19 5l2-1M19 8h2M19 11l2 1" />
    </g>
  ),
  maleta: (
    <g>
      <rect x="3" y="8" width="18" height="12" rx="1.5" />
      <path d="M9 8V5h6v3M3 13h18M7 20v1M17 20v1" />
    </g>
  ),
  habitacion: (
    <g>
      <path d="M3 18V7M3 14h18v4M21 14v-2a3 3 0 0 0-3-3h-7v5" />
      <circle cx="7" cy="11" r="1.8" />
    </g>
  ),
  mesa: (
    <g>
      <circle cx="12" cy="12" r="5.5" />
      <circle cx="12" cy="12" r="2.5" />
      <path d="M3 4v6c0 1 .8 1.5 1.5 1.5S6 11 6 10V4M4.5 11.5V20M20 4c-1.5 1-2 3-2 6h2v10" />
    </g>
  ),
};

interface SelloProps {
  icono: Icono;
  etiqueta: string;
  color?: string;
  /** Grados de giro, como en el mockup (los sellos no van rectos). */
  giro?: number;
  /** Sello que falta: gris y con borde punteado. */
  falta?: boolean;
  tamano?: number;
}

/** Sello circular con ícono y etiqueta (docs/mockup/Sello.dc.html). */
export function Sello({ icono, etiqueta, color = "#1C5FA8", giro = 0, falta = false, tamano = 112 }: SelloProps) {
  const tinta = falta ? "#8A94A3" : color;
  const linea = falta ? "dashed" : "solid";
  const icono_px = tamano >= 80 ? Math.round(tamano * 0.3) : Math.round(tamano * 0.42);
  const letra = tamano >= 110 ? 11 : tamano >= 92 ? 10 : 9;
  return (
    <div
      className="sello"
      style={{ width: tamano, height: tamano, transform: `rotate(${giro}deg)` }}
      role="img"
      aria-label={etiqueta}
    >
      <div
        className="sello-borde"
        style={{ borderStyle: linea, borderColor: tinta, background: falta ? "#FFFFFF" : `${color}14` }}
      >
        <div className="sello-interior" style={{ borderStyle: linea, borderColor: tinta }}>
          <svg
            width={icono_px}
            height={icono_px}
            viewBox="0 0 24 24"
            fill="none"
            stroke={tinta}
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            {TRAZOS[icono]}
          </svg>
          {tamano >= 80 && (
            <span className="sello-etiqueta" style={{ fontSize: letra, color: tinta }}>
              {etiqueta}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
