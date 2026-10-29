import { useLocation } from "react-router";
import { TEXTOS } from "../textos";

/** Barra de 4 pasos (spec 2): muestra en qué paso va la persona. */
export function Pasos() {
  const { pathname } = useLocation();

  let pasoActivo = 0;
  if (pathname === "/conversacion" || pathname === "/espera") pasoActivo = 1;
  else if (pathname === "/pasaporte" || pathname === "/intereses") pasoActivo = 2;
  else if (pathname.startsWith("/ruta") || pathname.startsWith("/destino")) pasoActivo = 3;
  else if (pathname.startsWith("/avisos") || pathname.startsWith("/cv")) pasoActivo = 4;

  if (pasoActivo === 0) return null;

  return (
    <nav className="pasos" aria-label="Progreso">
      {TEXTOS.pasos.map((nombre, i) => {
        const n = i + 1;
        const estado = n < pasoActivo ? "hecho" : n === pasoActivo ? "activo" : "siguiente";
        return (
          <div key={nombre} className={`paso paso-${estado}`}>
            <span className="paso-circulo" aria-hidden="true">
              {estado === "hecho" ? "✓" : n}
            </span>
            <span className="paso-nombre">{nombre}</span>
          </div>
        );
      })}
    </nav>
  );
}
