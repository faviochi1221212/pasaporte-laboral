export type Fuente = "oficio" | "pregunta" | "vida" | "relato" | "prueba";

export interface EstadoPersona {
  perfil: string;
  competencias: string[];
  pruebas: string[];
  avales: string[];
  prefs: string[];
  obstaculo: string;
  horas: number;
}

export interface Oferta {
  id: string;
  fuente: Fuente;
  titulo: string;
  empleador: string;
  ciudad: string;
  remoto: boolean;
  pago: string;
  planilla: boolean;
  pide_certificado: boolean;
  publicado_hace_dias: number;
  url: string;
  descripcion: string;
  ocupacion: string;
  fuentes: Fuente[];
  encaje: number;
  estafa: boolean;
}
