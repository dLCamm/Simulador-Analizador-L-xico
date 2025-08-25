import tkinter as tk
from tkinter import filedialog

class manejo_de_archivos:
    def __init__(self):
        self.ruta_archivo = None
        self.contenido = None
    
    def seleccionar_archivo(self):
        #Abre el explorador de archivos para seleccionar un archivo
        root = tk.Tk()
        root.withdraw() 
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de texto",
            filetypes=[("Archivos TXT", "*.txt")]
        )
        root.destroy()
        
        self.ruta_archivo = archivo if archivo else None
        return self.ruta_archivo
    
    #Lee el contenido de un archivo .txt 
    def leer_archivo(self, ruta_archivo=None):
        ruta = ruta_archivo or self.ruta_archivo
        if not ruta:
            return "No se ha seleccionado un archivo"
        
        try:
            with open(ruta, 'r', encoding='utf-8') as archivo:
                self.contenido = archivo.read()
            return self.contenido
        except Exception as error_contenido:
            mensaje_de_error = f"Error al leer archivo: {str(error_contenido)}"
            self.contenido = mensaje_de_error
            return mensaje_de_error
        
    #Muestra el contenido del archivo en pantalla
    def mostrar_contenido(self, contenido=None):
        texto = contenido or self.contenido
        if not texto:
            print("No hay contenido para mostrar")
            return
    
        print("CONTENIDO DEL ARCHIVO:")
        print(texto)
        
    # combina las 2 funciones para el boton de leer y mostrar informacion
    def leer_y_mostrar(self, ruta_archivo=None):
        contenido = self.leer_archivo(ruta_archivo)
        self.mostrar_contenido(contenido)
        return contenido
