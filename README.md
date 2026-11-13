# Códigos de barras del supermercado

Avance del Tema 1 de Fundamentos Teóricos de Informática. El programa busca candidatos EAN-8, UPC-A y EAN-13 en tickets de texto, verifica el dígito de control y puede consultar el catálogo mundial de alimentos Open Food Facts.

## Requisitos

- Instalá Python 3 si todavía no lo tenés. Verificá la instalación con `python3 --version` en Linux o macOS, o con `py -3 --version` en Windows.
- El programa usa solo la biblioteca estándar de Python. Podés ejecutarlo directamente, sin crear un entorno virtual ni instalar paquetes con `pip`.
- Las bibliotecas de la interfaz gráfica anterior (`customtkinter`, `python-barcode` y Pillow) solo corresponden al prototipo. La entrada del práctico es `main.py`.
- La conexión a internet se usa al activar `--catalogo` o pulsar **Consultar catálogo** en la ventana.

## Ejecución

Descargá el repositorio como ZIP y descomprimilo, o clonalo con Git. Abrí una terminal en la carpeta que contiene `main.py`.

```bash
python3 main.py muestras/tickets.txt
python3 main.py muestras/tickets.txt --catalogo
```

En Windows también podés usar `py -3` en lugar de `python3`. La primera ejecución funciona sin conexión. Con `--catalogo`, el programa busca nombre y marca para los candidatos comerciales con control válido. Si falta la ficha o falla la conexión, imprime el motivo y continúa.

## Entrada y salida

Pasá la ruta de un archivo UTF-8. Cada ticket puede incluir texto libre y se separa del siguiente con una línea que contiene `---`.

```text
3017620422003 NUTELLA 8.500,00
---
7791234567890 EJEMPLO CON CONTROL INVÁLIDO
```

```text
Ticket 1
  3017620422003 | EAN-13 | control válido | NUTELLA | $ 8.500,00
Ticket 2
  7791234567890 | EAN-13 | control inválido (leído 0, esperado 8) | EJEMPLO CON CONTROL INVÁLIDO
    Prefijo 779 — GS1 Argentina
```

## Archivos

- `main.py` lee el archivo, separa los tickets y presenta los resultados.
- `codigos.py` contiene las tres expresiones regulares y calcula el control módulo 10.
- `catalogo.py` consulta Open Food Facts por el código completo.
- `muestras/tickets.txt` es una muestra técnica con los tres formatos y casos de control inválido, posible código local y longitud fuera del alcance.

## Alcance del avance

Se informa el prefijo 779 como asignación de GS1 Argentina. La cobertura de otros rangos GS1 queda pendiente. Los EAN-13 que empiezan con 2 se marcan como posibles códigos de circulación restringida. Para interpretar sus campos queda por documentar el perfil de un comercio con etiquetas reales. Para la entrega quedan pendientes los tickets reales anonimizados.

[Documentación de Open Food Facts](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/tutorials/scanning-barcodes/)

## Ventana de escritorio

```bash
python3 main.py muestras/tickets.txt --interfaz
```

La ventana carga el archivo y selecciona el primer ticket. Usá **Abrir otro archivo** para cambiar de muestra y **Consultar catálogo** para buscar los productos del ticket seleccionado. También podés combinar `--interfaz` con `--catalogo` para consultar el primer ticket al abrirlo.

Usá como primera línea de cada bloque el nombre del comercio. Si el bloque empieza con una línea de producto con código, se muestra un nombre genérico, como «Ticket 1». Los encabezados de la muestra técnica se muestran tal como aparecen en el archivo. La descripción y el precio se leen de la línea del producto. Los precios de ejemplo son ilustrativos y usan coma decimal, como `1.250,00`.

La ventana requiere Tkinter y una sesión de escritorio. Podés comprobar si Tkinter está disponible con `python3 -m tkinter`. En Debian o Ubuntu se instala con `sudo apt install python3-tk` si falta. En Windows usá `py -3` en los comandos.

`interfaz.py` implementa la ventana. `tickets.py` comparte la lectura de bloques y las reglas de consulta entre la interfaz y la CLI.


## Demostración del catálogo sin conexión

```bash
python3 main.py muestras/tickets.txt --catalogo-local muestras/catalogo.json
```

Agregá `--interfaz` para usar las mismas fichas en la ventana. El JSON guarda resultados de la consulta de muestra a Open Food Facts, indexados por código completo. Si un código no figura en el archivo, el programa indica que falta en la muestra local y sigue procesando el ticket.
