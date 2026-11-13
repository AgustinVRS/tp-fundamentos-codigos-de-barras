import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from tickets import analizar_tickets, consultar, detalle_gs1


def abrir_interfaz(archivo, tickets, consultar_al_abrir=False, fichas=None):
    try:
        ventana = tk.Tk()
    except tk.TclError as error:
        raise RuntimeError(f"No se pudo abrir la ventana: {error}") from error

    ventana.title("Analizador de tickets")
    ventana.geometry("1260x570")
    ventana.minsize(760, 360)
    ventana.columnconfigure(0, weight=1)
    ventana.rowconfigure(1, weight=1)
    azul = "#0B1E42"
    azul_claro = "#17386A"
    oro = "#FFCF32"
    fondo = "#EEF3FA"
    tinta = "#142646"
    ventana.configure(background=fondo)
    estilo = ttk.Style(ventana)
    estilo.theme_use("clam")
    estilo.configure("TFrame", background=fondo)
    estilo.configure("TLabel", background=fondo, foreground=tinta)
    estilo.configure("Marca.TFrame", background=azul)
    estilo.configure("Marca.TLabel", background=azul, foreground=oro, font=("TkDefaultFont", 19, "bold"))
    estilo.configure("Archivo.TLabel", background=azul, foreground="#DBE7FC")
    estilo.configure("Oro.TButton", background=oro, foreground=azul, padding=(16, 10))
    estilo.map("Oro.TButton", background=[("disabled", "#D5DDEA"), ("active", "#FFE082")])
    estilo.configure("Abrir.TButton", background=azul_claro, foreground="white", padding=(16, 10))
    estilo.map("Abrir.TButton", background=[("active", "#254A81")])
    estilo.configure("Ticket.TButton", background="white", foreground=tinta, anchor="w", padding=(14, 12))
    estilo.map("Ticket.TButton", background=[("selected", "#FFF0B5"), ("active", "#DEE9F8")])
    for nombre in ("Oro", "Abrir", "Ticket"):
        estilo.layout(f"{nombre}.TButton", [
            ("Button.padding", {"sticky": "nsew", "children": [
                ("Button.focus", {"sticky": "nsew", "children": [
                    ("Button.label", {"sticky": "nsew"}),
                ]}),
            ]}),
        ])
    estilo.configure("Detalle.TFrame", background="white")
    estilo.configure("Comercio.TLabel", background="white", foreground=tinta,
                     font=("TkDefaultFont", 16, "bold"))
    estilo.configure("Treeview", rowheight=46, background="white", fieldbackground="white",
                     foreground=tinta, borderwidth=0, relief="flat")
    estilo.layout("Treeview.Heading", [
        ("Treeheading.cell", {"sticky": "nswe"}),
        ("Treeheading.padding", {"sticky": "nswe", "children": [
            ("Treeheading.text", {"sticky": "we"}),
        ]}),
    ])
    estilo.configure("Treeview.Heading", background="#EAF0F8", foreground=tinta, padding=(12, 10))
    estilo.configure("TScrollbar", background="#CED9EA", troughcolor="#F2F5FA",
                     borderwidth=0, arrowsize=11)

    barra = ttk.Frame(ventana, padding=(20, 14), style="Marca.TFrame")
    barra.grid(sticky="ew")
    barra.columnconfigure(0, weight=1)
    ttk.Label(barra, text="Boquita Passion", style="Marca.TLabel").grid(row=0, column=0, sticky="w")
    archivo_actual = tk.StringVar(value=archivo.name)
    ttk.Label(barra, textvariable=archivo_actual, style="Archivo.TLabel").grid(row=1, column=0, sticky="w")

    panel = ttk.Frame(ventana)
    panel.grid(row=1, sticky="nsew", padx=22, pady=(22, 0))
    panel.rowconfigure(0, weight=1)
    panel.columnconfigure(1, weight=1)
    lateral = ttk.Frame(panel, padding=(0, 0, 18, 0))
    lateral.grid(row=0, column=0, sticky="ns")
    detalle = ttk.Frame(panel, padding=16, style="Detalle.TFrame")
    detalle.grid(row=0, column=1, sticky="nsew")

    ttk.Label(lateral, text="Tickets", font=("TkDefaultFont", 12, "bold")).pack(anchor="w", pady=(0, 12))
    lista = ttk.Frame(lateral)
    lista.pack(fill="both", expand=True)
    seleccion = tk.IntVar(value=-1)

    detalle.columnconfigure(0, weight=1)
    detalle.rowconfigure(1, weight=1)
    comercio = tk.StringVar()
    ttk.Label(detalle, textvariable=comercio, style="Comercio.TLabel").grid(
        row=0, column=0, sticky="w", pady=(0, 16)
    )
    columnas = ("codigo", "descripcion", "precio", "tipo", "control", "gs1", "producto")
    tabla = ttk.Treeview(detalle, columns=columnas, show="headings", selectmode="none")
    for columna, titulo, ancho in zip(
        columnas, ("Código", "Descripción del ticket", "Precio", "Tipo", "Control", "Asignación GS1", "Catálogo"),
        (115, 166, 95, 65, 145, 155, 190)
    ):
        tabla.heading(columna, text=titulo)
        tabla.column(columna, width=ancho, minwidth=55, stretch=True, anchor="e" if columna == "precio" else "w")
    tabla.tag_configure("invalido", foreground="#a52130", background="#FFF0F1")
    tabla.tag_configure("alterna", background="#F0F5FD")
    tabla.grid(row=1, column=0, sticky="nsew")
    vertical = ttk.Scrollbar(detalle, command=tabla.yview)
    vertical.grid(row=1, column=1, sticky="ns")
    horizontal = ttk.Scrollbar(detalle, orient="horizontal", command=tabla.xview)
    horizontal.grid(row=2, column=0, sticky="ew")
    def ajustar_scroll(barra, primero, ultimo):
        barra.set(primero, ultimo)
        if float(primero) == 0 and float(ultimo) == 1:
            barra.grid_remove()
        else:
            barra.grid()

    tabla.configure(
        yscrollcommand=lambda primero, ultimo: ajustar_scroll(vertical, primero, ultimo),
        xscrollcommand=lambda primero, ultimo: ajustar_scroll(horizontal, primero, ultimo),
    )

    estado = tk.StringVar()
    ttk.Label(ventana, textvariable=estado, padding=14).grid(row=2, sticky="w")
    resultados = {}
    cache = {}
    ejecutor = ThreadPoolExecutor(max_workers=1)

    def mostrar(_evento=None):
        tabla.delete(*tabla.get_children())
        indice = seleccion.get()
        if indice < 0:
            comercio.set("Sin tickets")
            estado.set("El archivo está vacío.")
            return
        nombre, candidatos = tickets[indice]
        comercio.set(nombre)
        for fila, candidato in enumerate(candidatos):
            codigo = candidato["codigo"]
            esperado = candidato["control_esperado"]
            valido = candidato["control_leido"] == esperado
            control = "Válido" if valido else f"Inválido · esperaba {esperado}"
            asignacion = detalle_gs1(candidato)
            if asignacion.startswith("Posible"):
                asignacion = "Perfil local sin confirmar"
            precio = f'$ {candidato["precio"]}' if candidato["precio"] else "—"
            tabla.insert(
                "", "end",
                values=(
                    codigo, candidato["descripcion"] or "—", precio, candidato["tipo"],
                    control, asignacion or "—", resultados.get(indice, {}).get(codigo) or "—",
                ),
                tags=(("alterna",) if fila % 2 else ()) if valido else ("invalido",),
            )
        estado.set(f"{len(candidatos)} códigos detectados")

    def cargar_lista():
        for boton in lista.winfo_children():
            boton.destroy()
        seleccion.set(0 if tickets else -1)

        def elegir(indice):
            seleccion.set(indice)
            for numero, boton in enumerate(lista.winfo_children()):
                boton.state(["selected" if numero == indice else "!selected"])
            mostrar()

        for indice, (nombre, candidatos) in enumerate(tickets):
            cantidad = len(candidatos)
            etiqueta = "código" if cantidad == 1 else "códigos"
            boton = ttk.Button(
                lista, text=f"{nombre}\n{cantidad} {etiqueta}", width=25,
                style="Ticket.TButton", command=lambda indice=indice: elegir(indice),
            )
            boton.pack(fill="x", pady=(0, 8))
            if indice == 0:
                boton.state(["selected"])
        mostrar()

    def abrir_archivo():
        nonlocal tickets
        ruta = filedialog.askopenfilename(parent=ventana, filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*")])
        if not ruta:
            return
        try:
            nuevo = Path(ruta)
            tickets = analizar_tickets(nuevo.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as error:
            messagebox.showerror("No se pudo leer el archivo", str(error), parent=ventana)
            return
        resultados.clear()
        archivo_actual.set(nuevo.name)
        cargar_lista()

    def consultar_catalogo():
        indice = seleccion.get()
        if indice < 0:
            return
        candidatos = tickets[indice][1]
        boton_catalogo.state(["disabled"])
        boton_abrir.state(["disabled"])
        estado.set("Cargando fichas locales…" if fichas is not None else "Consultando Open Food Facts…")

        def buscar():
            return {candidato["codigo"]: consultar(candidato, cache, fichas) for candidato in candidatos}

        tarea = ejecutor.submit(buscar)

        def actualizar():
            if not tarea.done():
                ventana.after(100, actualizar)
                return
            boton_catalogo.state(["!disabled"])
            boton_abrir.state(["!disabled"])
            try:
                resultados[indice] = tarea.result()
            except Exception as error:
                messagebox.showerror("Falló la consulta", str(error), parent=ventana)
            mostrar()

        actualizar()

    boton_abrir = ttk.Button(barra, text="Abrir otro archivo", command=abrir_archivo, style="Abrir.TButton")
    boton_abrir.grid(row=0, column=1, padx=8)
    boton_catalogo = ttk.Button(barra, text="Consultar catálogo", command=consultar_catalogo, style="Oro.TButton")
    boton_catalogo.grid(row=0, column=2)
    cargar_lista()
    if consultar_al_abrir:
        ventana.after(0, consultar_catalogo)
    try:
        ventana.mainloop()
    finally:
        ejecutor.shutdown(wait=False, cancel_futures=True)
