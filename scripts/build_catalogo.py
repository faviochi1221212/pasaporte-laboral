"""Genera data/ocupaciones.json y data/competencias.json.
Uso: python scripts/build_catalogo.py (desde la raíz del repositorio).

Fuente: PDF de los perfiles ocupacionales del CNPO (MTPE), descargados el 27 oct 2026.
- texto_oficial: copia literal del elemento de competencia en el PDF.
- criterios_clave: fragmentos literales de los criterios de desempeño (ayudan al modelo a reconocer la tarea).
- texto_simple, sello y que_harias: redacción del equipo, para el usuario. Revisar a mano.
- codigo: código oficial del estándar (ECL) + "E" + número del elemento según el orden del PDF.
  El MTPE no numera los elementos con código propio; la numeración del elemento es nuestra.
Solo se cargan los estándares de puestos operativos (no supervisor, jefe ni administrador).
"""
import json
from pathlib import Path

FECHA = "2026-10-27"

OCUPACIONES = [
    {"codigo": "G2347002", "nombre": "Caja en Establecimientos Comerciales", "nombre_simple": "Cajero/a",
     "tipo": "gente", "origen": True, "vence": "2029-02-26", "norma": "RDG N° 000020-2026-MTPE/3/19",
     "estandares_operativos": ["G2347002-1"],
     "que_harias": ["Abrir la caja al empezar el turno", "Cobrar con efectivo, tarjeta o Yape", "Cuadrar la caja al cerrar"],
     "kind_ilustracion": "cajera"},
    {"codigo": "H2452001", "nombre": "Operaciones de Almacén", "nombre_simple": "Operario/a de almacén",
     "tipo": "cosas", "origen": True, "vence": "2027-08-29", "norma": "RDG N° 000081-2026-MTPE/3/19",
     "estandares_operativos": ["H2452001-1"],
     "que_harias": ["Recibir la mercadería que llega", "Guardarla ordenada en su lugar", "Preparar y despachar los pedidos"],
     "kind_ilustracion": "almacen"},
    {"codigo": "M2981001", "nombre": "Servicios de Limpieza", "nombre_simple": "Operario/a de limpieza",
     "tipo": "cosas", "origen": True, "vence": "2030-08-11", "norma": "RDG N° 000052-2025-MTPE/3/19",
     "estandares_operativos": ["M2981001-1"],
     "que_harias": ["Preparar tus materiales de limpieza", "Limpiar las áreas asignadas", "Revisar que todo quede en buen estado"],
     "kind_ilustracion": "limpieza"},
    {"codigo": "I2555001", "nombre": "Recepción de Hotel/Hostal", "nombre_simple": "Recepcionista de hotel",
     "tipo": "gente", "origen": False, "vence": "2027-04-25", "norma": "RDG N° 000038-2025-MTPE/3/19",
     "estandares_operativos": ["I2555001-1", "I2555001-2"],
     "que_harias": ["Recibir a los huéspedes y registrar su entrada y salida", "Dar información y atender pedidos", "Cobrar y cuadrar la caja de recepción"],
     "kind_ilustracion": "administrativo"},
    {"codigo": "I2555002", "nombre": "Operaciones de Housekeeping", "nombre_simple": "Housekeeping (limpieza de hotel)",
     "tipo": "cosas", "origen": False, "vence": "2028-05-01", "norma": "RD N° 0028-2023-MTPE/3/19",
     "estandares_operativos": ["I2555002-1", "I2555002-2", "I2555002-3"],
     "que_harias": ["Limpiar áreas y habitaciones de hotel", "Dejar lista la habitación para el huésped", "Atender lo que pida el huésped"],
     "kind_ilustracion": "limpieza"},
    {"codigo": "I2556002", "nombre": "Atención en Salón de Comidas y Bebidas/Eventos", "nombre_simple": "Mozo/a o ayudante de salón",
     "tipo": "gente", "origen": False, "vence": "2029-02-22", "norma": "RDG N° 000018-2026-MTPE/3/19",
     "estandares_operativos": ["I2556002-1", "I2556002-2"],
     "que_harias": ["Preparar mesas y menaje", "Recibir al cliente y tomar su pedido", "Servir, cobrar y entregar el vuelto"],
     "kind_ilustracion": "vendedor"},
]

# (codigo, perfil, texto_oficial, criterios_clave, texto_simple, sello)
E = [
    # --- Caja (ECL G2347002-1, Cajero/a, nivel 2)
    ("G2347002-1.E1", "G2347002",
     "Ejecutar la apertura del punto de caja asignado, teniendo en cuenta los procedimientos establecidos por la empresa y normativa vigente.",
     ["Verifica la disponibilidad del fondo de dinero en caja", "Verifica la operatividad de los equipos de caja"],
     "Abrir la caja: revisar el fondo de dinero y que los equipos funcionen", ("caja", "Abre la caja")),
    ("G2347002-1.E2", "G2347002",
     "Realizar la cobranza y de corresponder la entrega de los productos/servicios, de acuerdo a los procedimientos establecidos por la empresa y normativa vigente.",
     ["Recibe, cuenta y verifica el dinero", "entrega el vuelto", "Absuelve y/o deriva las inquietudes o reclamos expresadas por el cliente"],
     "Cobrar en efectivo, con tarjeta o con Yape y entregar lo comprado", ("cobro", "Cobra y da vuelto")),
    ("G2347002-1.E3", "G2347002",
     "Ejecutar el arqueo y cuadre de caja, teniendo en cuenta los procedimientos establecidos por la empresa y normativa vigente.",
     ["Ejecuta el cuadre de caja al cierre de la jornada laboral", "Realiza el cierre del lote de tarjetas bancarias (POS)"],
     "Cuadrar la caja al final del día", ("caja", "Cuadra la caja")),
    # --- Almacén (ECL H2452001-1, Almacenero/Operario de almacén, nivel 2)
    ("H2452001-1.E1", "H2452001",
     "Recepcionar las existencias que ingresan al almacén, de acuerdo a los procedimientos de la empresa, requerimientos de clientes y normativa correspondiente.",
     ["Recibe las existencias y el documento sustentatorio", "Registra las entradas en el sistema del almacén"],
     "Recibir la mercadería que llega y revisar que esté completa y en buen estado", ("mercaderia", "Recibe mercadería")),
    ("H2452001-1.E2", "H2452001",
     "Almacenar las existencias, según tipo y características, de acuerdo a los procedimientos de la empresa, requerimientos de clientes y normativa correspondiente.",
     ["Agrupa y ubica las existencias en el almacén", "Ordena y reordena las existencias del almacén según su rotación"],
     "Ordenar y guardar la mercadería en su lugar", ("mercaderia", "Ordena mercadería")),
    ("H2452001-1.E3", "H2452001",
     "Despachar las existencias, de acuerdo a los procedimientos de la empresa, requerimientos de clientes y normativa correspondiente.",
     ["Recibe requerimientos de despacho de existencias", "Realiza el picking"],
     "Preparar y entregar los pedidos que salen", ("mercaderia", "Despacha pedidos")),
    # --- Limpieza (ECL M2981001-1, Operario/a de limpieza, nivel 1)
    ("M2981001-1.E1", "M2981001",
     "Organizar las actividades de limpieza de las áreas designadas, de acuerdo a las políticas del establecimiento y teniendo en cuenta la normativa vigente.",
     ["Verifica la operatividad de los equipos", "Abastece el carrito o balde de limpieza"],
     "Organizar el trabajo de limpieza y preparar los materiales", ("limpieza", "Organiza la limpieza")),
    ("M2981001-1.E2", "M2981001",
     "Limpiar las áreas asignadas, teniendo en cuenta las políticas del establecimiento y la normativa vigente.",
     ["Limpia las áreas asignadas", "Desecha los desperdicios de las áreas asignadas", "Reporta objetos olvidados"],
     "Limpiar las áreas y botar los desperdicios", ("limpieza", "Limpia áreas")),
    ("M2981001-1.E3", "M2981001",
     "Ordenar y verificar el estado óptimo de los enseres e infraestructura, de acuerdo a las políticas del establecimiento y teniendo en cuenta la normativa vigente.",
     ["Ordena el equipamiento de las áreas asignadas", "reporta desperfectos del área asignada"],
     "Ordenar los espacios y avisar si algo está malogrado", ("revision", "Ordena y revisa espacios")),
    # --- Recepción de hotel (UC I2555001-1 y -2, nivel 2)
    ("I2555001-1.E1", "I2555001",
     "Trasladar el equipaje del huésped al área requerida, de acuerdo a las normas de seguridad y procedimientos del establecimiento.",
     ["Recibe y acompaña al huésped", "Traslada el equipaje del huésped hacia el área requerida"],
     "Recibir al huésped y llevar su equipaje", ("maleta", "Recibe huéspedes")),
    ("I2555001-1.E2", "I2555001",
     "Distribuir mensajería y encargos para los huéspedes o áreas internas, de acuerdo a los procedimientos del establecimiento.",
     ["Registra la llegada de mensajería y encargos", "Entrega al huésped o al área interna correspondiente la mensajería y encargos"],
     "Recibir y entregar encargos y mensajes", ("mercaderia", "Entrega encargos")),
    ("I2555001-1.E3", "I2555001",
     "Brindar información al huésped, de acuerdo a los procedimientos del establecimiento.",
     ["Orienta al huésped sobre la ubicación de los ambientes y servicios", "Informa al huésped sobre la disponibilidad de servicios"],
     "Dar información y orientar a las personas", ("atencion", "Da información")),
    ("I2555001-2.E1", "I2555001",
     "Atender requerimientos del huésped, de acuerdo a los procedimientos del establecimiento y normativa correspondiente.",
     ["Atiende o deriva los requerimientos del huésped", "Gestiona las llamadas telefónicas"],
     "Atender pedidos y quejas de los clientes", ("atencion", "Atiende reclamos")),
    ("I2555001-2.E2", "I2555001",
     "Registrar la entrada (check in) del huésped, de acuerdo a los procedimientos del establecimiento y normativa correspondiente.",
     ["Registra la entrada (check in) del huésped", "Verifica el número de habitaciones disponibles y ocupadas"],
     "Registrar la llegada de los huéspedes", ("registro", "Registra llegadas")),
    ("I2555001-2.E3", "I2555001",
     "Registrar la salida (check out) del huésped, de acuerdo a los procedimientos del establecimiento y normativa correspondiente.",
     ["Verifica la cuenta final del huésped", "Realiza el cobro o facturación"],
     "Cerrar la cuenta del huésped y cobrarle al salir", ("cobro", "Cierra cuentas")),
    ("I2555001-2.E4", "I2555001",
     "Realizar operaciones de caja del área de recepción, de acuerdo a los procedimientos del establecimiento y normativa correspondiente.",
     ["Ejecuta el cuadre de caja al inicio y culminación de su turno", "Cierra las operaciones realizadas en el POS"],
     "Manejar y cuadrar la caja de recepción", ("caja", "Cuadra la caja")),
    # --- Housekeeping (ECL I2555002-1, -2, -3, nivel 1)
    ("I2555002-1.E1", "I2555002",
     "Organizar las actividades de limpieza de las áreas asignadas, teniendo en cuenta las indicaciones del jefe inmediato, de acuerdo a las políticas y los procedimientos de la empresa.",
     ["Prioriza el trabajo asignado", "Prepara los productos de limpieza seleccionados"],
     "Organizar el trabajo de limpieza y preparar los productos", ("limpieza", "Organiza la limpieza")),
    ("I2555002-1.E2", "I2555002",
     "Aplicar las técnicas de limpieza en las áreas asignadas, teniendo en cuenta las indicaciones del jefe inmediato, de acuerdo a las políticas y los procedimientos de la empresa.",
     ["Emplea técnicas de limpieza en las áreas asignadas", "Reporta los objetos perdidos/olvidados del cliente"],
     "Limpiar superficies, muebles y pisos con la técnica correcta", ("limpieza", "Limpia áreas")),
    ("I2555002-2.E1", "I2555002",
     "Organizar las actividades para el acondicionamiento de la habitación asignada, teniendo en cuenta los requerimientos del huésped, de acuerdo a las políticas y los procedimientos de la empresa.",
     [],
     "Planificar cómo dejar lista una habitación", ("habitacion", "Planifica habitaciones")),
    ("I2555002-2.E2", "I2555002",
     "Habilitar la habitación, teniendo en cuenta los requerimientos del huésped, de acuerdo a las políticas y los procedimientos de la empresa.",
     [],
     "Dejar la habitación limpia y lista para el huésped", ("habitacion", "Deja lista la habitación")),
    ("I2555002-3.E1", "I2555002",
     "Cumplir con los estándares de atención al cliente, de acuerdo a las políticas y los procedimientos de la empresa.",
     [],
     "Tratar bien al cliente según las reglas del lugar", ("atencion", "Trata bien al cliente")),
    ("I2555002-3.E2", "I2555002",
     "Atender los requerimientos del cliente, de acuerdo a las políticas y los procedimientos de la empresa.",
     [],
     "Atender lo que pide el cliente", ("atencion", "Atiende pedidos")),
    # --- Salón (ECL I2556002-1 Ayudante de mozo, I2556002-2 Mozo/Mesera, nivel 1)
    ("I2556002-1.E1", "I2556002",
     "Organizar el menaje para el servicio en salón o evento, de acuerdo a las políticas, procedimientos del establecimiento y la normativa correspondiente.",
     ["Verifica las condiciones del menaje", "Abastece la estación de los mozos"],
     "Preparar platos, vasos y cubiertos para el servicio", ("mesa", "Prepara platos y cubiertos")),
    ("I2556002-1.E2", "I2556002",
     "Realizar el montaje y desmontaje del salón o evento, de acuerdo al servicio requerido, las políticas, procedimientos del establecimiento y la normativa correspondiente.",
     ["Acomoda las mesas y sillas en el salón", "Realiza el montaje de las mesas"],
     "Armar y desarmar mesas para el servicio o un evento", ("mesa", "Arma mesas")),
    ("I2556002-2.E1", "I2556002",
     "Asistir al cliente, brindándole información sobre los servicios, productos y ofertas disponibles, de acuerdo a las políticas, procedimientos del establecimiento y la normativa correspondiente.",
     ["Recibe al cliente", "Brinda información sobre los servicios, productos y ofertas", "Anota el pedido en su respectiva comanda"],
     "Recibir al cliente, explicarle lo que hay y tomar su pedido", ("registro", "Toma pedidos")),
    ("I2556002-2.E2", "I2556002",
     "Atender los pedidos del cliente, teniendo en cuenta las políticas, procedimientos del establecimiento y la normativa correspondiente.",
     ["Sirve los alimentos y/o bebidas al cliente", "Resuelve quejas y reclamos", "Entrega el comprobante respectivo y de ser el caso el vuelto"],
     "Servir, resolver quejas y cobrar la cuenta", ("cobro", "Sirve y cobra")),
]


def main():
    base = Path(__file__).resolve().parent.parent / "data"
    for o in OCUPACIONES:
        o.update({"fuente": "Catálogo Nacional de Perfiles Ocupacionales (MTPE)", "tomado": FECHA})
    comps = []
    for codigo, perfil, oficial, criterios, simple, (icono, etiqueta) in E:
        comps.append({"codigo": codigo, "perfil": perfil, "estandar": codigo.split(".")[0],
                      "texto_oficial": oficial, "criterios_clave": criterios,
                      "texto_simple": simple, "sello": {"icono": icono, "etiqueta": etiqueta},
                      "fuente": "PDF del perfil ocupacional " + perfil, "tomado": FECHA})
    # chequeos mínimos
    codigos = [c["codigo"] for c in comps]
    assert len(codigos) == len(set(codigos)), "códigos repetidos"
    perfiles = {o["codigo"] for o in OCUPACIONES}
    assert all(c["perfil"] in perfiles for c in comps)
    for o in OCUPACIONES:
        assert all(any(c["estandar"] == e for c in comps) for e in o["estandares_operativos"]), o["codigo"]
    (base / "ocupaciones.json").write_text(json.dumps(OCUPACIONES, ensure_ascii=False, indent=2), encoding="utf-8")
    (base / "competencias.json").write_text(json.dumps(comps, ensure_ascii=False, indent=2), encoding="utf-8")
    for o in OCUPACIONES:
        n = sum(c["perfil"] == o["codigo"] for c in comps)
        print(f"{o['codigo']} {o['nombre_simple']:35s} {n} sellos")
    print("total", len(comps))


if __name__ == "__main__":
    main()
