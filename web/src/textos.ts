// Textos fijos que solo salen en pantalla (los que vienen de la API se muestran tal cual).
// tests/test_web.py revisa que no tengan palabras prohibidas (regla 5 de CLAUDE.md).

export const TEXTOS = {
  banda: "Prototipo · no es un sitio oficial",
  sinConexion: "modo sin conexión",
  atras: "Atrás",
  errorRed: "No pudimos conectarnos. Inténtalo de nuevo.",

  inicio: {
    titulo: "Sabes más de lo que crees.",
    subtitulo: "Cuéntanos tu trabajo y descubre a qué trabajos puedes llegar.",
    pregunta: "¿En qué trabajas?",
    tarjetas: {
      caja: "Caja",
      ventas: "Ventas",
      limpieza: "Limpieza",
      almacen: "Almacén",
      oficina: "Oficina",
      todo: "De todo",
    },
    otro: "¿No está tu trabajo?",
    otroEjemplo: "Escríbelo: mozo, costurera, chofer…",
    otroContinuar: "Continuar con mi trabajo",
    minutos: "5 minutos",
    puedesHablar: "Puedes hablar",
    sellosDecorativos: ["Cuadra la caja", "Atiende reclamos", "Ordena mercadería"],
  },

  chat: {
    escribiendo: "escribiendo…",
    progreso: (n: number) => `Pregunta ${n} de 6`,
    campo: "Tu respuesta",
    campoEjemplo: "Escribe aquí con tus palabras",
    enviar: "Enviar",
    hablar: "Responder hablando",
    escuchando: "Te escucho…",
    sellosGanados: (n: number) => (n === 1 ? "1 sello ganado" : `${n} sellos ganados`),
    sigueContando: "Sigue contándonos",
  },

  espera: {
    titulo: "Armando tu pasaporte…",
    detalle: "Estamos buscando en lo que contaste las tareas del catálogo de perfiles del MTPE.",
    reintentar: "Volver a intentar",
  },

  pasaporte: {
    titulo: "¡Mira todo lo que sabes!",
    resumen: (n: number) =>
      n === 1 ? "1 sello. Tócalo para ver por qué lo ganaste." : `${n} sellos. Toca uno para ver por qué lo ganaste.`,
    cabecera: "PASAPORTE LABORAL",
    pais: "PERÚ",
    loQueHaces: "Lo que contaste que haces",
    porQue: (etiqueta: string) => `Sello «${etiqueta}» · Lo ganaste porque dijiste:`,
    sirveEn: (n: number) => `sirve en ${n} trabajos`,
    quitarSello: "Quitar este sello",
    quitados: "Quitaste:",
    deshacer: (que: string) => `Deshacer: ${que}`,
    fortalezas: "Otras fortalezas",
    fortalezasDetalle: "No dan sellos, pero van a tu CV.",
    quitar: "Quitar",
    sinSellos: "No encontramos sellos en lo que contaste. Puedes volver a empezar y contarnos con más detalle.",
    empezar: "Volver a empezar",
    siguiente: "Ver a dónde te lleva",
    pie: "Sellos según el catálogo de perfiles del MTPE · es lo que contaste que haces",
  },

  intereses: {
    titulo: "¿Qué tipo de trabajo te gusta más?",
    detalle: "Así ordenamos los trabajos que te mostramos. No hay respuesta buena ni mala.",
    opciones: {
      gente: ["Con gente", "Atender, ayudar, conversar"],
      cosas: ["Con cosas y orden", "Ordenar, limpiar, preparar"],
      papeles: ["Con papeles y números", "Registrar, contar, revisar"],
    },
  },

  ruta: {
    titulo: "Tu ruta",
    detalle: "Cada parada es un sello que te falta. Toca una estación.",
    estasAqui: "ESTÁS AQUÍ",
    estacion: (nombre: string) => `Estación: ${nombre}`,
    tienes: (n: number, total: number) => `Ya tienes ${n} de ${total} sellos`,
    faltan: (n: number) => (n === 1 ? "Te falta 1 sello" : `Te faltan ${n} sellos`),
    avisos: (n: number, fecha: string) => (n === 1 ? `1 aviso en Lima al ${fecha}` : `${n} avisos en Lima al ${fecha}`),
    pocos: "Cuéntanos un poco más para encontrar otros caminos",
    volverAContar: "Volver a contar",
    porQueTitulo: "¿Por qué estos trabajos?",
    porQue:
      "Los ordenamos según cuántos de tus sellos sirven ahí, si es el tipo de trabajo que te gusta y cuántos avisos hay hoy en Lima. Tú eliges.",
    fuentes: "Sellos según el catálogo de perfiles del MTPE · Avisos de Empleos Perú en Lima · Cursos de CAPACITA-T",
  },

  destino: {
    proxima: "PRÓXIMA ESTACIÓN",
    volver: "Volver a tu ruta",
    yaHaces: "Lo que ya haces y aquí también sirve",
    queHarias: "Qué harías ahí",
    teFalta: "Lo que te falta",
    teFaltaDetalle: "Tu siguiente paso para llegar a este trabajo.",
    nadaFalta: "Ya haces todo lo que pide este trabajo",
    semanas: (n: number) => `unas ${n} semanas con tu tiempo`,
    horas: (n: number) => `${n} h · gratis y virtual`,
    teorica: (modulo: string) => `Te ayuda con la parte teórica de: ${modulo}`,
    verCurso: "Ver el curso",
    avisos: "Avisos hoy en Lima",
    sinAvisos: "Hoy no hay avisos en Lima para esto",
    verAvisos: "Ver los avisos",
    miCv: "Mi CV",
  },
};

// Único lugar donde vale la frase de la regla 5, y solo en la pantalla del CV.
export const TEXTOS_CV = {
  tituloSellos: "COMPETENCIAS DECLARADAS",
  pie: "Competencias declaradas por la persona, basadas en el Catálogo Nacional de Perfiles Ocupacionales del MTPE.",
};
