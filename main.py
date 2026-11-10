import re
import barcode
import customtkinter
from tkinter import messagebox
from barcode.writer import ImageWriter
from PIL import Image

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

# --- funcion para cambiar el mensaje y el color del frame ---
def set_message(label, frame, text, color):
    frame.configure(fg_color=("#262626" if color=="green" else "#3b1f1f"))
    label.configure(text=text, text_color=color)

# --- funciones del verificar Estandar-13 ---
def verificar_codigo_EAN13( codigo13):
    #se verifica la entrada
    if validar_entrada_13(codigo13):
        #si la entrada es valida, se verifica el digito de control
        if verificar_digito_control(codigo13):
            set_message(mensaje_label_13, mensaje_frame_13, "El codigo ingresado es valido segun el estandar EAN-13", "green")
        else:
            set_message(mensaje_label_13, mensaje_frame_13, "El digito de control no es valido", "red")            
    else:
        set_message(mensaje_label_13, mensaje_frame_13, "El codigo ingresado no cumple con la cantidad de caracteres, deben ser 13 caracteres", "red")        
    return

def validar_entrada_13( codigo13):
    #con regex
    return re.fullmatch(r"[0-9]{13}", str(codigo13))

def verificar_digito_control( codigo13):
    codigo13 = str(codigo13)
    cuerpo = codigo13[:12]
    digito_real = int(codigo13[-1])
    digito_calc = generar_digito_control(cuerpo)
    return digito_real == digito_calc



# --- funciones del generar Estandar-13 ---
def generar_codigo_EAN13( codigo12):
    if validar_entrada_12(codigo12):
        #Generar digito de control
        digito_control = generar_digito_control(codigo12)
        codigo_completo = str(codigo12) + str(digito_control)
        set_message(mensaje_label_12, mensaje_frame_12, f"El codigo EAN-13 generado es: {codigo_completo}", "green")        
        
        #Codigo de barras
        ean = barcode.get('ean13', codigo_completo, writer=ImageWriter())
        nombre_archivo = ean.save('codigo_ean13')
        messagebox.showinfo("Codigo de Barras Generado", f"El codigo de barras ha sido generado y guardado como {nombre_archivo}")            

        # Mostrar la imagen en la ventana
        img = Image.open(nombre_archivo)
        ctk_img = customtkinter.CTkImage(light_image=img, dark_image=img, size=(300, 150))
        label_codigo.configure(image=ctk_img, text="")
        label_codigo.image = ctk_img  # mantener referencia

    else:
        set_message(mensaje_label_12, mensaje_frame_12, "El codigo ingresado no cumple con la cantidad de caracteres, deben ser 12 caracteres", "red")        
    return

def validar_entrada_12( codigo12):
    #con regex
    return re.fullmatch(r"[0-9]{12}", str(codigo12))




def generar_digito_control( codigo12):
    codigo12 = str(codigo12)
    suma_pares = 0
    suma_impares = 0

    for i, ch in enumerate(codigo12):
        dig = int(ch)
        pos = i + 1
        if pos % 2 == 1:
            suma_impares += dig
        else:
            suma_pares += dig

    total = suma_impares + (suma_pares * 3)
    digito_control = (10 - (total % 10)) % 10
    return digito_control




#Interfaz
app = customtkinter.CTk()
app.title("FTI- Estandar EAN-13")
app.geometry("600x600")

contenedor_fila13 = customtkinter.CTkFrame(app)
contenedor_fila13.pack(pady=15, padx=20, fill="x")

texto_entrada13 = customtkinter.CTkLabel(contenedor_fila13, text="introduzca el codigo EAN-13")
texto_entrada13.pack(padx=25, pady=10)

entrada13 = customtkinter.CTkEntry(contenedor_fila13, placeholder_text="ej: 5901234123457", width=260)
entrada13.pack(side="left", padx=10)

boton13 = customtkinter.CTkButton(contenedor_fila13, text="Verificar codigo", command=lambda: verificar_codigo_EAN13(entrada13.get()))
boton13.pack(side="left", padx=10)

mensaje_frame_13 = customtkinter.CTkFrame(app, corner_radius=10)
mensaje_frame_13.pack(pady=5, padx=20, fill="x")

mensaje_label_13 = customtkinter.CTkLabel(mensaje_frame_13, text="", font=("Arial", 12), anchor="w")
mensaje_label_13.pack(padx=10, pady=5)

contenedor_fila12 = customtkinter.CTkFrame(app)
contenedor_fila12.pack(pady=15, padx=20, fill="x")

texto_entrada12 = customtkinter.CTkLabel(contenedor_fila12, text="introduzca Los 12 digitos del codigo EAN-13 a generar")
texto_entrada12.pack(padx=25, pady=10)

entrada12 = customtkinter.CTkEntry(contenedor_fila12, placeholder_text="ej: 458679582451", width=260)
entrada12.pack(side="left", padx=10)

boton12 = customtkinter.CTkButton(contenedor_fila12, text="Generar codigo", command=lambda: generar_codigo_EAN13(entrada12.get()))
boton12.pack(side="left", padx=10)

mensaje_frame_12 = customtkinter.CTkFrame(app, corner_radius=10)
mensaje_frame_12.pack(pady=5, padx=20, fill="x")

mensaje_label_12 = customtkinter.CTkLabel(mensaje_frame_12, text="", font=("Arial", 12), anchor="w")
mensaje_label_12.pack(padx=10, pady=5)

#crear imagen del codigo de barras
label_codigo = customtkinter.CTkLabel(app, text="")
label_codigo.pack(pady=20)

app.mainloop()
