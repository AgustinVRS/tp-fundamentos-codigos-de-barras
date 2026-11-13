import re

from catalogo import buscar_producto
from codigos import extraer_codigos


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


def consultar(candidato, productos, fichas=None):
    if es_local(candidato) or candidato["control_leido"] != candidato["control_esperado"]:
        return None
    codigo = candidato["codigo"]
    if fichas is not None:
        return fichas.get(codigo, "Sin datos de catálogo en la muestra")
    if codigo not in productos:
        resultado = buscar_producto(codigo)
        if not resultado.startswith(("Falló", "Open Food Facts devolvió")):
            productos[codigo] = resultado
        return resultado
    return productos[codigo]
