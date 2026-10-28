"""Comprueba que texto_oficial y criterios_clave de data/competencias.json aparezcan tal cual en los PDF del MTPE.

Necesita el programa pdftotext (poppler). En Windows: instalar poppler y agregarlo al PATH.
Uso: python scripts/verificar_textos_pdf.py   (desde la raíz del repositorio)

Recepción de Hotel (I2555001) es un PDF escaneado sin texto: sus textos se transcribieron a mano
y este script los marca como "revisar a mano" en vez de fallar.
"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PDFS = {
    "G2347002": "G2347002_caja_establecimientos_comerciales.pdf",
    "H2452001": "H2452001_operaciones_de_almacen.pdf",
    "M2981001": "M2981001_servicios_de_limpieza.pdf",
    "I2555001": "I2555001_recepcion_hotel_hostal.pdf",
    "I2555002": "I2555002_operaciones_housekeeping.pdf",
    "I2556002": "I2556002_atencion_salon_comidas_bebidas.pdf",
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def texto_pdf(ruta):
    salida = subprocess.run(["pdftotext", str(ruta), "-"], capture_output=True, text=True, check=True)
    return normalizar(salida.stdout)


def main():
    competencias = json.loads((RAIZ / "data" / "competencias.json").read_text(encoding="utf-8"))
    textos = {p: texto_pdf(RAIZ / "docs" / "fuentes" / f) for p, f in PDFS.items()}
    fallas = 0
    for c in competencias:
        t = textos[c["perfil"]]
        if len(t) < 100:
            print(f"revisar a mano (PDF escaneado): {c['codigo']}")
            continue
        for frase in [c["texto_oficial"], *c["criterios_clave"]]:
            if normalizar(frase) not in t:
                fallas += 1
                print(f"NO ESTÁ EN EL PDF: {c['codigo']} | {frase[:90]}")
    print("OK" if not fallas else f"{fallas} textos no coinciden")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
