"""Valida que los archivos de data/ sean coherentes entre sí (criterio "Hecho cuando" de M1).

Uso: python scripts/validar_datos.py   (desde la raíz del repositorio)
Sale con código 1 si encuentra algún problema.
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"


def cargar(nombre):
    return json.loads((DATA / nombre).read_text(encoding="utf-8"))


def main():
    problemas = []
    ocupaciones = cargar("ocupaciones.json")
    competencias = cargar("competencias.json")
    cursos = cargar("cursos.json")
    avisos = cargar("avisos.json")
    demanda = cargar("demanda.json")

    perfiles = {o["codigo"] for o in ocupaciones}
    codigos = {c["codigo"] for c in competencias}

    if len(codigos) != len(competencias):
        problemas.append("competencias.json tiene códigos repetidos")

    for o in ocupaciones:
        for campo in ("tipo", "que_harias", "estandares_operativos", "fuente", "tomado"):
            if not o.get(campo):
                problemas.append(f"ocupación {o['codigo']} sin {campo}")
        if o.get("tipo") not in ("gente", "cosas", "papeles"):
            problemas.append(f"ocupación {o['codigo']} con tipo inválido: {o.get('tipo')}")
        if len(o.get("que_harias", [])) != 3:
            problemas.append(f"ocupación {o['codigo']} debe tener 3 'que_harias'")

    for c in competencias:
        if c["perfil"] not in perfiles:
            problemas.append(f"competencia {c['codigo']} apunta a perfil inexistente {c['perfil']}")
        for campo in ("texto_oficial", "texto_simple", "fuente", "tomado"):
            if not c.get(campo):
                problemas.append(f"competencia {c['codigo']} sin {campo}")
        if not c.get("sello", {}).get("etiqueta") or not c.get("sello", {}).get("icono"):
            problemas.append(f"competencia {c['codigo']} sin sello completo")

    for cu in cursos:
        for campo in ("nombre", "horas", "url", "fuente", "tomado"):
            if not cu.get(campo):
                problemas.append(f"curso {cu.get('id')} sin {campo}")
        for cub in cu.get("cubre", []):
            if cub["codigo"] not in codigos:
                problemas.append(f"curso {cu['id']} cubre un código inexistente: {cub['codigo']}")
            if cub.get("alcance") not in ("completo", "solo_teoria"):
                problemas.append(f"curso {cu['id']} con alcance inválido en {cub['codigo']}")

    for a in avisos:
        if a["perfil"] not in perfiles:
            problemas.append(f"aviso {a['id']} apunta a perfil inexistente {a['perfil']}")
        for campo in ("titulo", "empresa", "distrito", "cierre", "url", "fuente", "tomado"):
            if not a.get(campo):
                problemas.append(f"aviso {a['id']} sin {campo}")
        if not a.get("que_piden"):
            problemas.append(f"aviso {a['id']} sin que_piden")
    por_perfil = {}
    for a in avisos:
        por_perfil[a["perfil"]] = por_perfil.get(a["perfil"], 0) + 1
    for p, n in por_perfil.items():
        if n > 3:
            problemas.append(f"perfil {p} tiene {n} avisos; el máximo es 3")

    if set(demanda["perfiles"]) != perfiles:
        problemas.append("demanda.json no tiene exactamente los mismos perfiles que ocupaciones.json")
    for p, d in demanda["perfiles"].items():
        if not 0 <= d["demanda"] <= 1:
            problemas.append(f"demanda de {p} fuera de 0 a 1")

    if problemas:
        print("PROBLEMAS:")
        for p in problemas:
            print(" -", p)
        sys.exit(1)
    print(f"OK: {len(ocupaciones)} perfiles, {len(competencias)} sellos, {len(cursos)} cursos, "
          f"{len(avisos)} avisos, demanda tomada {demanda['tomado']}")


if __name__ == "__main__":
    main()
