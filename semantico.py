import re

class AnalizadorSemantico:
    def __init__(self):
        # tabla de símbolos usando tipos de PSeInt
        self.tabla_simbolos = {}
        self.errores = []
        self.funciones = {}
        self.variables_usadas = set()

    def limpiar(self):
        self.tabla_simbolos = {}
        self.errores = []
        self.funciones = {}
        self.variables_usadas = set()

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

        # Primera pasada: declaraciones con "Definir" y "Dimension"
        for linea in sorted(tokens_por_linea.keys()):
            lista = tokens_por_linea[linea]
            if not lista:
                continue

            self._analizar_definicion_pseint(linea, lista)
            self._analizar_dimension_pseint(linea, lista)   

        # Segunda pasada: asignaciones y usos
        for linea in sorted(tokens_por_linea.keys()):
            lista = tokens_por_linea[linea]
            if not lista:
                continue

            self._analizar_asignaciones_pseint(linea, lista)
            self._verificar_usos_variables(linea, lista)

        # Tercera pasada: verificar variables no usadas
        self._verificar_variables_no_usadas()

        # eliminar duplicados
        seen = set()
        errores_unicos = []
        for e in self.errores:
            if e not in seen:
                errores_unicos.append(e)
                seen.add(e)

        # Crear tabla de símbolos simplificada para la interfaz
        tabla_simbolos_simple = {}
        for var, info in self.tabla_simbolos.items():
            if isinstance(info, dict):
                tabla_simbolos_simple[var] = info['tipo']
            else:
                tabla_simbolos_simple[var] = info

        return errores_unicos, tabla_simbolos_simple

    def _analizar_definicion_pseint(self, linea, lista):
        """Analiza declaraciones con 'Definir' de PSeInt"""
        if len(lista) >= 4 and lista[0][0].lower() == "definir":
            # Estructura: Definir var1, var2, ... Como Tipo
            i = 1
            variables = []
            
            # Recoger todas las variables hasta "Como"
            while i < len(lista) and lista[i][0].lower() != "como":
                if lista[i][1] == "Identificador":
                    var_name = lista[i][0]
                    if var_name in self.tabla_simbolos:
                        self.errores.append(f"Línea {linea}: variable '{var_name}' ya declarada anteriormente")
                    else:
                        variables.append(var_name)
                elif lista[i][0] == ",":
                    pass  # Coma separadora, ignorar
                else:
                    if lista[i][0] not in [',', ';', ':']:
                        self.errores.append(f"Línea {linea}: se esperaba identificador o 'Como' en declaración")
                    return
                i += 1
            
            # Verificar que siga "Como" y el tipo
            if i < len(lista) - 1 and lista[i][0].lower() == "como":
                tipo = lista[i + 1][0].capitalize()
                tipos_validos = {"Entero", "Real", "Caracter", "Logico"}
                
                if tipo in tipos_validos:
                    for var in variables:
                        self.tabla_simbolos[var] = {
                            'tipo': tipo,
                            'linea': linea,
                            'usada': False,
                            'inicializada': False
                        }
                else:
                    self.errores.append(f"Línea {linea}: tipo no válido '{tipo}'")
            else:
                self.errores.append(f"Línea {linea}: declaración incompleta, falta 'Como [tipo]'")

    def _analizar_dimension_pseint(self, linea, lista):
        """Analiza declaraciones con 'Dimension' de PSeInt"""
        if len(lista) >= 2 and lista[0][0].lower() == "dimension":
            i = 1
            while i < len(lista):
                token, tipo = lista[i]
                if tipo == "Identificador":
                    var_name = token
                    if var_name not in self.tabla_simbolos:
                        self.tabla_simbolos[var_name] = {
                            'tipo': 'Real',
                            'linea': linea,
                            'usada': False,
                            'inicializada': True,
                            'es_arreglo': True
                        }
                    else:
                        self.errores.append(f"Línea {linea}: variable '{var_name}' ya declarada anteriormente")
                i += 1

    def _analizar_asignaciones_pseint(self, linea, lista):
        """Analiza asignaciones en PSeInt"""
        for idx, (tok, tok_tipo) in enumerate(lista):
            if tok == '<-' or tok == '=':
                if idx > 0 and idx < len(lista) - 1:
                    lhs_tok, lhs_tipo = lista[idx - 1]
                    
                    # Verificar que el lado izquierdo sea variable válida
                    if lhs_tipo == "Identificador":
                        if lhs_tok not in self.tabla_simbolos:
                            self.errores.append(f"Línea {linea}: variable '{lhs_tok}' no declarada")
                        else:
                            # Marcar variable como usada e inicializada
                            if isinstance(self.tabla_simbolos[lhs_tok], dict):
                                self.tabla_simbolos[lhs_tok]['usada'] = True
                                self.tabla_simbolos[lhs_tok]['inicializada'] = True
                            self.variables_usadas.add(lhs_tok)
                        
                        # Evaluar expresión del lado derecho
                        expr_tokens = []
                        j = idx + 1
                        while j < len(lista):
                            if lista[j][0] in [';', '<-', '=']:
                                break
                            expr_tokens.append(lista[j])
                            j += 1
                        
                        if expr_tokens:
                            tipo_expr = self._evaluar_expresion(expr_tokens, linea)
                            if tipo_expr and lhs_tok in self.tabla_simbolos:
                                tipo_decl = self._obtener_tipo_variable(lhs_tok)
                                if tipo_decl and not self._compatibles_pseint(tipo_decl, tipo_expr):
                                    self.errores.append(
                                        f"Línea {linea}: incompatibilidad en asignación a '{lhs_tok}': '{tipo_decl}' <- '{tipo_expr}'"
                                    )

    def _verificar_usos_variables(self, linea, lista):
        """Verifica usos correctos de variables - CORREGIDO"""
        i = 0
        
        while i < len(lista):
            tok, tok_tipo = lista[i]
            
            # Saltar comentarios
            if tok_tipo == "Comentario":
                i += 1
                continue
                
            # Saltar cadenas completas
            if tok_tipo == "Cadena":
                i += 1
                continue
                
            # Verificar solo identificadores que no sean palabras reservadas
            if tok_tipo == "Identificador" and not self._es_palabra_reservada_pseint(tok):
                # IGNORAR: Si es el nombre del algoritmo (primer identificador después de "Algoritmo")
                if i > 0 and lista[i-1][0].lower() == "algoritmo":
                    i += 1
                    continue
                    
                if tok in self.tabla_simbolos:
                    # Marcar como usada
                    if isinstance(self.tabla_simbolos[tok], dict):
                        self.tabla_simbolos[tok]['usada'] = True
                    self.variables_usadas.add(tok)
                    
                    # Si está en una lectura (Leer), marcarla como inicializada
                    if i > 0 and lista[i-1][0].lower() == "leer":
                        if isinstance(self.tabla_simbolos[tok], dict):
                            self.tabla_simbolos[tok]['inicializada'] = True
                else:
                    # Verificar contexto para evitar falsos positivos
                    if not self._es_contexto_seguro(lista, i):
                        self.errores.append(f"Línea {linea}: variable '{tok}' usada sin declarar")
            
            i += 1

    def _es_contexto_seguro(self, lista, indice):
        """Determina si el identificador está en un contexto seguro (no es variable)"""
        # Si está después de Escribir, probablemente sea texto
        for i in range(max(0, indice-5), indice):
            if lista[i][0].lower() == "escribir":
                return True
                
        # Si está en una estructura Segun...Hacer
        for i in range(max(0, indice-3), min(len(lista), indice+2)):
            if lista[i][0].lower() in ["segun", "hacer", "de", "otro", "modo"]:
                return True
                
        # Si está cerca de texto que indica menú o interfaz
        palabras_menu = {'sistema', 'gestión', 'universidad', 'estudiante', 'estadísticas', 
                        'buscar', 'agregar', 'mostrar', 'calcular', 'opción', 'seleccione',
                        'salir', 'menú', 'presione', 'tecla', 'continuar'}
        
        for i in range(max(0, indice-2), min(len(lista), indice+2)):
            if lista[i][0].lower() in palabras_menu:
                return True
                
        return False

    def _verificar_variables_no_usadas(self):
        """Verifica variables declaradas pero no usadas"""
        for var_name, info in self.tabla_simbolos.items():
            if isinstance(info, dict) and not info['usada']:
                self.errores.append(f"Línea {info['linea']}: variable '{var_name}' declarada pero no usada")

    def _evaluar_expresion(self, expr_tokens, linea):
        if not expr_tokens:
            return None

        operandos_tipos = []
        operadores_pseint = {'+','-','*','/','%','^','=','<>','<','>','<=','>=','y','o','no','&'}

        # Verificar si contiene operadores de comparación
        contiene_comparador = any(tok[0] in {'=','<>','<','>','<=','>='} for tok in expr_tokens)

        i = 0
        while i < len(expr_tokens):
            tok, tok_tipo = expr_tokens[i]
            tok_lower = tok.lower()

            # Ignorar comentarios y cadenas
            if tok.startswith("//") or tok_tipo == "Cadena":
                i += 1
                continue

            # Ignorar signos de puntuación
            if tok in {',', '[', ']', ';', '(', ')'}:
                i += 1
                continue

            # Si es operador, continuar
            if tok_lower in operadores_pseint:
                i += 1
                continue

            # Manejar paréntesis para expresiones complejas
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
                else:
                    i += 1
                    continue

            # Obtener tipo del token actual
            tipo = self._obtener_tipo_token(tok, tok_tipo)
            if tipo:
                operandos_tipos.append(tipo)
                # Marcar variable como usada
                if tok_tipo == "Identificador" and tok in self.tabla_simbolos:
                    if isinstance(self.tabla_simbolos[tok], dict):
                        self.tabla_simbolos[tok]['usada'] = True
                    self.variables_usadas.add(tok)

            i += 1

        if not operandos_tipos:
            return None

        # Si la expresión contiene comparadores, el resultado es siempre lógico
        if contiene_comparador:
            return 'Logico'

        # Determinar tipo resultante basado en los operandos
        tipos_unicos = set(operandos_tipos)

        # Reglas de compatibilidad PSeInt
        if 'Caracter' in tipos_unicos and len(tipos_unicos) > 1:
            return 'Caracter'

        if 'Logico' in tipos_unicos and len(tipos_unicos) > 1:
            return 'Logico'

        # Jerarquía de tipos PSeInt
        if 'Real' in tipos_unicos:
            return 'Real'
        if tipos_unicos == {'Logico'}:
            return 'Logico'
        if tipos_unicos == {'Caracter'}:
            return 'Caracter'
        if 'Entero' in tipos_unicos:
            return 'Entero'

        return operandos_tipos[0] if operandos_tipos else 'Entero'

    def _obtener_tipo_token(self, token, tipo_token):
        """Obtiene el tipo semántico de un token"""
        tipo_lit = self._tipo_de_literal(token, tipo_token)
        if tipo_lit:
            return tipo_lit
        if tipo_token == "Identificador" and token in self.tabla_simbolos:
            return self._obtener_tipo_variable(token)
        return None

    def _obtener_tipo_variable(self, variable):
        """Obtiene el tipo de una variable de la tabla de símbolos"""
        if variable in self.tabla_simbolos:
            info = self.tabla_simbolos[variable]
            if isinstance(info, dict):
                return info['tipo']
            else:
                return info
        return None

    def _es_palabra_reservada_pseint(self, token):
        """Verifica si un token es palabra reservada de PSeInt"""
        palabras_reservadas = {
            'algoritmo', 'finalgoritmo', 'proceso', 'finproceso',
            'definir', 'como', 'entero', 'real', 'caracter', 'logico',
            'escribir', 'leer', 'si', 'entonces', 'sino', 'finsi',
            'para', 'hasta', 'con', 'paso', 'hacer', 'finpara',
            'mientras', 'finmientras', 'repetir',
            'segun', 'de', 'otro', 'finsegun',
            'dimension', 'verdadero', 'falso', 'esperar', 'tecla'
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

    def generar_reporte_semantico(self):
        """Genera un reporte completo del análisis semántico"""
        if not self.errores:
            reporte = "✓ ANÁLISIS SEMÁNTICO: Correcto - No se encontraron errores semánticos\n\n"
        else:
            reporte = "❌ ERRORES SEMÁNTICOS:\n"
            reporte += "----------------------\n"
            for error in self.errores:
                reporte += f"• {error}\n"
            reporte += f"\nTotal de errores semánticos: {len(self.errores)}\n\n"

        # Información de la tabla de símbolos
        if self.tabla_simbolos:
            reporte += "📊 TABLA DE SÍMBOLOS:\n"
            reporte += "---------------------\n"
            
            # Contar variables por tipo
            contador_tipos = {}
            for var, info in self.tabla_simbolos.items():
                if isinstance(info, dict):
                    tipo = info['tipo']
                else:
                    tipo = info
                contador_tipos[tipo] = contador_tipos.get(tipo, 0) + 1
            
            for var, info in sorted(self.tabla_simbolos.items()):
                if isinstance(info, dict):
                    estado = "✓" if info['usada'] else "⚠️"
                    reporte += f"{estado} {var}: {info['tipo']}\n"
                else:
                    reporte += f"? {var}: {info}\n"
            
            reporte += f"\nDISTRIBUCIÓN DE TIPOS:\n"
            reporte += "----------------------\n"
            for tipo, cantidad in contador_tipos.items():
                reporte += f"• {tipo}: {cantidad} variable(s)\n"
            
            reporte += f"\nTotal variables: {len(self.tabla_simbolos)}\n"
        else:
            reporte += "No hay variables declaradas\n"

        return reporte