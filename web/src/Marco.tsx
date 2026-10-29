import { useEffect, useState } from "react";
import { Outlet, useLocation, useOutletContext } from "react-router";
import { api } from "./api";
import { TEXTOS } from "./textos";
import { Pasos } from "./componentes/Pasos";

interface Modo {
  sinConexion: boolean;
}

/** Pie "Prototipo…" en todas las pantallas y, solo en modo respaldo, la marca pequeña arriba (HU-15). */
export function Marco() {
  const [sinConexion, setSinConexion] = useState(false);

  useEffect(() => {
    api
      .salud()
      .then((s) => setSinConexion(s.modo === "respaldo"))
      .catch(() => setSinConexion(false));
  }, []);

  const { pathname } = useLocation();
  const esInicio = pathname === "/";

  return (
    <div className="marco">
      {sinConexion && (
        <div className="marca-arriba" role="note">
          <span className="marca-sin-conexion">{TEXTOS.sinConexion}</span>
        </div>
      )}
      {!esInicio && (
        <>
          <header className="cabecera">
            <h1 className="cabecera-titulo">{TEXTOS.cabecera}</h1>
          </header>
          <Pasos />
        </>
      )}
      <Outlet context={{ sinConexion } satisfies Modo} />
      <footer className="pie">{TEXTOS.pie}</footer>
    </div>
  );
}

/** true si el backend corre en modo respaldo: solo entonces se ofrece el ejemplo de María (spec 7). */
export function useSinConexion(): boolean {
  return useOutletContext<Modo>().sinConexion;
}
