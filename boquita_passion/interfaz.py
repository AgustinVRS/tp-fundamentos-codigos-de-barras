import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .informe import exportar_ticket
from .tickets import analizar_tickets, consultar, detalle_gs1, presentar_producto


def abrir_interfaz(archivo, tickets, consultar_al_abrir=False, fichas=None, *, respaldo_local=False):
    try:
        ventana = tk.Tk()
    except tk.TclError as error:
        raise RuntimeError(f"No se pudo abrir la ventana: {error}") from error

    ventana.title("Analizador de tickets")
    ventana.geometry("1000x600")
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
    estilo.configure("Producto.TLabel", background="white", foreground=tinta,
                     font=("TkDefaultFont", 11, "bold"))
    estilo.configure("Meta.TLabel", background="white", foreground="#52637B")
    estilo.configure("Invalido.TLabel", background="white", foreground="#A12237")
    estilo.configure("Separador.TFrame", background="#DCE4EE")
    estilo.configure("TScrollbar", background="#CED9EA", troughcolor="#F2F5FA",
                     borderwidth=0, arrowsize=11)

    tk.Frame(ventana, background=oro, height=4).grid(row=0, sticky="new")
    barra = ttk.Frame(ventana, padding=(20, 14), style="Marca.TFrame")
    barra.grid(row=0, sticky="ew", pady=(4, 0))
    barra.columnconfigure(0, weight=1)
    ttk.Label(barra, text="Boquita Passion", style="Marca.TLabel").grid(row=0, column=0, sticky="w")
    archivo_actual = tk.StringVar(value=f"Analizador de tickets · {archivo.name}")
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
    lienzo = tk.Canvas(detalle, background="white", highlightthickness=0, width=1, height=1)
    lienzo.grid(row=1, column=0, columnspan=2, sticky="nsew")
    filas = ttk.Frame(lienzo, style="Detalle.TFrame")
    contenido = lienzo.create_window(0, 0, window=filas, anchor="nw")
    vertical = ttk.Scrollbar(detalle, command=lienzo.yview)
    vertical.grid(row=1, column=2, sticky="ns")

    def ajustar_scroll(primero, ultimo):
        vertical.set(primero, ultimo)
        if float(primero) == 0 and float(ultimo) == 1:
            vertical.grid_remove()
        else:
            vertical.grid()

    def ajustar_ancho(evento):
        lienzo.itemconfigure(contenido, width=evento.width)
        for etiqueta in textos:
            etiqueta.configure(wraplength=max(160, evento.width - 195))

    def desplazar(evento):
        pasos = -1 if evento.num == 4 or evento.delta > 0 else 1
        lienzo.yview_scroll(pasos, "units")

    textos = []
    lienzo.configure(yscrollcommand=ajustar_scroll)
    lienzo.bind("<Configure>", ajustar_ancho)
    filas.bind("<Configure>", lambda _: lienzo.configure(scrollregion=lienzo.bbox("all")))
    for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        lienzo.bind(evento, desplazar)

    estado = tk.StringVar()
    ttk.Label(ventana, textvariable=estado, padding=14).grid(row=2, sticky="w")
    resultados = {}
    cache = {}
    ejecutor = ThreadPoolExecutor(max_workers=1)

    def mostrar(_evento=None):
        for fila in filas.winfo_children():
            fila.destroy()
        textos.clear()
        lienzo.yview_moveto(0)
        indice = seleccion.get()
        if indice < 0:
            comercio.set("Sin tickets")
            estado.set("El archivo está vacío.")
            return
        nombre, candidatos = tickets[indice]
        comercio.set(nombre)
        for candidato in candidatos:
            codigo = candidato["codigo"]
            esperado = candidato["control_esperado"]
            valido = candidato["control_leido"] == esperado
            control = "Válido" if valido else f"Inválido · esperaba {esperado}"
            asignacion = detalle_gs1(candidato)
            if asignacion.startswith("Posible"):
                asignacion = "Perfil local sin confirmar"
            precio = f'$ {candidato["precio"]}' if candidato["precio"] else "—"
            ttk.Frame(filas, height=1, style="Separador.TFrame").pack(fill="x")
            fila = ttk.Frame(filas, padding=(0, 13), style="Detalle.TFrame")
            fila.pack(fill="x")
            fila.columnconfigure(0, weight=1)

            def agregar(texto, estilo, renglon, columna=0):
                etiqueta = ttk.Label(fila, text=texto, style=estilo, justify="left")
                etiqueta.grid(row=renglon, column=columna, sticky="w" if columna == 0 else "e",
                              padx=(0, 14) if columna == 0 else (0, 0), pady=(0, 3))
                if columna == 0:
                    etiqueta.configure(wraplength=max(160, lienzo.winfo_width() - 195))
                    textos.append(etiqueta)
                for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                    etiqueta.bind(evento, desplazar)

            ficha = resultados.get(indice, {}).get(codigo)
            titulo, detalle_catalogo = presentar_producto(candidato, ficha)
            agregar(titulo, "Producto.TLabel", 0)
            agregar(precio, "Producto.TLabel", 0, 1)
            meta = f'{codigo} · {candidato["tipo"]}'
            agregar(f"{meta} · {asignacion}" if asignacion else meta, "Meta.TLabel", 1)
            agregar(control, "Meta.TLabel" if valido else "Invalido.TLabel", 1, 1)
            if detalle_catalogo:
                agregar(detalle_catalogo, "Meta.TLabel", 2)
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
        archivo_actual.set(f"Analizador de tickets · {nuevo.name}")
        cargar_lista()

    def consultar_catalogo():
        indice = seleccion.get()
        if indice < 0:
            return
        candidatos = tickets[indice][1]
        boton_catalogo.state(["disabled"])
        boton_abrir.state(["disabled"])
        estado.set("Cargando fichas locales…" if fichas is not None and not respaldo_local else "Consultando Open Food Facts…")

        def buscar():
            return {candidato["codigo"]: consultar(candidato, cache, fichas, respaldo_local=respaldo_local) for candidato in candidatos}

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

    def guardar_pdf():
        indice = seleccion.get()
        if indice < 0:
            return
        nombre, candidatos = tickets[indice]
        ruta = filedialog.asksaveasfilename(
            parent=ventana, defaultextension=".pdf", initialfile=f"ticket-{indice + 1}.pdf",
            filetypes=[("Informe PDF", "*.pdf")],
        )
        if not ruta:
            return
        try:
            exportar_ticket(ruta, archivo_actual.get().split(" · ", 1)[1], nombre,
                            candidatos, resultados.get(indice, {}))
        except ImportError:
            messagebox.showerror("Exportación PDF", "Instalá ReportLab con python3 -m pip install reportlab.", parent=ventana)
        except OSError as error:
            messagebox.showerror("No se pudo guardar el PDF", str(error), parent=ventana)
        else:
            estado.set(f"PDF guardado · {Path(ruta).name}")

    boton_abrir = ttk.Button(barra, text="Abrir otro archivo", command=abrir_archivo, style="Abrir.TButton")
    boton_abrir.grid(row=0, column=1, padx=8)
    acciones = ttk.Frame(detalle, style="Detalle.TFrame")
    acciones.grid(row=0, column=1, sticky="e", padx=(12, 0), pady=(0, 16))
    boton_catalogo = ttk.Button(acciones, text="Consultar catálogo", command=consultar_catalogo)
    boton_catalogo.pack(side="left", padx=(0, 8))
    ttk.Button(acciones, text="Descargar PDF", command=guardar_pdf, style="Oro.TButton").pack(side="left")
    cargar_lista()
    if consultar_al_abrir:
        ventana.after(0, consultar_catalogo)
    try:
        ventana.mainloop()
    finally:
        ejecutor.shutdown(wait=False, cancel_futures=True)
