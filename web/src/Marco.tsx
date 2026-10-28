import { useEffect, useState } from "react";
import { Outlet, useOutletContext } from "react-router";
import { api } from "./api";
import { TEXTOS } from "./textos";

interface Modo {
  sinConexion: boolean;
}

/** Banda "Prototipo" fija arriba y marca pequeña cuando QVAC corre en modo respaldo (HU-15). */
export function Marco() {
  const [sinConexion, setSinConexion] = useState(false);

  useEffect(() => {
    api
      .salud()
      .then((s) => setSinConexion(s.modo === "respaldo"))
      .catch(() => setSinConexion(false));
  }, []);

  return (
    <div className="marco">
      <div className="banda" role="note">
        <span>{TEXTOS.banda}</span>
        {sinConexion && <span className="marca-sin-conexion">{TEXTOS.sinConexion}</span>}
      </div>
      <Outlet context={{ sinConexion } satisfies Modo} />
    </div>
  );
}

/** true si el backend corre en modo respaldo: solo entonces se ofrece el ejemplo de María (spec 7). */
export function useSinConexion(): boolean {
  return useOutletContext<Modo>().sinConexion;
}
