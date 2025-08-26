import tkinter as tk;
from tkinter import ttk
from main import *




class ventana_principal:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Ventana de ejemplo")
        self.ventana.geometry("1200x700")
        self.ventana.configure(bg="")
        self.for_archivo = manejo_de_archivos()


        self.notebook = ttk.Notebook(self.ventana)

        self.notbook_archivo = tk.Frame(self.notebook, bg="LightBlue3")
        self.notbook_analizar = tk.Frame(self.notebook, bg="LightBlue3")
        self.notbook_tokens = tk.Frame(self.notebook, bg="LightBlue3")


        self.notebook.add(self.notbook_archivo, text="Inicio")
        self.notebook.add(self.notbook_analizar, text="Analizar txt")
        self.notebook.add(self.notbook_tokens, text="Visualizar Tokens")

        self.boton_insertar_archivo = tk.Button(self.notbook_archivo, text="Insertar archivo", font=("Arial", 25, "bold"), fg="pink4", bg="alice blue", command=lambda:self.iniciar_archivo())
        self.boton_insertar_archivo.pack(pady=20)

        self.texto_name_txt = tk.Label(self.notbook_archivo, text=f"Archivo seleccionado: Nada Aún", font=("Arial", 14), bg="LightBlue3", fg="pink4")
        self.texto_name_txt.pack(pady=10)

        self.notebook.pack(expand=1, fill="both")

        contenedor = tk.Frame(self.notbook_archivo, height=500, width=1000)
        contenedor.pack(pady=65)

        scroll_y = tk.Scrollbar(contenedor, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.canvas = tk.Canvas(contenedor, bg="Azure", yscrollcommand=scroll_y.set, width=1000, height=500, relief="solid")
        self.canvas.pack(fill="both", expand=True)

        scroll_y.config(command=self.canvas.yview)

        def update_scrollregion(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.canvas.bind("<Configure>", update_scrollregion)


        # Analizar txt

        self.texto2 = tk.Label(self.notbook_analizar, text=f"Archivo seleccionado: Nada aun", font=("Arial", 14), bg="LightBlue3", fg="pink4")
        self.texto2.pack(pady=10)

        contenedor_botones = tk.Frame(self.notbook_analizar, bg="LightBlue3")
        contenedor_botones.pack(pady=10)

        boton_analizar = tk.Button(contenedor_botones, text="Analizar Archivo", font=("Arial", 25, "bold"), fg="pink4")
        boton_analizar.grid(row=0, column=0, padx=5, pady=5)

        boton_greporte = tk.Button(contenedor_botones, text="Generar Reporte", font=("Arial", 25, "bold"), fg="pink4")
        boton_greporte.grid(row=0, column=1,padx=5, pady=5)

        contenedor2 = tk.Frame(self.notbook_analizar, height=500, width=1000)
        contenedor2.pack(pady=65)

        scroll_y = tk.Scrollbar(contenedor2, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        self.canvas2 = tk.Canvas(contenedor2, bg="Azure", yscrollcommand=scroll_y.set, width=1000, height=500, relief="solid")
        self.canvas2.pack(fill="both", expand=True)

        scroll_y.config(command=self.canvas2.yview)

        def update_scrollregion(event=None):
            self.canvas2.configure(scrollregion=self.canvas2.bbox("all"))

        self.canvas2.bind("<Configure>", update_scrollregion)

        self.ventana.mainloop()

    



    def iniciar_archivo(self):
        archivo = self.for_archivo.seleccionar_archivo()
        
        if archivo != None:
            self.canvas.create_text(
            10, 10,               
            anchor="nw",           
            text=f"{self.for_archivo.leer_y_mostrar()}",               
            font=("Arial", 12),   
            width=950,            
            fill="black",
            )
            self.texto_name_txt.config(text=f"Archivo seleccionado: {archivo.split('/')[-1]}")

 
   
    

ventana_principal()
