import re
from collections import Counter

class AnalizadorLexico:
    def __init__(self):
        # Palabras reservadas de PSeInt
        self.palabras_reservadas = {
            'Algoritmo', 'FinAlgoritmo', 'Proceso', 'FinProceso', 
            'SubProceso', 'FinSubProceso', 'Funcion', 'FinFuncion',
            'Definir', 'Como', 'Entero', 'Real', 'Caracter', 'Logico',
            'Escribir', 'Leer', 'Si', 'Entonces', 'Sino', 'FinSi',
            'Para', 'Hasta', 'Con', 'Paso', 'Hacer', 'FinPara',
            'Mientras', 'FinMientras', 'Repetir', 
            'Segun', 'De', 'Otro', 'FinSegun',  
            'Dimension', 'Verdadero', 'Falso'
        }
            
        # Operadores de PSeInt
        self.operadores = {
            '+', '-', '*', '/', '%', '^', '=', '<>', '<', '>', '<=', '>=', '<-', '->',
            'Y', 'O', 'NO', '&'  # & para concatenación
        }

        # Signos PERMITIDOS en PSeInt
        self.signos_permitidos = {
            '(', ')', ',', ';', '[', ']', '"', ':'
        }
      
        # Expresiones regulares para PSeInt
        self.patron_numeros = r'^\d+$'
        self.patron_decimal = r'^\d+\.\d+$'
        self.patron_identificadores = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        self.patron_cadena = r'^"[^"]*"$'
    
    def analizar_linea(self, linea, num_linea):
        tokens = []
        errores = []
        
        elementos = self._dividir_linea_pseint(linea)
        
        for elemento in elementos:
            if not elemento.strip():
                continue
                
            tipo = self._determinar_tipo_pseint(elemento)
            
            if tipo == "DESCONOCIDO":
                errores.append(f"Línea {num_linea}: Token no reconocido '{elemento}'")
            else:
                tokens.append((elemento, tipo, num_linea))
        
        return tokens, errores
    
    def _dividir_linea_pseint(self, linea):
        """Divide la línea según las reglas de PSeInt - CORREGIDO"""
        elementos = []
        i = 0
        n = len(linea)
        
        while i < n:
            if linea[i].isspace():
                i += 1
                continue
            
            # Verificar si es una cadena entre comillas - MEJORADO
            if linea[i] == '"':
                j = i + 1
                while j < n and linea[j] != '"':
                    j += 1
                if j < n:
                    # Encontramos comilla de cierre
                    elementos.append(linea[i:j+1])
                    i = j + 1
                else:
                    # Comilla sin cerrar, tomamos hasta el final
                    elementos.append(linea[i:])
                    i = n
                continue
            
            # Verificar comentarios
            if i + 1 < n and linea[i:i+2] == "//":
                # Todo lo que sigue es comentario
                elementos.append(linea[i:])
                i = n
                continue
            
            # Verificar operadores de múltiples caracteres
            elif i + 1 < n and linea[i:i+2] in {'<-', '->', '<>', '<=', '>='}:
                elementos.append(linea[i:i+2])
                i += 2
                continue
            
            # Verificar operadores y signos de un solo carácter
            elif linea[i] in self.operadores or linea[i] in self.signos_permitidos:
                elementos.append(linea[i])
                i += 1
                continue
            
            # Palabras y números
            else:
                j = i
                # Avanzar hasta encontrar un delimitador
                while j < n and not linea[j].isspace() and \
                      linea[j] not in self.operadores and \
                      linea[j] not in self.signos_permitidos and \
                      linea[j] != '"' and \
                      not (j + 1 < n and linea[j:j+2] == "//"):
                    j += 1
                palabra = linea[i:j]
                if palabra:
                    elementos.append(palabra)
                i = j
        
        return elementos
    
    def _determinar_tipo_pseint(self, elemento):
        elemento = elemento.strip()
        e_lower = elemento.lower()
        
        # Verificar si es comentario primero
        if elemento.startswith("//"):
            return "Comentario"
        
        # Palabras reservadas (case-insensitive)
        if e_lower in [p.lower() for p in self.palabras_reservadas]:
            return "Palabra Reservada"
        
        # Operadores
        if elemento in self.operadores:
            return "Operador"
        
        # Signos permitidos
        if elemento in self.signos_permitidos:
            return "Signo"
        
        # Números enteros
        if re.match(self.patron_numeros, elemento):
            return "Número"
        
        # Números decimales
        if re.match(self.patron_decimal, elemento):
            return "Decimal"
        
        # Cadenas entre comillas
        if re.match(self.patron_cadena, elemento):
            return "Cadena"
        
        # Identificadores (incluye snake_case)
        if re.match(self.patron_identificadores, elemento):
            # Verificar si es snake_case válido (opcional, para tu reporte)
            if "_" in elemento:
                return "Identificador (snake_case)"
            else:
                return "Identificador"
        
        # Si no coincide con ningún patrón válido
        return "DESCONOCIDO"

    
    def analizar_archivo(self, contenido):
        lineas = contenido.split('\n')
        todos_tokens = []
        todos_errores = []
        
        for num_linea, linea in enumerate(lineas, 1):
            linea = linea.strip()
            if linea:
                tokens, errores = self.analizar_linea(linea, num_linea)
                todos_tokens.extend(tokens)
                todos_errores.extend(errores)
        
        return todos_tokens, todos_errores
    
    def generar_reporte(self, tokens):
        contador_tokens = Counter((token, tipo) for token, tipo, _ in tokens)
        
        reporte = "REPORTE DE TOKENS - ANALIZADOR LÉXICO (PSEINT)\n"
        reporte += "=" * 65 + "\n\n"
        
        reporte += "TOKENS ENCONTRADOS (CLASIFICADOS POR TIPO Y CANTIDAD):\n"
        reporte += "=" * 70 + "\n\n"
        
        reporte += f"{'TOKEN':<20} {'TIPO':<25} {'CANTIDAD':<10}\n"
        reporte += "-" * 55 + "\n"
        
        tokens_ordenados = sorted(contador_tokens.items(), key=lambda x: (x[0][1], x[0][0]))
        
        for (token, tipo), cantidad in tokens_ordenados:
            reporte += f"{token:<20} {tipo:<25} {cantidad:<10}\n"
        
        contador_tipos = Counter(tipo for _, tipo, _ in tokens)
        
        reporte += "\n" + "=" * 55 + "\n"
        reporte += "RESUMEN POR TIPO DE TOKEN:\n"
        reporte += "-" * 40 + "\n"
        
        for tipo, cantidad in contador_tipos.items():
            reporte += f"{tipo}: {cantidad} tokens\n"
        
        tokens_validos = [t for t in tokens if t[1] != "DESCONOCIDO"]
        tokens_no_reconocidos = [t for t in tokens if t[1] == "DESCONOCIDO"]
        
        reporte += "\n" + "=" * 55 + "\n"
        reporte += f"TOTAL DE TOKENS VÁLIDOS: {len(tokens_validos)}\n"
        reporte += f"TOTAL DE TOKENS NO RECONOCIDOS: {len(tokens_no_reconocidos)}\n"
        reporte += f"TOTAL GENERAL: {len(tokens)}\n"
        
        if tokens_no_reconocidos:
            reporte += "\nTOKENS NO RECONOCIDOS (ERRORES LÉXICOS):\n"
            reporte += "-" * 45 + "\n"
            errores_por_linea = {}
            for token, tipo, linea in tokens_no_reconocidos:
                if linea not in errores_por_linea:
                    errores_por_linea[linea] = []
                errores_por_linea[linea].append(token)
            
            for linea in sorted(errores_por_linea.keys()):
                tokens_error = errores_por_linea[linea]
                tokens_str = ', '.join([f'"{t}"' for t in tokens_error])
                reporte += f"Línea {linea}: {tokens_str}\n"
        
        return reporte