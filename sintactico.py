import re

class AnalizadorSintactico:
    def __init__(self):
        self.variables = set()
        self.errores = []

    def analizar(self, tokens):
        self.errores = []
        self.variables = set()
        pila_llaves = []
        pila_parentesis = []
        pila_cadenas = []

        # Analizar estructura token por token
        for i, (token, tipo, linea) in enumerate(tokens):
            # --- Verificar apertura y cierre de signos ---
            if token == "{":
                pila_llaves.append(linea)
            elif token == "}":
                if not pila_llaves:
                    self.errores.append(f"Línea {linea}: '}}' sin apertura previa")
                else:
                    pila_llaves.pop()

            elif token == "(":
                pila_parentesis.append(linea)
            elif token == ")":
                if not pila_parentesis:
                    self.errores.append(f"Línea {linea}: ')' sin apertura previa")
                else:
                    pila_parentesis.pop()

            elif token.startswith('"') and token.endswith('"'):
                # Cadenas completas están bien
                continue
            elif token.startswith('"') and not token.endswith('"'):
                pila_cadenas.append(linea)
            elif token.endswith('"') and not token.startswith('"'):
                if not pila_cadenas:
                    self.errores.append(f"Línea {linea}: cierre de cadena sin apertura previa")
                else:
                    pila_cadenas.pop()

            # --- Declaración de variables ---
            if token in ["entero", "decimal", "booleano", "cadena"]:
                # Buscar si después hay un identificador
                if i + 1 < len(tokens):
                    siguiente_token, tipo_sig, linea_sig = tokens[i + 1]
                    if tipo_sig == "Identificador":
                        self.variables.add(siguiente_token)
                    else:
                        self.errores.append(f"Línea {linea}: se esperaba un identificador después de '{token}'")

            # --- Uso de variables no declaradas ---
            if tipo == "Identificador" and i > 0:
                anterior_token, tipo_ant, _ = tokens[i - 1]
                if anterior_token not in ["entero", "decimal", "booleano", "cadena", "si", "mientras", "hacer", "="]:
                    if token not in self.variables:
                        self.errores.append(f"Línea {linea}: variable '{token}' usada sin declarar")

            # --- Orden correcto en estructuras de control ---
            if token == "si":
                if not self._verificar_siguiente(tokens, i, "("):
                    self.errores.append(f"Línea {linea}: se esperaba '(' después de 'si'")
            if token == "mientras":
                if not self._verificar_siguiente(tokens, i, "("):
                    self.errores.append(f"Línea {linea}: se esperaba '(' después de 'mientras'")
            if token == "sino":
                if not self._verificar_siguiente(tokens, i, "{"):
                    self.errores.append(f"Línea {linea}: se esperaba '{{' después de 'sino'")

        # --- Validar cierres finales ---
        if pila_llaves:
            self.errores.append(f"Falta cerrar {len(pila_llaves)} llave(s) '{{' abiertas")
        if pila_parentesis:
            self.errores.append(f"Falta cerrar {len(pila_parentesis)} paréntesis '(' abiertos")
        if pila_cadenas:
            self.errores.append(f"Falta cerrar {len(pila_cadenas)} comillas '\"' abiertas")

        return self.errores

    def _verificar_siguiente(self, tokens, i, esperado):
        """Verifica si el token siguiente es el esperado"""
        if i + 1 < len(tokens):
            sig_token, _, _ = tokens[i + 1]
            return sig_token == esperado
        return False
