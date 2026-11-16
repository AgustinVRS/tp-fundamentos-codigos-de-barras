# Boquita Passion

**Analizador de tickets de supermercado** · Fundamentos Teóricos de Informática, Tema 1

Extrae códigos **EAN-8, UPC-A y EAN-13** con expresiones regulares, verifica su dígito de control y muestra los productos y precios por comercio. También permite consultar **Open Food Facts** y exportar el ticket seleccionado en PDF.

## Inicio rápido

Descargá el repositorio, descomprimilo si bajaste un ZIP y abrí una terminal en la carpeta que contiene `main.py`.

```bash
python3 main.py
```

Se abre la ventana con la muestra. La demo intenta consultar Open Food Facts y usa el catálogo guardado si la consulta falla o falta la ficha. Desde la ventana podés cambiar de ticket, abrir otro archivo o consultar el catálogo del ticket seleccionado. Al guardar cambios en el archivo abierto, la ventana actualiza los tickets automáticamente.

Necesitás **Python 3**. Para la ventana, comprobá Tkinter con `python3 -m tkinter`. Si falta en Debian o Ubuntu, instalalo con `sudo apt install python3-tk`. En Windows, usá `py -3` en lugar de `python3`.

## Comandos para la defensa

| Para | Comando |
| --- | --- |
| Analizar por consola, sin consultar el catálogo | `python3 main.py muestras/tickets_demo.txt` |
| Abrir la ventana con Open Food Facts en vivo | `python3 main.py --catalogo` |
| Abrir la ventana con el catálogo sin conexión | `python3 main.py muestras/tickets_demo.txt --interfaz --catalogo-local muestras/catalogo.json` |
| Ver todas las opciones | `python3 main.py --help` |

## Formato del ticket

Usá un archivo `.txt` en UTF-8. Poné el nombre del comercio en la primera línea de cada bloque y separá los tickets con una línea que contenga solo `---`. En una línea de producto, podés poner la descripción después del código y el precio al final, con coma decimal.

```text
SUPERMERCADO EJEMPLO
3017620422003 NUTELLA 8.500,00
---
KIOSCO LA ESQUINA
77900104 CARAMELOS 300,00
```

La muestra del repositorio es ilustrativa. Si el ticket trae un código sin descripción, la ventana y el PDF pueden mostrar el nombre que devuelva el catálogo. El precio se lee del ticket.

## Exportar un PDF

La exportación requiere **ReportLab**. Instalalo una sola vez en un entorno virtual. En Linux o macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install reportlab
.venv/bin/python main.py
```

En Windows, creá el entorno con `py -3 -m venv .venv` y usá `.venv\Scripts\python.exe` en los dos comandos siguientes. Una vez abierta la ventana, seleccioná el ticket y pulsá **Descargar PDF**. El informe incluye las fichas del catálogo que ya estén visibles.

## Archivos principales

- `main.py` — punto de entrada para la consola y la ventana.
- `boquita_passion/` — extracción, validación, lectura de tickets, catálogo, interfaz y exportación.
- `muestras/` — ticket de demostración y fichas del catálogo sin conexión.

El encabezado identifica al comercio. Para códigos con control válido, el programa informa la organización GS1 consultando la tabla local de rangos de `boquita_passion/prefijos.py`, sin pedir el país ni usar internet. Por ejemplo, muestra `779` para Argentina y `060` para Estados Unidos. Esa asignación señala quién asignó la numeración. El país de fabricación requiere otros datos. Los EAN-13 que empiezan con `2` se marcan como posibles códigos de balanza.


## Productos de peso variable

El perfil documentado se observó en **Coto, sucursal 184**. La expresión regular en `boquita_passion/balanza.py` separa el prefijo `25`, cinco dígitos de producto, cinco de peso en gramos y el dígito de control EAN-13.

| Código | Identificador local | Peso embebido |
| --- | --- | --- |
| `2515271001505` | `15271` | `00150` → 0,150 kg |
| `2515271001468` | `15271` | `00146` → 0,146 kg |

Probá ambos ejemplos con `python3 main.py muestras/tickets_reales.txt`. El peso se lee del código. Los renglones sin un código compatible quedan fuera del análisis. El formato se aplica a códigos válidos con prefijo `25`, incluido el número impreso con un cero de relleno delante. En otros comercios el peso se muestra como una interpretación según el formato observado. Para otros prefijos o controles inválidos se conserva el aviso de circulación restringida. El peso embebido se muestra entre paréntesis junto al nombre del producto.
