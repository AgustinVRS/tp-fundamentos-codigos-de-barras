#funcion para validar la entrada de 12 digitos - Creacion de codigo EAN
#funcion para crear el digito de control
#funcion para crear el codigo de barras

#funcion para validar la entrada de 13 digitos - Verificacion codigo EAN
#funcion para validar el digito de control

#interfaz
#pedir codigo EAN-13
#validar el digito de control
#pedir codigo EAN-12
#boton para validar e imprimir el codigo de barras
#imprimir el codigo de barras una vez generado el codigo, usar python barcode


import re
import barcode
import customtkinter

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

def calcular_digito_control(codigo12):
    suma = 0

    #multiplicar digitos y sumar
    for i, num in enumerate(codigo12):
        digito = int(num)
        if ((i +1) % 2 == 0):   #posicion par (izq a der)   #impar (der a iz)
            suma += digito * 3 
        else:                   #posicion impar
            suma += digito * 1 

    #calcular digito de control
    digito_control = (10 - (suma % 10)) % 10    # % 10 por si suma mod 10 = 10

    return digito_control

# --- funciones del verificar Estandar-13 ---
def verificar_codigo_EAN13( codigo13):
    #se verifica la entrada
    if validar_entrada_13(codigo13):
        #si la entrada es valida, se verifica el digito de control
        if verificar_digito_control(codigo13):
            print("Codigo EAN13 valido")
            pass #digito de control validado
        else:
            print("Codigo EAN13 no valido")
            pass #digito de control no valido            
    else:
        print("Entrada no valida")
        pass #entrada no valida
    #devolver resultado
    return

def validar_entrada_13( codigo13):
    #con regex
    return re.fullmatch(r"\d{13}", codigo13)

def verificar_digito_control( codigo13):
    #hacer calculos
    codigo_sin_digito = codigo13[:12]
    digito_recibido = int(codigo13[12])

    digito_control = calcular_digito_control(codigo_sin_digito)

    return digito_recibido == digito_control

# --- funciones del generar Estandar-13 ---
def generar_codigo_EAN13( codigo12):
    #se verifica la entrada
    if validar_entrada_12(codigo12):
        #si la entrada es valida, se genera el digito de control
        generar_digito_control(codigo12)
        print("Codigo EAN13 generado")
        pass #digito de control generado            
    else:
        print("Entrada no valida")
        pass #entrada no valida
    #devolver resultado
    return

def validar_entrada_12( codigo12):
    #con regex
    return re.fullmatch(r"\d{12}", codigo12)    

def generar_digito_control( codigo12):
    digito_control = 0

    digito_control = calcular_digito_control(codigo12)

    return digito_control

app = customtkinter.CTk()
app.title("FTI- Estandar EAN-13")
app.geometry("400x500")

contenedor_fila13 = customtkinter.CTkFrame(app)
contenedor_fila13.pack(pady=25)

texto_entrada13 = customtkinter.CTkLabel(contenedor_fila13, text="introduzca el codigo EAN-13")
texto_entrada13.pack(padx=25, pady=10)

entrada13 = customtkinter.CTkEntry(contenedor_fila13, placeholder_text="ej: (buscar un codigo valido)")
entrada13.pack(side="left", padx=10)

boton13 = customtkinter.CTkButton(contenedor_fila13, text="Verificar codigo", command=lambda: verificar_codigo_EAN13(entrada13.get()))
boton13.pack(side="left", padx=10)

contenedor_fila12 = customtkinter.CTkFrame(app)
contenedor_fila12.pack(pady=25)

texto_entrada12 = customtkinter.CTkLabel(contenedor_fila12, text="introduzca Los 12 digitos del codigo EAN-13 a generar")
texto_entrada12.pack(padx=25, pady=10)

entrada12 = customtkinter.CTkEntry(contenedor_fila12, placeholder_text="ej: 458679582451")
entrada12.pack(side="left", padx=10)

boton12 = customtkinter.CTkButton(contenedor_fila12, text="Generar codigo", command=lambda: generar_codigo_EAN13(entrada12.get()))
boton12.pack(side="left", padx=10)

#crear imagen del codigo de barras

app.mainloop()

