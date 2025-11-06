import re

class AnalizadorSemantico:
    def __init__(self):
        # Tabla de símbolos y estructuras auxiliares
        self.tabla_simbolos = {}
        self.errores = []
        self.funciones = {}
        self.variables_usadas = set()

    def limpiar(self):
        self.tabla_simbolos = {}
        self.errores = []
        self.funciones = {}
        self.variables_usadas = set()

    # ------------------------------------------------------------
    # MÉTODOS PRINCIPALES
    # ------------------------------------------------------------

    def analizar(self, tokens):
        self.limpiar()

        # Agrupar tokens por línea
        tokens_por_linea = {}
        for token, tipo, linea in tokens:
            tokens_por_linea.setdefault(linea, []).append((token, tipo))

        # PRIMERA PASADA: Declaraciones y funciones
        for linea in sorted(tokens_por_linea.keys()):
            lista = tokens_por_linea[linea]
            if not lista:
                continue

            self._analizar_funcion_pseint(linea, lista)
            self._analizar_definicion_pseint(linea, lista)
            self._analizar_dimension_pseint(linea, lista)

        # SEGUNDA PASADA: Asignaciones y uso de variables
        contexto_funcion = None
        for linea in sorted(tokens_por_linea.keys()):
            lista = tokens_por_linea[linea]
            if not lista:
                continue

            # Detectar inicio o fin de función
            if lista[0][0].lower() == "funcion" and len(lista) > 1:
                contexto_funcion = lista[1][0]
            elif lista[0][0].lower() in {"finfuncion", "finalgoritmo", "finproceso"}:
                contexto_funcion = None

            self._analizar_asignaciones_pseint(linea, lista)
            self._verificar_usos_variables(linea, lista)
            self._analizar_retorno_pseint(linea, lista, contexto_funcion)

        # TERCERA PASADA: Verificar llamadas a funciones
        for linea in sorted(tokens_por_linea.keys()):
            lista = tokens_por_linea[linea]
            if not lista:
                continue
            self._verificar_llamadas_funciones(linea, lista)

        # CUARTA PASADA: Variables no usadas
        self._verificar_variables_no_usadas()

        # Eliminar errores duplicados
        seen = set()
        errores_unicos = []
        for e in self.errores:
            if e not in seen:
                errores_unicos.append(e)
                seen.add(e)

        # Crear tabla de símbolos simplificada
        tabla_simbolos_simple = {}
        for var, info in self.tabla_simbolos.items():
            if isinstance(info, dict):
                tabla_simbolos_simple[var] = info['tipo']
            else:
                tabla_simbolos_simple[var] = info

        return errores_unicos, tabla_simbolos_simple

    # ------------------------------------------------------------
    # DECLARACIONES
    # ------------------------------------------------------------

    def _analizar_definicion_pseint(self, linea, lista):
        """Analiza declaraciones con 'Definir' de PSeInt"""
        if len(lista) >= 4 and lista[0][0].lower() == "definir":
            i = 1
            variables = []

            while i < len(lista) and lista[i][0].lower() != "como":
                if lista[i][1] == "Identificador":
                    var_name = lista[i][0]
                    if var_name in self.tabla_simbolos:
                        self.errores.append(f"Línea {linea}: variable '{var_name}' ya declarada anteriormente")
                    else:
                        variables.append(var_name)
                i += 1

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
        """Analiza declaraciones con 'Dimension'"""
        if len(lista) >= 2 and lista[0][0].lower() == "dimension":
            for i in range(1, len(lista)):
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

    def _analizar_funcion_pseint(self, linea, lista):
        """Analiza definiciones de funciones"""
        if len(lista) >= 2 and lista[0][0].lower() == "funcion":
            nombre_funcion = None
            parametros = []
            tipo_retorno = "Void"

            i = 1
            if lista[i][1] == "Identificador":
                nombre_funcion = lista[i][0]
                i += 1
            else:
                self.errores.append(f"Línea {linea}: falta nombre de la función")
                return

            # Leer parámetros dentro de paréntesis
            if i < len(lista) and lista[i][0] == "(":
                i += 1
                while i < len(lista) and lista[i][0] != ")":
                    token, tipo = lista[i]
                    if tipo == "Identificador":
                        parametros.append(token)
                    i += 1

            # Registrar la función
            if nombre_funcion in self.funciones:
                self.errores.append(f"Línea {linea}: función '{nombre_funcion}' ya declarada anteriormente")
            else:
                self.funciones[nombre_funcion] = {
                    "parametros": parametros,
                    "tipo_retorno": tipo_retorno,
                    "linea": linea,
                    "usada": False
                }

    # ------------------------------------------------------------
    # ASIGNACIONES Y USOS
    # ------------------------------------------------------------

    def _analizar_asignaciones_pseint(self, linea, lista):
        """Analiza asignaciones (<-)"""
        for idx, (tok, tok_tipo) in enumerate(lista):
            if tok in ('<-', '='):
                if idx > 0 and idx < len(lista) - 1:
                    lhs_tok, lhs_tipo = lista[idx - 1]

                    if lhs_tipo == "Identificador":
                        if lhs_tok not in self.tabla_simbolos:
                            self.errores.append(f"Línea {linea}: variable '{lhs_tok}' no declarada")
                        else:
                            self.tabla_simbolos[lhs_tok]['usada'] = True
                            self.tabla_simbolos[lhs_tok]['inicializada'] = True
                            self.variables_usadas.add(lhs_tok)

                        expr_tokens = lista[idx + 1:]
                        tipo_expr = self._evaluar_expresion(expr_tokens, linea)
                        if tipo_expr and lhs_tok in self.tabla_simbolos:
                            tipo_decl = self._obtener_tipo_variable(lhs_tok)
                            if tipo_decl and not self._compatibles_pseint(tipo_decl, tipo_expr):
                                self.errores.append(
                                    f"Línea {linea}: incompatibilidad en asignación '{lhs_tok}': {tipo_decl} <- {tipo_expr}"
                                )

    def _verificar_usos_variables(self, linea, lista):
        """Verifica uso de variables"""
        for i, (tok, tok_tipo) in enumerate(lista):
            if tok_tipo == "Identificador" and not self._es_palabra_reservada_pseint(tok):
                if i > 0 and lista[i - 1][0].lower() == "algoritmo":
                    continue

                if tok in self.tabla_simbolos:
                    self.tabla_simbolos[tok]['usada'] = True
                    self.variables_usadas.add(tok)

                    if i > 0 and lista[i - 1][0].lower() == "leer":
                        self.tabla_simbolos[tok]['inicializada'] = True
                else:
                    if not self._es_contexto_seguro(lista, i):
                        self.errores.append(f"Línea {linea}: variable '{tok}' usada sin declarar")

    def _verificar_llamadas_funciones(self, linea, lista):
        """Verifica llamadas a funciones"""
        for i in range(len(lista)):
            token, tipo = lista[i]
            if tipo == "Identificador" and i + 1 < len(lista) and lista[i + 1][0] == "(":
                if not self._es_palabra_reservada_pseint(token):
                    if token not in self.funciones:
                        self.errores.append(f"Línea {linea}: función '{token}' no declarada")
                    else:
                        self.funciones[token]["usada"] = True

    def _analizar_retorno_pseint(self, linea, lista, contexto_funcion):
        """Analiza instrucciones 'Retornar'"""
        for i, (tok, tipo) in enumerate(lista):
            if tok.lower() == "retornar":
                if not contexto_funcion:
                    self.errores.append(f"Línea {linea}: 'Retornar' fuera de una función")
                else:
                    expr = lista[i + 1:] if i + 1 < len(lista) else []
                    tipo_expr = self._evaluar_expresion(expr, linea)
                    tipo_decl = self.funciones[contexto_funcion]["tipo_retorno"]
                    if tipo_expr and tipo_decl != "Void" and not self._compatibles_pseint(tipo_decl, tipo_expr):
                        self.errores.append(
                            f"Línea {linea}: tipo de retorno incompatible en función '{contexto_funcion}' ({tipo_expr} ≠ {tipo_decl})"
                        )

    # ------------------------------------------------------------
    # FUNCIONES AUXILIARES
    # ------------------------------------------------------------

    def _es_contexto_seguro(self, lista, indice):
        """
        Determina si un identificador está en un contexto donde no representa una variable real.
        Versión genérica válida para cualquier pseudocódigo PSeInt.
        """
        if lista[indice][1] == "Cadena":
            return True

        for i in range(max(0, indice - 3), indice):
            if lista[i][0].lower() in {"escribir", "mostrar"}:
                return True

        for i in range(max(0, indice - 3), min(len(lista), indice + 3)):
            if lista[i][0].lower() in {"segun", "de", "otro", "modo"}:
                return True

        for i in range(max(0, indice - 2), min(len(lista), indice + 2)):
            if lista[i][0].lower() in {"funcion", "algoritmo", "proceso"}:
                return True

        for i in range(max(0, indice - 1), indice):
            if lista[i][0].lower() == "leer":
                return True

        if indice + 1 < len(lista) and lista[indice + 1][0] == "<-":
            return True

        return False

    def _verificar_variables_no_usadas(self):
        for var_name, info in self.tabla_simbolos.items():
            if isinstance(info, dict) and not info['usada']:
                self.errores.append(f"Línea {info['linea']}: variable '{var_name}' declarada pero no usada")

    # ------------------------------------------------------------
    # EVALUACIÓN DE EXPRESIONES Y TIPOS
    # ------------------------------------------------------------

    def _evaluar_expresion(self, expr_tokens, linea):
        if not expr_tokens:
            return None

        operandos_tipos = []
        operadores = {'+','-','*','/','%','^','=','<>','<','>','<=','>=','y','o','no','&'}
        contiene_comparador = any(tok[0] in {'=','<>','<','>','<=','>='} for tok in expr_tokens)

        for tok, tok_tipo in expr_tokens:
            tok_lower = tok.lower()

            if tok.startswith("//") or tok_tipo == "Cadena":
                continue
            if tok in {',', '[', ']', ';', '(', ')'}:
                continue
            if tok_lower in operadores:
                continue

            tipo = self._obtener_tipo_token(tok, tok_tipo)
            if tipo:
                operandos_tipos.append(tipo)

        if not operandos_tipos:
            return None

        if contiene_comparador:
            return 'Logico'

        tipos_unicos = set(operandos_tipos)
        if 'Real' in tipos_unicos:
            return 'Real'
        if 'Entero' in tipos_unicos:
            return 'Entero'
        if 'Caracter' in tipos_unicos:
            return 'Caracter'
        if 'Logico' in tipos_unicos:
            return 'Logico'

        return operandos_tipos[0]

    def _tipo_de_literal(self, token, tipo_token):
        if tipo_token == "Número":
            return "Entero"
        if tipo_token == "Decimal":
            return "Real"
        if tipo_token == "Cadena":
            return "Caracter"
        if token.lower() in ("verdadero", "falso"):
            return "Logico"
        return None

    def _obtener_tipo_token(self, token, tipo_token):
        tipo_lit = self._tipo_de_literal(token, tipo_token)
        if tipo_lit:
            return tipo_lit
        if tipo_token == "Identificador" and token in self.tabla_simbolos:
            return self._obtener_tipo_variable(token)
        return None

    def _obtener_tipo_variable(self, variable):
        if variable in self.tabla_simbolos:
            info = self.tabla_simbolos[variable]
            if isinstance(info, dict):
                return info['tipo']
            return info
        return None

    def _es_palabra_reservada_pseint(self, token):
        palabras = {
            'algoritmo','finalgoritmo','proceso','finproceso','funcion','finfuncion',
            'definir','como','entero','real','caracter','logico','escribir','leer',
            'si','entonces','sino','finsi','para','hasta','con','paso','hacer','finpara',
            'mientras','finmientras','repetir','segun','de','otro','finsegun',
            'dimension','verdadero','falso','esperar','tecla','retornar'
        }
        return token.lower() in palabras

    def _compatibles_pseint(self, tipo_decl, tipo_expr):
        if tipo_decl == tipo_expr:
            return True
        if tipo_decl == 'Real' and tipo_expr == 'Entero':
            return True
        if tipo_decl == 'Caracter' and tipo_expr in ['Entero', 'Real']:
            return True
        return False

    # ------------------------------------------------------------
    # REPORTE
    # ------------------------------------------------------------

    def generar_reporte_semantico(self):
        if not self.errores:
            reporte = "✓ ANÁLISIS SEMÁNTICO: Correcto\n\n"
        else:
            reporte = "❌ ERRORES SEMÁNTICOS:\n"
            reporte += "----------------------\n"
            for error in self.errores:
                reporte += f"• {error}\n"
            reporte += f"\nTotal: {len(self.errores)} error(es)\n\n"

        if self.tabla_simbolos:
            reporte += "📊 TABLA DE SÍMBOLOS:\n"
            reporte += "---------------------\n"
            for var, info in sorted(self.tabla_simbolos.items()):
                if isinstance(info, dict):
                    estado = "✓" if info['usada'] else "⚠️"
                    reporte += f"{estado} {var}: {info['tipo']}\n"
                else:
                    reporte += f"? {var}: {info}\n"
            reporte += f"\nTotal variables: {len(self.tabla_simbolos)}\n"

        if self.funciones:
            reporte += "\n📘 FUNCIONES DETECTADAS:\n"
            reporte += "------------------------\n"
            for nombre, datos in self.funciones.items():
                usadosim = "✓" if datos['usada'] else "⚠️"
                reporte += f"{usadosim} {nombre}({', '.join(datos['parametros'])}) → {datos['tipo_retorno']}\n"

        return reporte
