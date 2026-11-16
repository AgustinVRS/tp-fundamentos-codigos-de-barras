import re
from decimal import Decimal

from .balanza import CODIGO_PESO_COTO, detalle_peso
from .catalogo import buscar_producto
from .codigos import extraer_codigos
from .prefijos import pais_del_prefijo


PESO_EN_DESCRIPCION = re.compile(
    r"\s*\(\s*[0-9]+(?:[.,][0-9]+)?\s*(?:kg|g)\s*\)\s*$"
    r"|\s+[0-9]+[.,][0-9]+\s*(?:kg|g)\s*$",
    re.IGNORECASE,
)

PRECIO_FINAL = re.compile(r"(?:^|\s)\$?\s*(-?(?:[0-9]{1,3}(?:\.[0-9]{3})+|[0-9]+),[0-9]{2})$")


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
        lineas = bloque.splitlines()
        if nombre == encabezado:
            lineas = lineas[1:]
        for linea in lineas:
            encontrados = extraer_codigos(linea)
            for indice, candidato in enumerate(encontrados):
                inicio = candidato["posicion"] + len(candidato["codigo"])
                fin = encontrados[indice + 1]["posicion"] if indice + 1 < len(encontrados) else len(linea)
                descripcion = linea[inicio:fin].strip()
                precio = PRECIO_FINAL.search(descripcion)
                candidato["descripcion"] = descripcion[:precio.start()].strip() if precio else descripcion
                candidato["precio"] = precio.group(1) if precio else ""
                datos_peso = detalle_peso(candidato, nombre) if es_local(candidato) else None
                if datos_peso:
                    candidato["peso"], candidato["detalle_balanza"] = datos_peso
                    sin_peso = PESO_EN_DESCRIPCION.sub("", candidato["descripcion"]).strip()
                    candidato["descripcion"] = sin_peso or candidato["descripcion"]
                candidatos.append(candidato)
        tickets.append((nombre, candidatos))
    return tickets


def es_local(candidato):
    codigo = candidato["codigo"]
    return candidato.get("tipo") == "EAN-13" and (
        codigo.startswith("2") or CODIGO_PESO_COTO.fullmatch(codigo) is not None
    )


def detalle_gs1(candidato):
    if not candidato["codigo"]:
        return ""
    if es_local(candidato):
        return candidato.get("detalle_balanza") or "Posible código de circulación restringida. Perfil local sin confirmar."
    if candidato["control_leido"] != candidato["control_esperado"]:
        return ""

    codigo = candidato["codigo"]
    tipo = candidato["tipo"]
    prefijo = f"0{codigo}"[:3] if tipo == "UPC-A" else codigo[:3]
    if tipo != "EAN-8" and prefijo.startswith(("02", "04")):
        return "Prefijo de circulación restringida"

    numero = int(prefijo)
    pais = pais_del_prefijo(numero) if tipo != "EAN-8" or numero >= 100 else None
    if pais:
        return f"Prefijo {prefijo} — GS1 {pais}"
    return f"Prefijo {prefijo} — asignación GS1 sin identificar"


def consultar(candidato, productos, fichas=None, *, respaldo_local=False):
    if not candidato["codigo"] or es_local(candidato) or candidato["control_leido"] != candidato["control_esperado"]:
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


def titulo_con_peso(titulo, candidato):
    peso = candidato.get("peso")
    return f"{titulo} ({peso})" if peso else titulo


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


def mostrar_precio(precio, comercio):
    if not precio:
        return "—"
    moneda = re.search(r"\((GBP|EUR|USD|CLP|MXN)\)$", comercio)
    return f"{moneda.group(1)} {precio}" if moneda else f"$ {precio}"


def total_importes(candidatos, comercio):
    precios = [fila["precio"] for fila in candidatos if fila["precio"]]
    if not precios:
        return None
    total = sum(Decimal(precio.replace(".", "").replace(",", ".")) for precio in precios)
    importe = f"{total:,.2f}".translate(str.maketrans(",.", ".,"))
    return mostrar_precio(importe, comercio)
