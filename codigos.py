import re

PATRONES = {
    "EAN-8": re.compile(r"(?<![0-9])([0-9]{7})([0-9])(?![0-9])"),
    "UPC-A": re.compile(r"(?<![0-9])([0-9]{11})([0-9])(?![0-9])"),
    "EAN-13": re.compile(r"(?<![0-9])([0-9]{12})([0-9])(?![0-9])"),
}


def calcular_control(cuerpo):
    suma = 0
    for posicion, digito in enumerate(reversed(cuerpo)):
        peso = 3 if posicion % 2 == 0 else 1
        suma += int(digito) * peso
    return (-suma) % 10


def extraer_codigos(texto):
    candidatos = []
    for tipo, patron in PATRONES.items():
        for coincidencia in patron.finditer(texto):
            cuerpo, control = coincidencia.groups()
            candidatos.append({
                "tipo": tipo,
                "codigo": coincidencia.group(),
                "control_leido": int(control),
                "control_esperado": calcular_control(cuerpo),
                "posicion": coincidencia.start(),
            })
    return sorted(candidatos, key=lambda candidato: candidato["posicion"])
