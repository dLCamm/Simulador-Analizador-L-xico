import tkinter as tk
from tkinter import ttk
from analizador import AnalizadorLexico
from main import manejo_de_archivos
from sintactico import AnalizadorSintactico
from semantico import AnalizadorSemantico  # nuevo

class ventana_principal:
    def __init__(self):
        self.analizador_sintactico = AnalizadorSintactico()
        self.analizador_semantico = AnalizadorSemantico()  # instancia semántico
        self.ventana = tk.Tk()
        self.ventana.title("Analizador Léxico")
        self.ventana.geometry("1200x700")
        self.ventana.configure(bg="")
        self.for_archivo = manejo_de_archivos()
        self.analizador = AnalizadorLexico()

        self.notebook = ttk.Notebook(self.ventana)

        self.notbook_archivo = tk.Frame(self.notebook, bg="LightBlue3")
        self.notbook_analizar = tk.Frame(self.notebook, bg="LightBlue3")
        self.notbook_tokens = tk.Frame(self.notebook, bg="LightBlue3")

        self.notebook.add(self.notbook_archivo, text="Inicio")
        self.notebook.add(self.notbook_analizar, text="Analizar txt")
        self.notebook.add(self.notbook_tokens, text="Visualizar Tokens")

        # Botón para insertar archivo
        self.boton_insertar_archivo = tk.Button(
            self.notbook_archivo,
            text="Insertar archivo",
            font=("Arial", 25, "bold"),
            fg="pink4",
            bg="alice blue",
            command=lambda: self.iniciar_archivo()
        )
        self.boton_insertar_archivo.pack(pady=20)

        # Botón para editar archivo (nuevo, mantiene diseño cercano al original)
        self.boton_editar_archivo = tk.Button(
            self.notbook_archivo,
            text="Editar archivo",
            font=("Arial", 16, "bold"),
            fg="pink4",
            bg="alice blue",
            command=lambda: self.abrir_editor()
        )
        self.boton_editar_archivo.pack(pady=2)

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

        self.boton_analizar = tk.Button(contenedor_botones, text="Analizar Archivo", font=("Arial", 25, "bold"), fg="pink4", command=lambda:self.analizar_archivo())
        self.boton_analizar.grid(row=0, column=0, padx=5, pady=5)

        self.boton_greporte = tk.Button(contenedor_botones, text="Generar Reporte", font=("Arial", 25, "bold"), fg="pink4", command=lambda:self.generar_reporte())
        self.boton_greporte.grid(row=0, column=1,padx=5, pady=5)

        contenedor2 = tk.Frame(self.notbook_analizar, height=500, width=1000)
        contenedor2.pack(pady=65)

        scroll_y2 = tk.Scrollbar(contenedor2, orient="vertical")
        scroll_y2.pack(side="right", fill="y")

        self.canvas2 = tk.Canvas(contenedor2, bg="Azure", yscrollcommand=scroll_y2.set, width=1000, height=500, relief="solid")
        self.canvas2.pack(fill="both", expand=True)

        scroll_y2.config(command=self.canvas2.yview)

        def update_scrollregion2(event=None):
            self.canvas2.configure(scrollregion=self.canvas2.bbox("all"))

        self.canvas2.bind("<Configure>", update_scrollregion2)

        # Frame para Visualizar Tokens
        contenedor3 = tk.Frame(self.notbook_tokens, height=600, width=1100)
        contenedor3.pack(pady=20)

        scroll_y3 = tk.Scrollbar(contenedor3, orient="vertical")
        scroll_y3.pack(side="right", fill="y")

        self.texto_tokens = tk.Text(contenedor3, bg="Azure", yscrollcommand=scroll_y3.set, width=110, height=40, relief="solid", font=("Courier", 10))
        self.texto_tokens.pack(fill="both", expand=True)

        scroll_y3.config(command=self.texto_tokens.yview)

        self.ventana.mainloop()

    def iniciar_archivo(self):
        archivo = self.for_archivo.seleccionar_archivo()
        
        if archivo != None:
            contenido = self.for_archivo.leer_archivo()
            
            # Limpiar canvas antes de agregar nuevo contenido
            self.canvas.delete("all")
            
            # Mostrar contenido en el canvas
            self.canvas.create_text(
                10, 10,               
                anchor="nw",           
                text=contenido,               
                font=("Arial", 12),   
                width=950,            
                fill="black",
            )
            nombre_archivo = archivo.split('/')[-1]
            self.texto_name_txt.config(text=f"Archivo seleccionado: {nombre_archivo}")
            self.texto2.config(text=f"Archivo seleccionado: {nombre_archivo}")

    def abrir_editor(self):
        """
        Abre una ventana para editar el contenido del archivo actualmente cargado.
        Al guardar, actualiza self.for_archivo.contenido y actualiza la vista en canvas.
        Si el archivo fue seleccionado desde disco, preguntamos para sobrescribirlo; por simplicidad,
        aquí sobrescribimos directamente el archivo si existe, pero la operación está envuelta en try/except.
        """
        if not self.for_archivo.contenido:
            # No hay nada que editar
            top = tk.Toplevel(self.ventana)
            top.title("Editar - Sin archivo cargado")
            tk.Label(top, text="No hay archivo cargado para editar.").pack(padx=20, pady=20)
            tk.Button(top, text="Cerrar", command=top.destroy).pack(pady=10)
            return

        # Crear ventana de edición
        editor = tk.Toplevel(self.ventana)
        editor.title("Editor de archivo")
        editor.geometry("900x600")

        texto = tk.Text(editor, wrap="none", font=("Courier", 11))
        texto.pack(fill="both", expand=True)

        # rellenar con contenido actual
        texto.insert("1.0", self.for_archivo.contenido)

        boton_frame = tk.Frame(editor)
        boton_frame.pack(pady=6)

        def guardar_cambios():
            nuevo_contenido = texto.get("1.0", tk.END).rstrip('\n')
            # actualizar contenido en el objeto de manejo de archivos
            self.for_archivo.contenido = nuevo_contenido

            # actualizar vista en canvas principal (Inicio)
            self.canvas.delete("all")
            self.canvas.create_text(
                10, 10,
                anchor="nw",
                text=nuevo_contenido,
                font=("Arial", 12),
                width=950,
                fill="black",
            )

            # actualizar texto en pestaña Analizar
            nombre_archivo = (self.for_archivo.ruta_archivo.split('/')[-1]) if self.for_archivo.ruta_archivo else "Archivo editado (no guardado)"
            self.texto_name_txt.config(text=f"Archivo seleccionado: {nombre_archivo}")
            self.texto2.config(text=f"Archivo seleccionado: {nombre_archivo}")

            # si existe ruta de archivo, sobrescribir (intentamos guardar)
            if self.for_archivo.ruta_archivo:
                try:
                    with open(self.for_archivo.ruta_archivo, 'w', encoding='utf-8') as f:
                        f.write(nuevo_contenido)
                except Exception as e:
                    # mostrar advertencia pero continuar
                    aviso = tk.Toplevel(editor)
                    aviso.title("Error al guardar")
                    tk.Label(aviso, text=f"No se pudo sobrescribir el archivo:\n{e}").pack(padx=20, pady=20)
                    tk.Button(aviso, text="Cerrar", command=aviso.destroy).pack(pady=8)

            editor.destroy()

        def cancelar():
            editor.destroy()

        btn_guardar = tk.Button(boton_frame, text="Guardar cambios", command=guardar_cambios, bg="lightgreen", font=("Arial", 12, "bold"))
        btn_guardar.grid(row=0, column=0, padx=8)

        btn_cancel = tk.Button(boton_frame, text="Cancelar", command=cancelar, bg="lightgray", font=("Arial", 12))
        btn_cancel.grid(row=0, column=1, padx=8)

    def analizar_archivo(self):
        if self.for_archivo.contenido:
            # Limpiar canvas antes de mostrar resultados
            self.canvas2.delete("all")
            
            tokens, errores = self.analizador.analizar_archivo(self.for_archivo.contenido)
            
            resultado = "RESULTADO DEL ANÁLISIS LÉXICO (PALABRA POR PALABRA)\n"
            resultado += "=" * 60 + "\n\n"
            
            if errores:
                resultado += "ERRORES ENCONTRADOS:\n"
                resultado += "=" * 30 + "\n"
                for error in errores:
                    resultado += error + "\n"
                resultado += "\n"
            else:
                resultado += "✓ No se encontraron errores léxicos\n\n"

            # para lo sintactico
            errores_sintacticos = self.analizador_sintactico.analizar(tokens)

            if errores_sintacticos:
                resultado += "ERRORES SINTÁCTICOS:\n"
                resultado += "-" * 30 + "\n"
                for error in errores_sintacticos:
                    resultado += error + "\n"
                resultado += "\n"
            else:
                resultado += "✓ No se encontraron errores sintácticos\n\n"

            # Análisis semántico (se ejecuta aunque haya errores sintácticos; reporta lo que pueda)
            errores_semanticos, tabla_simbolos = self.analizador_semantico.analizar(tokens)

            if errores_semanticos:
                resultado += "ERRORES SEMÁNTICOS:\n"
                resultado += "-" * 30 + "\n"
                for error in errores_semanticos:
                    resultado += error + "\n"
                resultado += "\n"
            else:
                resultado += "✓ No se encontraron errores semánticos\n\n"

            resultado += "TOKENS RECONOCIDOS (POR LÍNEA):\n"
            resultado += "=" * 40 + "\n"
            
            # Agrupar tokens por línea
            tokens_por_linea = {}
            for token, tipo, linea in tokens:
                if linea not in tokens_por_linea:
                    tokens_por_linea[linea] = []
                tokens_por_linea[linea].append((token, tipo))
            
            for linea in sorted(tokens_por_linea.keys()):
                resultado += f"\nLínea {linea}:\n"
                for token, tipo in tokens_por_linea[linea]:
                    resultado += f"  {token} -> {tipo}\n"
            
            # Mostrar resultado en el canvas
            self.canvas2.create_text(
                10, 10,               
                anchor="nw",           
                text=resultado,               
                font=("Courier", 9),   # Font más pequeño para más contenido
                width=980,            
                fill="black",
            )
            
            # Guardar tokens para el reporte
            self.tokens_analizados = tokens
            self.errores_encontrados = errores

    def generar_reporte(self):
        if hasattr(self, 'tokens_analizados'):
            reporte = self.analizador.generar_reporte(self.tokens_analizados)
            
            # Limpiar y mostrar reporte en la pestaña de tokens
            self.texto_tokens.delete(1.0, tk.END)
            self.texto_tokens.insert(1.0, reporte)
            
            # Cambiar a la pestaña de tokens
            self.notebook.select(2)

# ejecutar ventana
ventana_principal()
