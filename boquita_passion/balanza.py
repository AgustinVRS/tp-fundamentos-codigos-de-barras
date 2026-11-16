"""Formato de peso observado en Coto, sucursal 184."""

import re

COMERCIO_COTO = re.compile(r"COTO\s*[-–—]?\s*SUCURSAL\s+184", re.IGNORECASE)
CODIGO_PESO_COTO = re.compile(
    r"0?25(?P<producto>[0-9]{5})(?P<gramos>[0-9]{5})[0-9]"
)


def detalle_peso(candidato, comercio):
    if candidato["control_leido"] != candidato["control_esperado"]:
        return None

    coincidencia = CODIGO_PESO_COTO.fullmatch(candidato["codigo"])
    if coincidencia is None:
        return None

    producto = coincidencia["producto"]
    kilos, gramos = divmod(int(coincidencia["gramos"]), 1000)
    peso = f"{kilos},{gramos:03d} kg"
    detalle = f"Formato (peso) · Producto local {producto}"
    if not COMERCIO_COTO.fullmatch(comercio.strip()):
        detalle += " · Interpretación según el formato observado"
    return peso, detalle
