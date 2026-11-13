import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

URL_PRODUCTO = "https://world.openfoodfacts.org/api/v2/product"
AGENTE = "FTI-CodigosDeBarras/1.0 (trabajo practico universitario)"


def buscar_producto(codigo):
    solicitud = Request(
        f"{URL_PRODUCTO}/{codigo}.json?fields=product_name,brands",
        headers={"User-Agent": AGENTE},
    )
    try:
        with urlopen(solicitud, timeout=5) as respuesta:
            datos = json.load(respuesta)
    except HTTPError as error:
        if error.code == 404:
            return "Producto sin ficha"
        return f"Falló la consulta (HTTP {error.code})"
    except (URLError, TimeoutError):
        return "Falló la conexión con Open Food Facts"
    except (ValueError, UnicodeError):
        return "Open Food Facts devolvió una respuesta inválida"

    if not isinstance(datos, dict):
        return "Open Food Facts devolvió una respuesta inválida"
    if datos.get("status") == 0:
        return "Producto sin ficha"

    producto = datos.get("product")
    if not isinstance(producto, dict):
        return "Open Food Facts devolvió una respuesta inválida"
    nombre = producto.get("product_name") or "Nombre sin informar"
    marca = producto.get("brands") or "Marca sin informar"
    return f"{nombre} | {marca}"
