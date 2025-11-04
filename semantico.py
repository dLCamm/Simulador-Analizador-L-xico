class AnalizadorSemantico:
    def __init__(self):
        # tabla de símbolos usando tipos de PSeInt
        self.tabla_simbolos = {}
        self.errores = []
        self.funciones = {}

    def limpiar(self):
        self.tabla_simbolos = {}
        self.errores = []
        self.funciones = {}

    def _tipo_de_literal(self, token, tipo_token):
        # Determina tipo semántico según PSeInt
        if tipo_token == "Número":
            return "Entero"
        if tipo_token == "Decimal":
            return "Real"
        if tipo_token == "Cadena":
            return "Caracter"
        if token.lower() in ("verdadero", "falso"):
            return "Logico"
        return None

    def analizar(self, tokens):
        self.limpiar()

        # Agrupar tokens por linea
        tokens_por_linea = {}
        for token, tipo, linea in tokens:
            tokens_por_linea.setdefault(linea, []).append((token, tipo))

        # Primera pasada: declaraciones con "Definir"
        for linea in sorted(tokens_por_linea.keys()):
            lista = tokens_por_linea[linea]
            if not lista:
                continue

            self._analizar_definicion_pseint(linea, lista)
            self._analizar_estructuras_control_pseint(linea, lista)

        # Segunda pasada: asignaciones y usos
        for linea in sorted(tokens_por_linea.keys()):
            lista = tokens_por_linea[linea]
            if not lista:
                continue

            self._analizar_asignaciones_pseint(linea, lista)
            self._verificar_usos_variables(linea, lista)

        # eliminar duplicados
        seen = set()
        errores_unicos = []
        for e in self.errores:
            if e not in seen:
                errores_unicos.append(e)
                seen.add(e)

        return errores_unicos, self.tabla_simbolos

    def _analizar_definicion_pseint(self, linea, lista):
        """Analiza declaraciones con 'Definir' de PSeInt"""
        if len(lista) >= 4 and lista[0][0].lower() == "definir":
            # Estructura: Definir var1, var2, ... Como Tipo
            i = 1
            variables = []
            
            # Recoger todas las variables hasta "Como"
            while i < len(lista) and lista[i][0].lower() != "como":
                if lista[i][1] == "Identificador":
                    variables.append(lista[i][0])
                elif lista[i][0] == ",":
                    pass  # Coma separadora, ignorar
                else:
                    self.errores.append(f"Línea {linea}: se esperaba identificador o 'Como'")
                    return
                i += 1
            
            # Verificar que siga "Como" y el tipo
            if i < len(lista) - 1 and lista[i][0].lower() == "como":
                tipo = lista[i + 1][0]
                tipos_validos = {"Entero", "Real", "Caracter", "Logico"}
                
                if tipo in tipos_validos:
                    for var in variables:
                        self.tabla_simbolos[var] = tipo
                else:
                    self.errores.append(f"Línea {linea}: tipo no válido '{tipo}'")

    def _analizar_estructuras_control_pseint(self, linea, lista):
        """Analiza estructuras de control de PSeInt"""
        for i, (token, tok_tipo) in enumerate(lista):
            token_lower = token.lower()
            
            # Verificar estructura SI
            if token_lower == "si":
                # En PSeInt: Si condicion Entonces ... [Sino ...] FinSi
                if i + 2 < len(lista) and lista[i + 2][0].lower() != "entonces":
                    self.errores.append(f"Línea {linea}: después de condición se esperaba 'Entonces'")
                else:
                    # Verificar expresión booleana
                    if i + 1 < len(lista):
                        expr = [lista[i + 1]]  # Solo la condición
                        tipo_cond = self._evaluar_expresion(expr, linea)
                        if tipo_cond and tipo_cond != "Logico":
                            self.errores.append(f"Línea {linea}: condición debe ser lógica, no '{tipo_cond}'")
            
            # Verificar estructura MIENTRAS
            elif token_lower == "mientras":
                # En PSeInt: Mientras condicion Hacer ... FinMientras
                if i + 2 < len(lista) and lista[i + 2][0].lower() != "hacer":
                    self.errores.append(f"Línea {linea}: después de condición se esperaba 'Hacer'")
                else:
                    # Verificar expresión booleana
                    if i + 1 < len(lista):
                        expr = [lista[i + 1]]  # Solo la condición
                        tipo_cond = self._evaluar_expresion(expr, linea)
                        if tipo_cond and tipo_cond != "Logico":
                            self.errores.append(f"Línea {linea}: condición debe ser lógica, no '{tipo_cond}'")

    def _analizar_asignaciones_pseint(self, linea, lista):
        """Analiza asignaciones en PSeInt"""
        for idx, (tok, tok_tipo) in enumerate(lista):
            if tok == '<-' or tok == '=':  # PSeInt usa <- pero también acepta =
                if idx > 0:
                    lhs_tok, lhs_tipo = lista[idx - 1]
                    
                    # Verificar que el lado izquierdo sea variable válida
                    if lhs_tipo == "Identificador":
                        if lhs_tok not in self.tabla_simbolos:
                            self.errores.append(f"Línea {linea}: variable '{lhs_tok}' no declarada")
                            continue
                        
                        # Evaluar expresión del lado derecho
                        expr = lista[idx + 1:]
                        tipo_expr = self._evaluar_expresion(expr, linea)
                        if tipo_expr is None:
                            continue
                        
                        tipo_decl = self.tabla_simbolos.get(lhs_tok)
                        if not self._compatibles_pseint(tipo_decl, tipo_expr):
                            self.errores.append(
                                f"Línea {linea}: incompatibilidad en asignación a '{lhs_tok}': '{tipo_decl}' <- '{tipo_expr}'"
                            )

    def _verificar_usos_variables(self, linea, lista):
        """Verifica usos correctos de variables"""
        for tok, tok_tipo in lista:
            if tok_tipo == "Identificador" and not self._es_palabra_reservada_pseint(tok):
                if tok not in self.tabla_simbolos:
                    self.errores.append(f"Línea {linea}: variable '{tok}' usada sin declarar")

    def _evaluar_expresion(self, expr_tokens, linea):
        if not expr_tokens:
            return None

        operandos_tipos = []
        operadores_pseint = {'+','-','*','/','%','^','=','<>','<','>','<=','>=','Y','O','NO','&'}
        
        i = 0
        while i < len(expr_tokens):
            tok, tok_tipo = expr_tokens[i]
            
            if tok in operadores_pseint:
                i += 1
                continue
                
            # Manejar paréntesis
            if tok == '(':
                j = i + 1
                profundidad = 1
                while j < len(expr_tokens) and profundidad > 0:
                    if expr_tokens[j][0] == '(':
                        profundidad += 1
                    elif expr_tokens[j][0] == ')':
                        profundidad -= 1
                    j += 1
                
                if profundidad == 0:
                    sub_expr = expr_tokens[i+1:j-1]
                    tipo_sub = self._evaluar_expresion(sub_expr, linea)
                    if tipo_sub:
                        operandos_tipos.append(tipo_sub)
                    i = j
                    continue
            
            # Tipo literal o variable
            tipo = self._obtener_tipo_token(tok, tok_tipo)
            if tipo:
                operandos_tipos.append(tipo)
            
            i += 1

        if not operandos_tipos:
            return None

        # Determinar tipo resultante
        tipos_unicos = set(operandos_tipos)
        
        # Reglas de compatibilidad PSeInt
        if 'Caracter' in tipos_unicos and len(tipos_unicos) > 1:
            self.errores.append(f"Línea {linea}: operación entre cadena y otros tipos no permitida")
            return None
            
        if 'Logico' in tipos_unicos and len(tipos_unicos) > 1:
            self.errores.append(f"Línea {linea}: operación entre lógico y otros tipos no permitida")
            return None

        # Jerarquía de tipos PSeInt
        if 'Real' in tipos_unicos:
            return 'Real'
        if tipos_unicos == {'Logico'}:
            return 'Logico'
        if tipos_unicos == {'Caracter'}:
            return 'Caracter'
        if 'Entero' in tipos_unicos:
            return 'Entero'

        return 'Entero'

    def _obtener_tipo_token(self, token, tipo_token):
        """Obtiene el tipo semántico de un token"""
        tipo_lit = self._tipo_de_literal(token, tipo_token)
        if tipo_lit:
            return tipo_lit
        if tipo_token == "Identificador" and token in self.tabla_simbolos:
            return self.tabla_simbolos[token]
        return None

    def _es_palabra_reservada_pseint(self, token):
        """Verifica si un token es palabra reservada de PSeInt"""
        palabras_reservadas = {
            'algoritmo', 'finalgoritmo', 'proceso', 'finproceso',
            'definir', 'como', 'entero', 'real', 'caracter', 'logico',
            'escribir', 'leer', 'si', 'entonces', 'sino', 'finsi',
            'para', 'hasta', 'con', 'paso', 'hacer', 'finpara',
            'mientras', 'hacer', 'finmientras', 'repetir', 'hasta',
            'segun', 'hacer', 'de', 'otro', 'finsegun',
            'dimension', 'verdadero', 'falso'
        }
        return token.lower() in palabras_reservadas

    def _compatibles_pseint(self, tipo_decl, tipo_expr):
        """Verifica compatibilidad de tipos en PSeInt"""
        if tipo_decl == tipo_expr:
            return True
        if tipo_decl == 'Real' and tipo_expr == 'Entero':
            return True  # Entero se puede asignar a Real
        # PSeInt permite conversión implícita a cadena
        if tipo_decl == 'Caracter' and tipo_expr in ['Entero', 'Real']:
            return True
        return False