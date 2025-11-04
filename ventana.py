import tkinter as tk
from tkinter import ttk
from analizador import AnalizadorLexico
from main import manejo_de_archivos
from sintactico import AnalizadorSintactico
from semantico import AnalizadorSemantico

class ventana_principal:
    def __init__(self):
        self.analizador_sintactico = AnalizadorSintactico()
        self.analizador_semantico = AnalizadorSemantico()
        self.ventana = tk.Tk()
        self.ventana.title("Analizador Léxico, Sintáctico y Semántico")
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

        # Botón para editar archivo
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

        # Pestaña Analizar txt - Organización vertical
        self.texto2 = tk.Label(self.notbook_analizar, text=f"Archivo seleccionado: Nada aun", font=("Arial", 14), bg="LightBlue3", fg="pink4")
        self.texto2.pack(pady=10)

        contenedor_botones = tk.Frame(self.notbook_analizar, bg="LightBlue3")
        contenedor_botones.pack(pady=10)

        self.boton_analizar = tk.Button(contenedor_botones, text="Analizar Archivo", font=("Arial", 25, "bold"), fg="pink4", command=lambda:self.analizar_archivo())
        self.boton_analizar.grid(row=0, column=0, padx=5, pady=5)

        self.boton_greporte = tk.Button(contenedor_botones, text="Generar Reporte", font=("Arial", 25, "bold"), fg="pink4", command=lambda:self.generar_reporte())
        self.boton_greporte.grid(row=0, column=1,padx=5, pady=5)

        # Contenedor principal con scroll para los 3 análisis
        contenedor_principal = tk.Frame(self.notbook_analizar, bg="LightBlue3")
        contenedor_principal.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame con scroll para los análisis
        frame_scroll = tk.Frame(contenedor_principal, bg="LightBlue3")
        frame_scroll.pack(fill="both", expand=True)

        scroll_y_principal = tk.Scrollbar(frame_scroll, orient="vertical")
        scroll_y_principal.pack(side="right", fill="y")

        self.canvas_principal = tk.Canvas(frame_scroll, bg="LightBlue3", yscrollcommand=scroll_y_principal.set)
        self.canvas_principal.pack(fill="both", expand=True)

        scroll_y_principal.config(command=self.canvas_principal.yview)

        # Frame interno para contener los 3 análisis
        self.frame_analisis = tk.Frame(self.canvas_principal, bg="LightBlue3")
        self.canvas_principal.create_window((0, 0), window=self.frame_analisis, anchor="nw")

        def update_scrollregion_principal(event=None):
            self.canvas_principal.configure(scrollregion=self.canvas_principal.bbox("all"))
        self.frame_analisis.bind("<Configure>", update_scrollregion_principal)

        # ========== ANÁLISIS LÉXICO ==========
        frame_lexico = tk.LabelFrame(self.frame_analisis, text="🔍 ANÁLISIS LÉXICO", font=("Arial", 12, "bold"), 
                                   bg="lightcyan", fg="darkblue", relief="raised", bd=2, width=1100, height=200)
        frame_lexico.pack(fill="x", padx=10, pady=5)
        frame_lexico.pack_propagate(False)  # Evita que se reduzca el tamaño

        contenedor_lexico = tk.Frame(frame_lexico, bg="lightcyan")
        contenedor_lexico.pack(fill="both", expand=True, padx=5, pady=5)

        scroll_y_lexico = tk.Scrollbar(contenedor_lexico, orient="vertical")
        scroll_y_lexico.pack(side="right", fill="y")

        self.texto_lexico = tk.Text(contenedor_lexico, bg="lightcyan", yscrollcommand=scroll_y_lexico.set, 
                                   font=("Courier", 8), wrap="word", width=130, height=8)
        self.texto_lexico.pack(fill="both", expand=True)

        scroll_y_lexico.config(command=self.texto_lexico.yview)

        # ========== ANÁLISIS SINTÁCTICO ==========
        frame_sintactico = tk.LabelFrame(self.frame_analisis, text="📐 ANÁLISIS SINTÁCTICO", font=("Arial", 12, "bold"), 
                                       bg="lightgreen", fg="darkgreen", relief="raised", bd=2, width=1100, height=200)
        frame_sintactico.pack(fill="x", padx=10, pady=5)
        frame_sintactico.pack_propagate(False)

        contenedor_sintactico = tk.Frame(frame_sintactico, bg="lightgreen")
        contenedor_sintactico.pack(fill="both", expand=True, padx=5, pady=5)

        scroll_y_sintactico = tk.Scrollbar(contenedor_sintactico, orient="vertical")
        scroll_y_sintactico.pack(side="right", fill="y")

        self.texto_sintactico = tk.Text(contenedor_sintactico, bg="lightgreen", yscrollcommand=scroll_y_sintactico.set, 
                                      font=("Courier", 8), wrap="word", width=130, height=8)
        self.texto_sintactico.pack(fill="both", expand=True)

        scroll_y_sintactico.config(command=self.texto_sintactico.yview)

        # ========== ANÁLISIS SEMÁNTICO ==========
        frame_semantico = tk.LabelFrame(self.frame_analisis, text="🎯 ANÁLISIS SEMÁNTICO", font=("Arial", 12, "bold"), 
                                      bg="lightyellow", fg="darkred", relief="raised", bd=2, width=1100, height=250)
        frame_semantico.pack(fill="x", padx=10, pady=5)
        frame_semantico.pack_propagate(False)

        contenedor_semantico = tk.Frame(frame_semantico, bg="lightyellow")
        contenedor_semantico.pack(fill="both", expand=True, padx=5, pady=5)

        scroll_y_semantico = tk.Scrollbar(contenedor_semantico, orient="vertical")
        scroll_y_semantico.pack(side="right", fill="y")

        self.texto_semantico = tk.Text(contenedor_semantico, bg="lightyellow", yscrollcommand=scroll_y_semantico.set, 
                                     font=("Courier", 8), wrap="word", width=130, height=10)
        self.texto_semantico.pack(fill="both", expand=True)

        scroll_y_semantico.config(command=self.texto_semantico.yview)

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
        """
        if not self.for_archivo.contenido:
            top = tk.Toplevel(self.ventana)
            top.title("Editar - Sin archivo cargado")
            tk.Label(top, text="No hay archivo cargado para editar.").pack(padx=20, pady=20)
            tk.Button(top, text="Cerrar", command=top.destroy).pack(pady=10)
            return

        editor = tk.Toplevel(self.ventana)
        editor.title("Editor de archivo")
        editor.geometry("900x600")

        texto = tk.Text(editor, wrap="none", font=("Courier", 11))
        texto.pack(fill="both", expand=True)

        texto.insert("1.0", self.for_archivo.contenido)

        boton_frame = tk.Frame(editor)
        boton_frame.pack(pady=6)

        def guardar_cambios():
            nuevo_contenido = texto.get("1.0", tk.END).rstrip('\n')
            self.for_archivo.contenido = nuevo_contenido

            self.canvas.delete("all")
            self.canvas.create_text(
                10, 10,
                anchor="nw",
                text=nuevo_contenido,
                font=("Arial", 12),
                width=950,
                fill="black",
            )

            nombre_archivo = (self.for_archivo.ruta_archivo.split('/')[-1]) if self.for_archivo.ruta_archivo else "Archivo editado (no guardado)"
            self.texto_name_txt.config(text=f"Archivo seleccionado: {nombre_archivo}")
            self.texto2.config(text=f"Archivo seleccionado: {nombre_archivo}")

            if self.for_archivo.ruta_archivo:
                try:
                    with open(self.for_archivo.ruta_archivo, 'w', encoding='utf-8') as f:
                        f.write(nuevo_contenido)
                except Exception as e:
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
            # Limpiar todos los textos antes de mostrar resultados
            self.texto_lexico.delete(1.0, tk.END)
            self.texto_sintactico.delete(1.0, tk.END)
            self.texto_semantico.delete(1.0, tk.END)
            
            # Ejecutar análisis
            tokens, errores_lexicos = self.analizador.analizar_archivo(self.for_archivo.contenido)
            errores_sintacticos = self.analizador_sintactico.analizar(tokens)
            errores_semanticos, tabla_simbolos = self.analizador_semantico.analizar(tokens)
            
            # Mostrar en cada texto correspondiente
            self._mostrar_analisis_lexico(tokens, errores_lexicos)
            self._mostrar_analisis_sintactico(errores_sintacticos)
            self._mostrar_analisis_semantico(errores_semanticos, tabla_simbolos)
            
            # Guardar datos para el reporte
            self.tokens_analizados = tokens
            self.errores_lexicos = errores_lexicos
            self.errores_sintacticos = errores_sintacticos
            self.errores_semanticos = errores_semanticos
            self.tabla_simbolos = tabla_simbolos

    def _mostrar_analisis_lexico(self, tokens, errores_lexicos):
        """Muestra el análisis léxico en su texto"""
        resultado = "TOKENS RECONOCIDOS:\n"
        resultado += "=" * 20 + "\n\n"
        
        if errores_lexicos:
            resultado += "❌ ERRORES LÉXICOS ENCONTRADOS:\n"
            resultado += "-" * 28 + "\n"
            for error in errores_lexicos:
                resultado += f"• {error}\n"
            resultado += f"\nTotal de errores: {len(errores_lexicos)}\n\n"
        else:
            resultado += "✅ No se encontraron errores léxicos\n\n"

        resultado += "TOKENS POR LÍNEA:\n"
        resultado += "-" * 15 + "\n"
        
        # Agrupar tokens por línea
        tokens_por_linea = {}
        for token, tipo, linea in tokens:
            if linea not in tokens_por_linea:
                tokens_por_linea[linea] = []
            tokens_por_linea[linea].append((token, tipo))
        
        for linea in sorted(tokens_por_linea.keys()):
            resultado += f"\nLínea {linea}:\n"
            for token, tipo in tokens_por_linea[linea]:
                resultado += f"   '{token}' → {tipo}\n"
        
        self.texto_lexico.insert(1.0, resultado)

    def _mostrar_analisis_sintactico(self, errores_sintacticos):
        """Muestra el análisis sintáctico en su texto"""
        resultado = "ESTRUCTURA SINTÁCTICA:\n"
        resultado += "=" * 25 + "\n\n"
        
        if errores_sintacticos:
            resultado += "❌ ERRORES SINTÁCTICOS:\n"
            resultado += "-" * 22 + "\n"
            for error in errores_sintacticos:
                resultado += f"• {error}\n"
            resultado += f"\nTotal de errores: {len(errores_sintacticos)}\n"
        else:
            resultado += "✅ Estructura sintáctica correcta\n\n"
            resultado += "✓ Balanceo de símbolos correcto\n"
            resultado += "✓ Estructuras de control válidas\n"
            resultado += "✓ Declaraciones bien formadas\n"
        
        resultado += "\nVERIFICACIONES REALIZADAS:\n"
        resultado += "-" * 25 + "\n"
        resultado += "• Llaves {}, paréntesis (), comillas \"\"\n"
        resultado += "• Estructuras si, mientras, para\n"
        resultado += "• Declaraciones de variables\n"
        resultado += "• Puntos y coma\n"
        
        self.texto_sintactico.insert(1.0, resultado)

    def _mostrar_analisis_semantico(self, errores_semanticos, tabla_simbolos):
        """Muestra el análisis semántico en su texto"""
        resultado = "ANÁLISIS DE TIPOS Y VARIABLES:\n"
        resultado += "=" * 30 + "\n\n"
        
        if errores_semanticos:
            resultado += "❌ ERRORES SEMÁNTICOS:\n"
            resultado += "-" * 22 + "\n"
            for error in errores_semanticos:
                resultado += f"• {error}\n"
            resultado += f"\nTotal de errores: {len(errores_semanticos)}\n\n"
        else:
            resultado += "✅ Semántica correcta\n\n"

        resultado += "TABLA DE SÍMBOLOS:\n"
        resultado += "-" * 18 + "\n"
        if tabla_simbolos:
            for variable, tipo in tabla_simbolos.items():
                resultado += f"• {variable} : {tipo}\n"
            resultado += f"\nTotal variables: {len(tabla_simbolos)}\n"
        else:
            resultado += "No hay variables declaradas\n"
        
        # Resumen de tipos
        if tabla_simbolos:
            resultado += "\nDISTRIBUCIÓN DE TIPOS:\n"
            resultado += "-" * 22 + "\n"
            tipos_count = {}
            for tipo in tabla_simbolos.values():
                tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
            for tipo, count in tipos_count.items():
                resultado += f"• {tipo}: {count} variable(s)\n"
        
        self.texto_semantico.insert(1.0, resultado)

    def generar_reporte(self):
        if hasattr(self, 'tokens_analizados'):
            reporte = self.analizador.generar_reporte(self.tokens_analizados)
            
            # Agregar información completa al reporte
            reporte += "\n" + "="*60 + "\n"
            reporte += "REPORTE GENERAL - ANÁLISIS COMPLETO\n"
            reporte += "="*60 + "\n\n"
            
            # Resumen de cada análisis
            reporte += "RESUMEN DE ANÁLISIS:\n"
            reporte += "-" * 20 + "\n"
            
            # Léxico
            if hasattr(self, 'errores_lexicos'):
                reporte += f"Léxico: {'❌' if self.errores_lexicos else '✅'} {len(self.errores_lexicos) if self.errores_lexicos else 0} errores\n"
            
            # Sintáctico
            if hasattr(self, 'errores_sintacticos'):
                reporte += f"Sintáctico: {'❌' if self.errores_sintacticos else '✅'} {len(self.errores_sintacticos) if self.errores_sintacticos else 0} errores\n"
            
            # Semántico
            if hasattr(self, 'errores_semanticos'):
                reporte += f"Semántico: {'❌' if self.errores_semanticos else '✅'} {len(self.errores_semanticos) if self.errores_semanticos else 0} errores\n"
            
            # Tabla de símbolos completa
            if hasattr(self, 'tabla_simbolos') and self.tabla_simbolos:
                reporte += "\nTABLA DE SÍMBOLOS COMPLETA:\n"
                reporte += "-" * 25 + "\n"
                for variable, tipo in self.tabla_simbolos.items():
                    reporte += f"  {variable} : {tipo}\n"
            
            # Limpiar y mostrar reporte
            self.texto_tokens.delete(1.0, tk.END)
            self.texto_tokens.insert(1.0, reporte)
            
            # Cambiar a la pestaña de tokens
            self.notebook.select(2)

# ejecutar ventana
ventana_principal()