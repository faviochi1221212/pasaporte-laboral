import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import "./estilos.css";
import { Marco } from "./Marco";
import { Avisos } from "./pantallas/Avisos";
import { Conversacion } from "./pantallas/Conversacion";
import { Cv } from "./pantallas/Cv";
import { Destino } from "./pantallas/Destino";
import { Espera } from "./pantallas/Espera";
import { Inicio } from "./pantallas/Inicio";
import { Intereses } from "./pantallas/Intereses";
import { PantallaPasaporte } from "./pantallas/Pasaporte";
import { Ruta } from "./pantallas/Ruta";
import { ProveedorSesion } from "./sesion";

const raiz = document.getElementById("raiz");
if (!raiz) throw new Error("Falta el elemento #raiz");

createRoot(raiz).render(
  <StrictMode>
    <ProveedorSesion>
      <BrowserRouter>
        <Routes>
          <Route element={<Marco />}>
            <Route path="/" element={<Inicio />} />
            <Route path="/conversacion" element={<Conversacion />} />
            <Route path="/espera" element={<Espera />} />
            <Route path="/pasaporte" element={<PantallaPasaporte />} />
            <Route path="/intereses" element={<Intereses />} />
            <Route path="/ruta" element={<Ruta />} />
            <Route path="/destino/:codigo" element={<Destino />} />
            <Route path="/avisos/:codigo" element={<Avisos />} />
            <Route path="/cv/:codigo" element={<Cv />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ProveedorSesion>
  </StrictMode>,
);
