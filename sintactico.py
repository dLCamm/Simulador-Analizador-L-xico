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
            'mientras', 'hacer', 'finmientras', 'repetir', 'hasta',
            'segun', 'hacer', 'de', 'otro', 'finsegun',
            'dimension', 'verdadero', 'falso'
        }

    def analizar(self, tokens):
        self.errores = []
        self.variables = set()
        pila_parentesis = []
        pila_corchetes = []
        pila_cadenas = []
        estructuras_abiertas = []  # Para estructuras de control

        for i, (token, tipo, linea) in enumerate(tokens):
            token_lower = token.lower()
            
            # --- Verificar apertura y cierre de signos PERMITIDOS en PSeInt ---
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

            # Verificar cadenas
            elif token.startswith('"') and token.endswith('"'):
                continue
            elif token.startswith('"') and not token.endswith('"'):
                pila_cadenas.append(linea)
            elif token.endswith('"') and not token.startswith('"'):
                if not pila_cadenas:
                    self.errores.append(f"Línea {linea}: cierre de cadena sin apertura previa")
                else:
                    pila_cadenas.pop()

            # --- Estructuras de control PSeInt ---
            self._verificar_estructuras_pseint(tokens, i, linea, estructuras_abiertas)

            # --- Declaración de variables con Definir ---
            if token_lower == "definir":
                self._verificar_definicion_pseint(tokens, i, linea)

            # --- Uso de palabras reservadas como variables ---
            if tipo == "Identificador" and token_lower in self.palabras_reservadas_pseint:
                self.errores.append(f"Línea {linea}: '{token}' es palabra reservada, no puede usarse como identificador")

        # --- Validar cierres finales ---
        self._validar_cierres_finales(pila_parentesis, pila_corchetes, pila_cadenas, estructuras_abiertas)

        return self.errores

    def _verificar_estructuras_pseint(self, tokens, i, linea, estructuras_abiertas):
        """Verifica sintaxis de estructuras de control PSeInt"""
        token, tipo, linea_actual = tokens[i]
        token_lower = token.lower()
        
        # Apertura de estructuras
        if token_lower in ["algoritmo", "proceso", "subproceso"]:
            estructuras_abiertas.append((token_lower, linea))
            
        elif token_lower in ["si", "para", "mientras", "repetir", "segun"]:
            estructuras_abiertas.append((token_lower, linea))
            
        # Cierre de estructuras
        elif token_lower in ["finalgoritmo", "finproceso", "finsi", "finpara", "finmientras", "finsegun"]:
            if not estructuras_abiertas:
                self.errores.append(f"Línea {linea}: '{token}' sin estructura de apertura")
            else:
                ultima_estructura, linea_apertura = estructuras_abiertas.pop()
                # Verificar correspondencia
                correspondencias = {
                    "si": "finsi", "para": "finpara", "mientras": "finmientras",
                    "segun": "finsegun", "algoritmo": "finalgoritmo", "proceso": "finproceso"
                }
                if correspondencias.get(ultima_estructura) != token_lower:
                    self.errores.append(f"Línea {linea}: '{token}' no corresponde con '{ultima_estructura}' de línea {linea_apertura}")

        # Verificar estructura SI
        if token_lower == "si":
            if i + 2 < len(tokens) and tokens[i + 2][0].lower() != "entonces":
                self.errores.append(f"Línea {linea}: después de condición se esperaba 'Entonces'")

        # Verificar estructura MIENTRAS
        elif token_lower == "mientras":
            if i + 2 < len(tokens) and tokens[i + 2][0].lower() != "hacer":
                self.errores.append(f"Línea {linea}: después de condición se esperaba 'Hacer'")

        # Verificar estructura PARA
        elif token_lower == "para":
            if i + 2 < len(tokens) and tokens[i + 2][0].lower() != "hasta":
                self.errores.append(f"Línea {linea}: estructura 'Para' incompleta, se esperaba 'Hasta'")

    def _verificar_definicion_pseint(self, tokens, i, linea):
        """Verifica sintaxis de definición de variables PSeInt"""
        if i + 3 >= len(tokens):
            self.errores.append(f"Línea {linea}: definición incompleta")
            return
            
        # Estructura: Definir var1, var2, ... Como Tipo
        i_var = i + 1
        variables_encontradas = False
        
        while i_var < len(tokens) and tokens[i_var][0].lower() != "como":
            if tokens[i_var][1] == "Identificador":
                self.variables.add(tokens[i_var][0])
                variables_encontradas = True
            elif tokens[i_var][0] != ",":
                self.errores.append(f"Línea {linea}: se esperaba identificador o ',' en definición")
                return
            i_var += 1
        
        if not variables_encontradas:
            self.errores.append(f"Línea {linea}: no se especificaron variables en definición")
        
        if i_var >= len(tokens) or tokens[i_var][0].lower() != "como":
            self.errores.append(f"Línea {linea}: se esperaba 'Como' en definición")
            return
            
        if i_var + 1 >= len(tokens):
            self.errores.append(f"Línea {linea}: se esperaba tipo después de 'Como'")
            return
            
        tipo = tokens[i_var + 1][0]
        tipos_validos = {"Entero", "Real", "Caracter", "Logico"}
        if tipo not in tipos_validos:
            self.errores.append(f"Línea {linea}: tipo no válido '{tipo}'")

    def _validar_cierres_finales(self, pila_parentesis, pila_corchetes, pila_cadenas, estructuras_abiertas):
        """Valida cierres pendientes"""
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