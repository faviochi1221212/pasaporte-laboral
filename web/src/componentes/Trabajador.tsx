import type { ReactElement } from "react";

/** Ilustraciones de docs/mockup/Trabajador.dc.html (kind_ilustracion en ocupaciones.json). */
export type Ilustracion = "cajera" | "vendedor" | "limpieza" | "almacen" | "administrativo" | "todo";

const FONDOS: Record<Ilustracion, string> = {
  cajera: "#E3F1EE",
  vendedor: "#FBEBDD",
  limpieza: "#E2EEF9",
  almacen: "#FDF1D6",
  administrativo: "#E8EEF7",
  todo: "#F1E9E1",
};

const CUERPO = "M28 120 C28 94 42 84 60 84 C78 84 92 94 92 120 Z";

const FIGURAS: Record<Ilustracion, ReactElement> = {
  cajera: (
    <g>
      <path d={CUERPO} fill="#2F7D6D" />
      <path d="M52 84 L60 96 L68 84 Z" fill="#FFFFFF" />
      <rect x="66" y="98" width="12" height="6" rx="1.5" fill="#FFFFFF" />
      <rect x="55" y="70" width="10" height="16" fill="#C68B59" />
      <path
        d="M41 58 C39 36 51 30 61 30 C72 30 81 38 79 58 L80 74 C75 70 75 58 73 49 C66 53 52 53 47 49 C46 58 45 66 41 74 Z"
        fill="#2B1B12"
      />
      <circle cx="60" cy="58" r="16" fill="#C68B59" />
      <path d="M44 52 C48 42 72 40 77 52 C70 47 52 46 44 52 Z" fill="#2B1B12" />
      <rect x="72" y="92" width="40" height="24" rx="3" fill="#4B5563" />
      <rect x="78" y="82" width="22" height="12" rx="2" fill="#9CD3C8" />
      <rect x="77" y="98" width="6" height="4" rx="1" fill="#D1D5DB" />
      <rect x="86" y="98" width="6" height="4" rx="1" fill="#D1D5DB" />
      <rect x="95" y="98" width="6" height="4" rx="1" fill="#D1D5DB" />
      <rect x="77" y="105" width="6" height="4" rx="1" fill="#D1D5DB" />
      <rect x="86" y="105" width="6" height="4" rx="1" fill="#D1D5DB" />
      <rect x="95" y="105" width="6" height="4" rx="1" fill="#D1D5DB" />
    </g>
  ),
  vendedor: (
    <g>
      <path d={CUERPO} fill="#D9822B" />
      <path d="M50 84 L60 94 L70 84 L66 82 L60 88 L54 82 Z" fill="#B8651A" />
      <rect x="55" y="70" width="10" height="16" fill="#8D5524" />
      <circle cx="60" cy="58" r="16" fill="#8D5524" />
      <path d="M43 56 C42 39 51 34 61 34 C72 34 79 41 77 56 C74 47 67 44 60 44 C53 44 46 48 43 56 Z" fill="#1B120C" />
      <path d="M78 88 L104 88 L108 118 L74 118 Z" fill="#F2C14E" />
      <path d="M84 90 C84 78 98 78 98 90" stroke="#B8860B" strokeWidth="3" fill="none" />
    </g>
  ),
  limpieza: (
    <g>
      <path d={CUERPO} fill="#3B82C4" />
      <rect x="46" y="96" width="28" height="24" rx="3" fill="#2F6CA8" />
      <rect x="55" y="70" width="10" height="16" fill="#A86B3C" />
      <circle cx="60" cy="31" r="7" fill="#2B1B12" />
      <circle cx="60" cy="58" r="16" fill="#A86B3C" />
      <path d="M44 55 C43 40 52 36 61 36 C71 36 78 42 76 55 C72 47 66 45 60 45 C54 45 47 48 44 55 Z" fill="#2B1B12" />
      <line x1="100" y1="40" x2="94" y2="108" stroke="#8B5E3C" strokeWidth="4" strokeLinecap="round" />
      <rect x="82" y="106" width="24" height="8" rx="3" fill="#E5E7EB" />
      <path d="M84 114 L84 118 M90 114 L90 118 M96 114 L96 118 M102 114 L102 118" stroke="#D1D5DB" strokeWidth="2" />
    </g>
  ),
  almacen: (
    <g>
      <path d={CUERPO} fill="#6B7280" />
      <path d="M36 120 C36 98 44 88 52 86 L52 120 Z" fill="#F59E0B" />
      <path d="M84 120 C84 98 76 88 68 86 L68 120 Z" fill="#F59E0B" />
      <rect x="36" y="104" width="16" height="4" fill="#FDE68A" />
      <rect x="68" y="104" width="16" height="4" fill="#FDE68A" />
      <rect x="55" y="70" width="10" height="16" fill="#D9A066" />
      <circle cx="60" cy="58" r="16" fill="#D9A066" />
      <path d="M42 52 C42 38 50 33 60 33 C70 33 78 38 78 52 Z" fill="#F2C14E" />
      <rect x="40" y="50" width="40" height="5" rx="2" fill="#E0A800" />
      <rect x="76" y="90" width="32" height="26" rx="2" fill="#C08A5B" />
      <line x1="76" y1="98" x2="108" y2="98" stroke="#8B5E3C" strokeWidth="2" />
      <rect x="82" y="72" width="22" height="18" rx="2" fill="#D4A373" />
      <line x1="82" y1="79" x2="104" y2="79" stroke="#A47148" strokeWidth="2" />
    </g>
  ),
  administrativo: (
    <g>
      <path d={CUERPO} fill="#DCE6F2" />
      <path d="M52 84 L60 92 L68 84" stroke="#9DB2CC" strokeWidth="2" fill="none" />
      <path d="M54 86 L60 112 L66 86" stroke="#0B4F9F" strokeWidth="2" fill="none" />
      <rect x="56" y="108" width="8" height="10" rx="1" fill="#0B4F9F" />
      <rect x="55" y="70" width="10" height="16" fill="#C68B59" />
      <circle cx="60" cy="58" r="16" fill="#C68B59" />
      <path d="M44 56 C42 40 51 34 61 34 C72 34 79 41 77 54 C70 46 58 44 50 48 C47 50 45 53 44 56 Z" fill="#3B2A20" />
      <circle cx="54" cy="60" r="5" fill="none" stroke="#1F2937" strokeWidth="1.6" />
      <circle cx="66" cy="60" r="5" fill="none" stroke="#1F2937" strokeWidth="1.6" />
      <line x1="59" y1="60" x2="61" y2="60" stroke="#1F2937" strokeWidth="1.6" />
      <rect x="72" y="88" width="38" height="24" rx="2" fill="#374151" />
      <rect x="76" y="92" width="30" height="16" rx="1" fill="#9DB7D5" />
      <rect x="68" y="112" width="46" height="4" rx="2" fill="#4B5563" />
    </g>
  ),
  todo: (
    <g>
      <path d={CUERPO} fill="#7C5C3E" />
      <rect x="46" y="94" width="28" height="26" rx="3" fill="#6A4C30" />
      <line x1="48" y1="86" x2="48" y2="96" stroke="#6A4C30" strokeWidth="3" />
      <line x1="72" y1="86" x2="72" y2="96" stroke="#6A4C30" strokeWidth="3" />
      <rect x="55" y="70" width="10" height="16" fill="#8D5524" />
      <circle cx="60" cy="58" r="16" fill="#8D5524" />
      <path d="M43 52 C43 38 51 34 60 34 C70 34 77 38 77 52 Z" fill="#0B4F9F" />
      <rect x="30" y="49" width="20" height="5" rx="2" fill="#0B4F9F" />
      <rect x="74" y="94" width="36" height="22" rx="3" fill="#B45309" />
      <path d="M84 94 L84 88 L100 88 L100 94" stroke="#7C3A06" strokeWidth="3" fill="none" />
      <rect x="74" y="102" width="36" height="3" fill="#7C3A06" />
      <path
        d="M88 72 L100 84 M86 70 C84 68 85 64 88 64 L90 66 L88 68 L90 70 L92 68 L94 70 C94 73 90 74 88 72 Z"
        stroke="#4B5563"
        strokeWidth="3"
        fill="#9CA3AF"
        strokeLinecap="round"
      />
    </g>
  ),
};

interface TrabajadorProps {
  tipo: Ilustracion;
  tamano?: number;
}

/** Ilustración de una persona trabajando; decorativa, el texto va al lado. */
export function Trabajador({ tipo, tamano = 120 }: TrabajadorProps) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 120 120" aria-hidden="true">
      <circle cx="60" cy="60" r="58" fill={FONDOS[tipo]} />
      {FIGURAS[tipo]}
    </svg>
  );
}
