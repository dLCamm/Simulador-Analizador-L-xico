import re

class AnalizadorSintactico:
    def __init__(self):
        self.variables = set()
        self.errores = []
        self.palabras_reservadas_pseint = {
            'algoritmo', 'finalgoritmo', 'proceso', 'finproceso',
            'definir', 'como', 'entero', 'real', 'caracter', 'logico',
            'escribir', 'leer', 'si', 'entonces', 'sino', 'finsi',
            'para', 'hasta', 'con', 'paso', 'hacer', 'finpara',
            'mientras', 'finmientras', 'repetir',
            'segun', 'de', 'otro', 'finsegun',
            'dimension', 'verdadero', 'falso'
        }
        self.tokens_completos = []

    def analizar(self, tokens):
        self.errores = []
        self.variables = set()
        self.tokens_completos = tokens
        pila_parentesis = []
        pila_corchetes = []
        pila_cadenas = []
        estructuras_abiertas = []

        # Agrupar tokens por línea
        lineas_tokens = {}
        for token, tipo, linea in tokens:
            if linea not in lineas_tokens:
                lineas_tokens[linea] = []
            lineas_tokens[linea].append((token, tipo, linea))

        # Verificar tokens individuales
        for i, (token, tipo, linea) in enumerate(tokens):
            token_lower = token.lower()

            # --- Verificar signos de apertura/cierre ---
            if token == "(":
                pila_parentesis.append((linea, i))
            elif token == ")":
                if not pila_parentesis:
                    self.errores.append(f"Línea {linea}: ')' sin apertura previa")
                else:
                    pila_parentesis.pop()

            elif token == "[":
                pila_corchetes.append((linea, i))
            elif token == "]":
                if not pila_corchetes:
                    self.errores.append(f"Línea {linea}: ']' sin apertura previa")
                else:
                    pila_corchetes.pop()

            # --- Verificar cadenas ---
            elif token.startswith('"') and token.endswith('"'):
                continue  # Cadena completa
            elif token.startswith('"') and not token.endswith('"'):
                pila_cadenas.append(linea)
            elif token.endswith('"') and not token.startswith('"'):
                if not pila_cadenas:
                    self.errores.append(f"Línea {linea}: cierre de cadena sin apertura previa")
                else:
                    pila_cadenas.pop()

            # --- Reservadas usadas como variables ---
            if tipo == "Identificador" and token_lower in self.palabras_reservadas_pseint:
                self.errores.append(f"Línea {linea}: '{token}' es palabra reservada, no puede usarse como identificador")

            # --- Verificar declaraciones ---
            if token_lower == "definir":
                self._verificar_definicion_pseint(tokens, i, linea)

        # Analizar estructuras por líneas
        self._verificar_estructuras_pseint(lineas_tokens, estructuras_abiertas)

        # --- Validar cierres finales ---
        self._validar_cierres_finales(pila_parentesis, pila_corchetes, pila_cadenas, estructuras_abiertas)
        return self.errores

    def _verificar_estructuras_pseint(self, lineas_tokens, estructuras_abiertas):
        """Analiza estructuras de control agrupadas por líneas"""
        
        for numero_linea in sorted(lineas_tokens.keys()):
            tokens_linea = lineas_tokens[numero_linea]
            if not tokens_linea:
                continue
                
            token_primero = tokens_linea[0][0].lower()
            
            # === ESTRUCTURAS DE APERTURA ===
            if token_primero in ["algoritmo", "proceso", "si", "mientras", "segun", "repetir", "para"]:
                estructuras_abiertas.append((token_primero, numero_linea))

                # Validación específica para PARA - CORREGIDA
                if token_primero == "para":
                    # Convertir toda la línea a minúsculas para búsqueda
                    tokens_texto = [tok[0].lower() for tok in tokens_linea]
                    
                    # Buscar '<' seguido de '-' como asignación (para tokenización separada)
                    tiene_asignacion = False
                    for i in range(len(tokens_texto) - 1):
                        if tokens_texto[i] == '<' and tokens_texto[i + 1] == '-':
                            tiene_asignacion = True
                            break
                    
                    # También buscar si está unido en algún token
                    if not tiene_asignacion:
                        tiene_asignacion = any("<-" in token for token in tokens_texto)
                    
                    tiene_hasta = "hasta" in tokens_texto
                    tiene_hacer = "hacer" in tokens_texto

                    if not tiene_asignacion:
                        self.errores.append(f"Línea {numero_linea}: estructura 'Para' incompleta, falta asignación (<-)")
                    if not tiene_hasta:
                        self.errores.append(f"Línea {numero_linea}: estructura 'Para' incompleta, falta 'Hasta'")
                    if not tiene_hacer:
                        self.errores.append(f"Línea {numero_linea}: estructura 'Para' incompleta, falta 'Hacer'")

            # === ESTRUCTURAS DE CIERRE ===
            elif token_primero in ["finalgoritmo", "finproceso", "finsi", "finpara", "finmientras", "finsegun"]:
                if not estructuras_abiertas:
                    self.errores.append(f"Línea {numero_linea}: '{token_primero}' sin estructura de apertura")
                else:
                    ultima, linea_apertura = estructuras_abiertas[-1]
                    correspondencias = {
                        "algoritmo": "finalgoritmo",
                        "proceso": "finproceso", 
                        "si": "finsi",
                        "para": "finpara",
                        "mientras": "finmientras",
                        "segun": "finsegun",
                        "repetir": "hasta"
                    }
                    
                    cierre_esperado = correspondencias.get(ultima)
                    if cierre_esperado == token_primero:
                        estructuras_abiertas.pop()
                    else:
                        self.errores.append(f"Línea {numero_linea}: '{token_primero}' no corresponde con '{ultima}' de línea {linea_apertura}")

            # === CASO ESPECIAL: HASTA (para REPETIR) ===
            elif token_primero == "hasta":
                # Buscar si hay una estructura repetir abierta
                estructura_repetir = None
                for i, (estruct, linea) in enumerate(estructuras_abiertas):
                    if estruct == "repetir":
                        estructura_repetir = (estruct, linea, i)
                        break
                
                if estructura_repetir:
                    estruct, linea_apertura, indice = estructura_repetir
                    estructuras_abiertas.pop(indice)
                else:
                    # Verificar si este 'hasta' pertenece a un 'para'
                    estructura_para = None
                    for i, (estruct, linea) in enumerate(estructuras_abiertas):
                        if estruct == "para":
                            estructura_para = (estruct, linea, i)
                            break
                    
                    if not estructura_para:
                        self.errores.append(f"Línea {numero_linea}: 'Hasta' sin estructura 'Repetir' o 'Para' correspondiente")

    def _verificar_definicion_pseint(self, tokens, i, linea):
        """Verifica definición de variables en PSeInt"""
        if i + 3 >= len(tokens):
            self.errores.append(f"Línea {linea}: definición incompleta")
            return

        i_var = i + 1
        variables_encontradas = False
        
        # Buscar variables hasta encontrar "como"
        while i_var < len(tokens) and tokens[i_var][0].lower() != "como":
            if tokens[i_var][1] == "Identificador":
                nombre_var = tokens[i_var][0]
                # Verificar que no sea palabra reservada
                if nombre_var.lower() in self.palabras_reservadas_pseint:
                    self.errores.append(f"Línea {linea}: '{nombre_var}' es palabra reservada, no puede usarse como nombre de variable")
                else:
                    self.variables.add(nombre_var)
                    variables_encontradas = True
            i_var += 1

        if not variables_encontradas:
            self.errores.append(f"Línea {linea}: no se especificaron variables en definición")
            return

        if i_var >= len(tokens) or tokens[i_var][0].lower() != "como":
            self.errores.append(f"Línea {linea}: se esperaba 'Como' en definición")
            return

        if i_var + 1 >= len(tokens):
            self.errores.append(f"Línea {linea}: se esperaba tipo después de 'Como'")
            return

        tipo = tokens[i_var + 1][0].capitalize()
        tipos_validos = {"Entero", "Real", "Caracter", "Logico"}
        if tipo not in tipos_validos:
            self.errores.append(f"Línea {linea}: tipo no válido '{tipo}'")

    def _validar_cierres_finales(self, pila_parentesis, pila_corchetes, pila_cadenas, estructuras_abiertas):
        """Valida cierres pendientes al final del análisis"""
        if pila_parentesis:
            for linea, _ in pila_parentesis:
                self.errores.append(f"Línea {linea}: paréntesis '(' sin cerrar")
        if pila_corchetes:
            for linea, _ in pila_corchetes:
                self.errores.append(f"Línea {linea}: corchete '[' sin cerrar")
        if pila_cadenas:
            for linea in pila_cadenas:
                self.errores.append(f"Línea {linea}: cadena sin cerrar")
        if estructuras_abiertas:
            for estructura, linea in estructuras_abiertas:
                self.errores.append(f"Línea {linea}: estructura '{estructura}' sin cerrar")

    def generar_reporte_sintactico(self):
        """Genera un reporte completo del análisis sintáctico"""
        if not self.errores:
            return "✓ ANÁLISIS SINTÁCTICO: Correcto - No se encontraron errores sintácticos"
        
        reporte = "❌ ERRORES SINTÁCTICOS:\n"
        reporte += "----------------------\n"
        for error in self.errores:
            reporte += f"• {error}\n"
        
        reporte += f"\nTotal de errores sintácticos: {len(self.errores)}"
        
        # Resumen de verificaciones
        reporte += "\n\nVERIFICACIONES REALIZADAS:\n"
        reporte += "-------------------------\n"
        reporte += "✓ Balanceo de paréntesis y corchetes\n"
        reporte += "✓ Cierre de cadenas\n"
        reporte += "✓ Estructuras de control (Si, Mientras, Para, Segun)\n"
        reporte += "✓ Declaraciones de variables\n"
        reporte += "✓ Uso de palabras reservadas\n"
        
        return reporte