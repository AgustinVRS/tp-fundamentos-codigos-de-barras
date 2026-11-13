from xml.sax.saxutils import escape

from .tickets import detalle_gs1, presentar_producto


def exportar_ticket(destino, archivo, nombre, candidatos, productos):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    from pathlib import Path
    import reportlab
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    fuentes = Path(reportlab.__file__).parent / "fonts"
    pdfmetrics.registerFont(TTFont("Informe-Regular", str(fuentes / "Vera.ttf")))
    pdfmetrics.registerFont(TTFont("Informe-Bold", str(fuentes / "VeraBd.ttf")))

    azul = colors.HexColor("#0C2148")
    oro = colors.HexColor("#FFC832")
    gris = colors.HexColor("#52637B")

    def texto(valor, tamano=10, color=azul, negrita=False, alineacion=0):
        estilo = ParagraphStyle(
            "Informe", fontName="Informe-Bold" if negrita else "Informe-Regular",
            fontSize=tamano, leading=tamano + 4, textColor=color, alignment=alineacion,
        )
        return Paragraph(escape(str(valor)), estilo)

    def decorar(lienzo, doc):
        ancho, alto = A4
        lienzo.setFillColor(azul)
        lienzo.rect(0, alto - 124, ancho, 124, fill=1, stroke=0)
        lienzo.setFillColor(oro)
        lienzo.rect(0, alto - 129, ancho, 5, fill=1, stroke=0)
        escudo = lienzo.beginPath()
        escudo.moveTo(42, alto - 34)
        for x, y in [(96, 34), (91, 76), (69, 94), (47, 76)]:
            escudo.lineTo(x, alto - y)
        escudo.close()
        lienzo.setLineWidth(2)
        lienzo.setStrokeColor(oro)
        lienzo.drawPath(escudo)
        lienzo.setFont("Informe-Bold", 13)
        lienzo.drawCentredString(69, alto - 66, "CABJ")
        for x in (58, 69, 80):
            lienzo.circle(x, alto - 47, 2, fill=1, stroke=0)
        lienzo.setFillColor(colors.white)
        lienzo.setFont("Informe-Bold", 26)
        lienzo.drawString(117, alto - 61, "Boquita Passion")
        lienzo.setFont("Informe-Regular", 11)
        lienzo.drawString(118, alto - 83, "Informe de ticket")
        lienzo.setStrokeColor(oro)
        lienzo.line(42, 48, ancho - 42, 48)
        lienzo.setFillColor(gris)
        lienzo.setFont("Informe-Regular", 9)
        lienzo.drawString(42, 32, "Boquita Passion · Fundamentos Teóricos de Informática")
        lienzo.drawRightString(ancho - 42, 32, f"Página {doc.page}")

    doc = SimpleDocTemplate(str(destino), pagesize=A4, leftMargin=36, rightMargin=36,
                            topMargin=151, bottomMargin=63, title=f"Boquita Passion - {nombre}")
    flujo = [texto(archivo, 9, gris), Spacer(1, 4), texto(nombre, 23, negrita=True), Spacer(1, 16)]
    anchos = (doc.width - 120, 108)
    cabecera = Table([[texto("Producto y validación", negrita=True),
                       texto("Importe", negrita=True, alineacion=2)]], colWidths=anchos)
    cabecera.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF3FA"))]))
    flujo.append(cabecera)
    invalidos = 0
    for candidato in candidatos:
        codigo = candidato["codigo"]
        esperado = candidato["control_esperado"]
        valido = candidato["control_leido"] == esperado
        invalidos += not valido
        control = "Control válido" if valido else f"Control inválido · esperaba {esperado}"
        titulo, detalle_catalogo = presentar_producto(candidato, productos.get(codigo))
        izquierda = [
            texto(titulo, 12, negrita=True),
            texto(f'{codigo} · {candidato["tipo"]}', 9, gris),
            texto(control, 9, gris if valido else colors.HexColor("#A12237")),
        ]
        if asignacion := detalle_gs1(candidato):
            izquierda.append(texto(asignacion, 9, gris))
        if detalle_catalogo:
            izquierda.append(texto(detalle_catalogo, 9, gris))
        precio = candidato["precio"]
        fila = Table([[izquierda, texto(f"$ {precio}" if precio else "—", 12, negrita=True, alineacion=2)]],
                     colWidths=anchos)
        fila.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LINEBELOW", (0, 0), (-1, -1), .5, colors.HexColor("#DFE7F2")),
        ]))
        flujo.append(KeepTogether([fila]))
    flujo.extend([Spacer(1, 12), texto(f"Códigos detectados: {len(candidatos)} · Controles inválidos: {invalidos}", 10, gris)])
    doc.build(flujo, onFirstPage=decorar, onLaterPages=decorar)
