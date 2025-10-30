class AnalizadorSemantico:
    def __init__(self):
        # tabla de símbolos ('entero','decimal','booleano','cadena')
        self.tabla_simbolos = {}
        self.errores = []

    def limpiar(self):
        self.tabla_simbolos = {}
        self.errores = []

    def _tipo_de_literal(self, token, tipo_token):
        # determina tipo semantico a partir de token lexico
        if tipo_token == "Número":
            return "entero"
        if tipo_token == "Decimal":
            return "decimal"
        if tipo_token == "Cadena":
            return "cadena"
        if token in ("verdadero", "falso"):
            return "booleano"
        return None

    def analizar(self, tokens):
        self.limpiar()

        # agrupar tokens por linea
        tokens_por_linea = {}
        for token, tipo, linea in tokens:
            tokens_por_linea.setdefault(linea, []).append((token, tipo))

        for linea in sorted(tokens_por_linea.keys()):
            lista = tokens_por_linea[linea]
            if not lista:
                continue

            # caso declaración (entero x = 1)
            primer_token, primer_tipo = lista[0]
            if primer_token in ("entero", "decimal", "booleano", "cadena"):
                # debe seguir un identificador
                if len(lista) >= 2:
                    ident, tipo_ident = lista[1]
                    if tipo_ident != "Identificador":
                        self.errores.append(f"Línea {linea}: se esperaba identificador después de '{primer_token}'")
                        continue
                    # registrar en tabla (si ya existe, lo actualizamos repeticion permitida)
                    self.tabla_simbolos[ident] = primer_token
                    # si hay asignacion, evaluar tipo del lado derecho
                    if len(lista) >= 4 and lista[2][0] == '=':
                        expr = lista[3:]
                        tipo_expr = self._evaluar_expresion(expr, linea)
                        if tipo_expr is None:
                            # errores ya agregados por evaluar expresion (uso de variable no declarada)
                            continue
                        # verificar compatibilidad tipo de declaracion vs tipo_expr
                        if not self._compatibles(primer_token, tipo_expr):
                            self.errores.append(
                                f"Línea {linea}: asignación incompatible: '{primer_token}' <- '{tipo_expr}'"
                            )
                else:
                    self.errores.append(f"Línea {linea}: declaración incompleta de tipo '{primer_token}'")

        # verificar asignaciones y usos posteriores (variables usadas deben existir)
        for linea in sorted(tokens_por_linea.keys()):
            lista = tokens_por_linea[linea]
            if not lista:
                continue

            # Buscar asignaciones 
            for idx, (tok, tok_tipo) in enumerate(lista):
                if tok == '=' and idx > 0:
                    lhs_tok, lhs_tipo = lista[idx - 1]
                    if lhs_tipo != "Identificador":
                        self.errores.append(f"Línea {linea}: lado izquierdo de '=' debe ser identificador")
                        continue
                    if lhs_tok not in self.tabla_simbolos:
                        self.errores.append(f"Línea {linea}: variable '{lhs_tok}' usada sin declarar antes de asignar")
                        continue
                    # evaluar expresion a la derecha
                    expr = lista[idx + 1:]
                    tipo_expr = self._evaluar_expresion(expr, linea)
                    if tipo_expr is None:
                        continue
                    tipo_decl = self.tabla_simbolos.get(lhs_tok)
                    if not self._compatibles(tipo_decl, tipo_expr):
                        self.errores.append(
                            f"Línea {linea}: incompatibilidad en asignación a '{lhs_tok}': '{tipo_decl}' <- '{tipo_expr}'"
                        )

            # Verificar uso de identificadores en expresiones (uso sin declarar)
            for tok, tok_tipo in lista:
                if tok_tipo == "Identificador":
                    if tok not in self.tabla_simbolos:
                        self.errores.append(f"Línea {linea}: variable '{tok}' usada sin declarar")

        # eliminar duplicados
        seen = set()
        errores_unicos = []
        for e in self.errores:
            if e not in seen:
                errores_unicos.append(e)
                seen.add(e)

        return errores_unicos, self.tabla_simbolos

    def _evaluar_expresion(self, expr_tokens, linea):
        if not expr_tokens:
            self.errores.append(f"Línea {linea}: expresión vacía en asignación")
            return None

        # construir lista simple de operandos y operadores
        operandos_tipos = []
        operadores = set(['+','-','*','/','%','==','>','<','>=','<='])
        for tok, tok_tipo in expr_tokens:
            if tok == ';':
                continue
            # si es literal
            tipo_lit = self._tipo_de_literal(tok, tok_tipo)
            if tipo_lit:
                operandos_tipos.append(tipo_lit)
                continue
            # si es identificador buscar en tabla
            if tok_tipo == "Identificador":
                if tok not in self.tabla_simbolos:
                    self.errores.append(f"Línea {linea}: variable '{tok}' usada sin declarar")
                    return None
                operandos_tipos.append(self.tabla_simbolos[tok])
                continue
            if tok in operadores:
                continue
            continue

        # Si no hay operandos reconocidos
        if not operandos_tipos:
            self.errores.append(f"Línea {linea}: no se pudo determinar tipo de la expresión")
            return None

        # Regla: si hay mezcla de cadena o entero
        tipos_unicos = set(operandos_tipos)
        numeros = {'entero', 'decimal'}
        if 'cadena' in tipos_unicos and (tipos_unicos & numeros):
            self.errores.append(f"Línea {linea}: operación entre cadena y número no permitida")
            return None

        # tipos de datos
        if 'decimal' in tipos_unicos:
            return 'decimal'
        if tipos_unicos == {'booleano'}:
            return 'booleano'
        if tipos_unicos == {'cadena'}:
            return 'cadena'
        # si solo enteros
        if tipos_unicos == {'entero'}:
            return 'entero'
        # combinaciones numericas
        if tipos_unicos <= numeros:
            return 'entero'

        return 'entero'

    def _compatibles(self, tipo_decl, tipo_expr):
        
        if tipo_decl == tipo_expr:
            return True
        if tipo_decl == 'decimal' and tipo_expr == 'entero':
            return True
        # resto incompatibles
        return False
