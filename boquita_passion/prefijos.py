"""Asignaciones geográficas GS1 para consultas sin conexión."""

# Fuentes: https://www.gs1.org/standards/id-keys/company-prefix
# y https://www.gs1tw.org/twct/web/prefixlist.jsp
RANGOS = (
    (0, 19, "Estados Unidos"),
    (30, 39, "Estados Unidos"),
    (60, 139, "Estados Unidos"),
    (300, 379, "Francia"),
    (400, 440, "Alemania"),
    (450, 459, "Japón"),
    (460, 469, "Rusia"),
    (490, 499, "Japón"),
    (500, 509, "Reino Unido"),
    (520, 521, "Grecia"),
    (540, 549, "Bélgica y Luxemburgo"),
    (570, 579, "Dinamarca"),
    (600, 601, "Sudáfrica"),
    (640, 649, "Finlandia"),
    (680, 681, "China"),
    (690, 699, "China"),
    (700, 709, "Noruega"),
    (730, 739, "Suecia"),
    (754, 755, "Canadá"),
    (760, 769, "Suiza"),
    (770, 771, "Colombia"),
    (778, 779, "Argentina"),
    (789, 790, "Brasil"),
    (800, 839, "Italia"),
    (840, 849, "España"),
    (868, 869, "Turquía"),
    (870, 879, "Países Bajos"),
    (880, 881, "Corea del Sur"),
    (900, 919, "Austria"),
    (930, 939, "Australia"),
    (940, 949, "Nueva Zelanda"),
)

PREFIJOS = {
    380: "Bulgaria", 383: "Eslovenia", 385: "Croacia", 387: "Bosnia y Herzegovina",
    389: "Montenegro", 470: "Kirguistán", 471: "Taiwán", 474: "Estonia",
    475: "Letonia", 476: "Azerbaiyán", 477: "Lituania", 478: "Uzbekistán",
    479: "Sri Lanka", 480: "Filipinas", 481: "Bielorrusia", 482: "Ucrania",
    483: "Turkmenistán", 484: "Moldavia", 485: "Armenia", 486: "Georgia",
    487: "Kazajistán", 488: "Tayikistán", 489: "Hong Kong", 528: "Líbano",
    529: "Chipre", 530: "Albania", 531: "Macedonia del Norte", 535: "Malta",
    539: "Irlanda", 560: "Portugal", 569: "Islandia", 590: "Polonia",
    594: "Rumania", 599: "Hungría", 603: "Ghana", 604: "Senegal",
    607: "Omán", 608: "Baréin", 609: "Mauricio", 611: "Marruecos",
    613: "Argelia", 615: "Nigeria", 616: "Kenia", 617: "Camerún",
    618: "Costa de Marfil", 619: "Túnez", 620: "Tanzania", 621: "Siria",
    622: "Egipto", 624: "Libia", 625: "Jordania", 626: "Irán",
    627: "Kuwait", 628: "Arabia Saudita", 629: "Emiratos Árabes Unidos",
    630: "Catar", 631: "Namibia", 729: "Israel", 740: "Guatemala",
    741: "El Salvador", 742: "Honduras", 743: "Nicaragua", 744: "Costa Rica",
    745: "Panamá", 746: "República Dominicana", 750: "México", 759: "Venezuela",
    773: "Uruguay", 775: "Perú", 777: "Bolivia", 780: "Chile",
    784: "Paraguay", 786: "Ecuador", 850: "Cuba", 858: "Eslovaquia",
    859: "Chequia", 860: "Serbia", 865: "Mongolia", 867: "Corea del Norte",
    883: "Myanmar", 884: "Camboya", 885: "Tailandia", 888: "Singapur",
    890: "India", 893: "Vietnam", 896: "Pakistán", 899: "Indonesia",
    955: "Malasia", 958: "Macao",
}


def pais_del_prefijo(prefijo):
    for desde, hasta, pais in RANGOS:
        if desde <= prefijo <= hasta:
            return pais
    return PREFIJOS.get(prefijo)
