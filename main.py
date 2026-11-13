import argparse
import json
from pathlib import Path

from tickets import analizar_tickets, consultar, detalle_gs1


def main():
    parser = argparse.ArgumentParser(description="Analiza códigos de barras en tickets.")
    parser.add_argument("archivo", type=Path, help="Archivo de tickets en UTF-8")
    modo_catalogo = parser.add_mutually_exclusive_group()
    modo_catalogo.add_argument("--catalogo-local", type=Path, metavar="JSON", help="Usa fichas guardadas sin internet")
    modo_catalogo.add_argument("--catalogo", action="store_true", help="Consulta Open Food Facts")
    parser.add_argument("--interfaz", action="store_true", help="Abre la ventana de escritorio")
    opciones = parser.parse_args()

    try:
        texto = opciones.archivo.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        parser.error(f"No se pudo leer el archivo: {error}")

    fichas = None
    if opciones.catalogo_local is not None:
        try:
            fichas = json.loads(opciones.catalogo_local.read_text(encoding="utf-8"))
            if not isinstance(fichas, dict) or not all(isinstance(valor, str) for valor in fichas.values()):
                raise ValueError("Se espera un objeto con códigos y fichas de texto")
        except (OSError, ValueError) as error:
            parser.error(f"No se pudo cargar el catálogo local: {error}")

    tickets = analizar_tickets(texto)
    if opciones.interfaz:
        try:
            from interfaz import abrir_interfaz

            abrir_interfaz(opciones.archivo, tickets, opciones.catalogo or fichas is not None, fichas)
        except ImportError:
            parser.error("La interfaz necesita Tkinter. Consultá el README.")
        except RuntimeError as error:
            parser.error(str(error))
        return

    productos = {}
    for numero, (_, candidatos) in enumerate(tickets, start=1):
        print(f"Ticket {numero}")
        if not candidatos:
            print("  Sin candidatos EAN-8, UPC-A o EAN-13.")
        for candidato in candidatos:
            codigo = candidato["codigo"]
            tipo = candidato["tipo"]
            leido = candidato["control_leido"]
            esperado = candidato["control_esperado"]
            valido = leido == esperado
            estado = "control válido" if valido else f"control inválido (leído {leido}, esperado {esperado})"
            campos = [codigo, tipo, estado]
            if candidato["descripcion"]:
                campos.append(candidato["descripcion"])
            if candidato["precio"]:
                campos.append(f'$ {candidato["precio"]}')
            print("  " + " | ".join(campos))
            detalle = detalle_gs1(candidato)
            if detalle:
                print(f"    {detalle}")
            if opciones.catalogo or fichas is not None:
                producto = consultar(candidato, productos, fichas)
                if producto is not None:
                    print(f"    Catálogo: {producto}")


if __name__ == "__main__":
    main()
