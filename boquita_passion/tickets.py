import re

from .catalogo import buscar_producto
from .codigos import extraer_codigos


PRECIO_FINAL = re.compile(r"(?:^|\s)\$?\s*((?:[0-9]{1,3}(?:\.[0-9]{3})+|[0-9]+),[0-9]{2})$")


def analizar_tickets(texto):
    bloques = re.split(r"(?m)^[^\S\n]*---[^\S\n]*$", texto)
    tickets = []
    for bloque in bloques:
        bloque = bloque.strip()
        if not bloque:
            continue
        encabezado = bloque.splitlines()[0].strip()
        nombre = f"Ticket {len(tickets) + 1}" if extraer_codigos(encabezado) else encabezado
        candidatos = []
        for linea in bloque.splitlines():
            encontrados = extraer_codigos(linea)
            for indice, candidato in enumerate(encontrados):
                inicio = candidato["posicion"] + len(candidato["codigo"])
                fin = encontrados[indice + 1]["posicion"] if indice + 1 < len(encontrados) else len(linea)
                descripcion = linea[inicio:fin].strip()
                precio = PRECIO_FINAL.search(descripcion)
                candidato["descripcion"] = descripcion[:precio.start()].strip() if precio else descripcion
                candidato["precio"] = precio.group(1) if precio else ""
                candidatos.append(candidato)
        tickets.append((nombre, candidatos))
    return tickets


def es_local(candidato):
    return candidato["tipo"] == "EAN-13" and candidato["codigo"].startswith("2")


def detalle_gs1(candidato):
    if es_local(candidato):
        return "Posible código de circulación restringida. Perfil local sin confirmar."
    if candidato["tipo"] == "EAN-13" and candidato["codigo"].startswith("779"):
        return "Prefijo 779 — GS1 Argentina"
    return ""


def consultar(candidato, productos, fichas=None, *, respaldo_local=False):
    if es_local(candidato) or candidato["control_leido"] != candidato["control_esperado"]:
        return None
    codigo = candidato["codigo"]
    if fichas is not None and not respaldo_local:
        ficha = fichas.get(codigo)
        if not ficha:
            return "Sin datos de catálogo en la muestra"
        return f"{ficha} (muestra local)" if ficha != "Producto sin ficha" else ficha
    if codigo in productos:
        resultado = productos[codigo]
    else:
        resultado = buscar_producto(codigo)
        if not resultado.startswith(("Falló", "Open Food Facts devolvió")):
            productos[codigo] = resultado

    if respaldo_local and (
        resultado == "Producto sin ficha" or resultado.startswith(("Falló", "Open Food Facts devolvió"))
    ):
        ficha = fichas.get(codigo)
        if ficha and ficha != "Producto sin ficha":
            return f"{ficha} (muestra local)"
    return resultado


def presentar_producto(candidato, ficha):
    """Devuelve el título y el detalle del catálogo para la ventana y el PDF."""
    descripcion = candidato["descripcion"].strip()
    titulo = descripcion or "Código sin descripción"
    if not ficha:
        return titulo, None

    contenido = ficha.removesuffix(" (muestra local)")
    nombre, separador, marca = contenido.partition(" | ")
    nombre = nombre.strip()
    if descripcion or not separador or not nombre or nombre == "Nombre sin informar":
        return titulo, f"Catálogo · {ficha}"

    fuente = "Catálogo local" if contenido != ficha else "Open Food Facts"
    return nombre, f"{fuente} · {marca}" if marca else fuente
