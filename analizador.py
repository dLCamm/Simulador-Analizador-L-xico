import re
from collections import Counter

class AnalizadorLexico:
    def __init__(self):
        # Palabras reservadas (case-sensitive)
        self.palabras_reservadas = {
            'entero', 'decimal', 'booleano', 'cadena', 'si', 'sino', 
            'mientras', 'hacer', 'verdadero', 'falso'
        }
        
        # Operadores
        self.operadores = {
            '+', '-', '*', '/', '%', '=', '==', '<', '>', '>=', '<='
        }
        
        # Signos (las comas NO están incluidas porque no son válidas en el lenguaje)
        self.signos = {
            '(', ')', '{', '}', '"', ';'
        }
        
        # Expresiones regulares mejoradas
        self.patron_numeros = r'^\d+$'  # Solo dígitos
        self.patron_decimal = r'^\d+\.\d+$'  # Números decimales
        self.patron_identificadores = r'^[a-zA-Z_][a-zA-Z0-9_]*$'  # Identificadores
        self.patron_cadena = r'^"[^"]*"$'  # Cadenas entre comillas
    
    def analizar_linea(self, linea, num_linea):
        tokens = []
        errores = []
        
        # Dividir la línea en tokens considerando espacios y comas como delimitadores
        elementos = self._dividir_linea_con_comas(linea)
        
        for elemento in elementos:
            if not elemento.strip():  # Saltar espacios vacíos
                continue
                
            tipo = self._determinar_tipo(elemento)
            
            if tipo == "DESCONOCIDO":
                errores.append(f"Línea {num_linea}: Token no reconocido '{elemento}'")
            else:
                tokens.append((elemento, tipo, num_linea))
        
        return tokens, errores
    
    def _dividir_linea_con_comas(self, linea):
        elementos = []
        i = 0
        n = len(linea)
        
        while i < n:
            if linea[i].isspace():
                i += 1
                continue
            
            # Verificar si es una cadena entre comillas
            if linea[i] == '"':
                j = i + 1
                while j < n and linea[j] != '"':
                    j += 1
                if j < n:
                    elementos.append(linea[i:j+1])
                    i = j + 1
                else:
                    # Comilla sin cerrar
                    elementos.append(linea[i:])
                    i = n
            
            # Verificar operadores de múltiples caracteres
            elif i + 1 < n and linea[i:i+2] in {'==', '>=', '<='}:
                elementos.append(linea[i:i+2])
                i += 2
            
            # Verificar operadores y signos de un solo carácter (EXCLUYENDO COMA)
            elif linea[i] in self.operadores or linea[i] in self.signos:
                elementos.append(linea[i])
                i += 1
            
            # Verificar comas (las tratamos como separadores individuales)
            elif linea[i] == ',':
                elementos.append(',')  # La coma como token separado
                i += 1
            
            # Palabras y números
            else:
                j = i
                # Avanzar hasta encontrar un delimitador (espacio, operador, signo o coma)
                while j < n and not linea[j].isspace() and linea[j] not in self.operadores and linea[j] not in self.signos and linea[j] != ',' and linea[j] != '"':
                    j += 1
                palabra = linea[i:j]
                if palabra:  # Solo agregar si no está vacía
                    elementos.append(palabra)
                i = j
        
        return elementos
    
    def _determinar_tipo(self, elemento):
        elemento = elemento.strip()
        
        # Verificar palabras reservadas (case-sensitive)
        if elemento in self.palabras_reservadas:
            return "Palabra Reservada"
        
        # Verificar operadores
        if elemento in self.operadores:
            return "Operador"
        
        # Verificar signos válidos
        if elemento in self.signos:
            return "Signo"
        
        # Verificar números enteros
        if re.match(self.patron_numeros, elemento):
            return "Número"
        
        # Verificar números decimales
        if re.match(self.patron_decimal, elemento):
            return "Decimal"
        
        # Verificar cadenas entre comillas
        if re.match(self.patron_cadena, elemento):
            return "Cadena"
        
        # Verificar identificadores (debe empezar con letra o _)
        if re.match(self.patron_identificadores, elemento):
            return "Identificador"
        
        # Las comas y cualquier otro carácter no reconocido
        return "DESCONOCIDO"
    
    def analizar_archivo(self, contenido):
        lineas = contenido.split('\n')
        todos_tokens = []
        todos_errores = []
        
        for num_linea, linea in enumerate(lineas, 1):
            if linea.strip():  # Si la línea no está vacía
                tokens, errores = self.analizar_linea(linea, num_linea)
                todos_tokens.extend(tokens)
                todos_errores.extend(errores)
        
        return todos_tokens, todos_errores
    
    def generar_reporte(self, tokens):
        # Contar la frecuencia de cada token (INCLUYENDO los no reconocidos)
        contador_tokens = Counter((token, tipo) for token, tipo, _ in tokens)
        
        reporte = "REPORTE DE TOKENS - ANALIZADOR LÉXICO\n"
        reporte += "=" * 60 + "\n\n"
        
        reporte += "TOKENS ENCONTRADOS (CLASIFICADOS POR TIPO Y CANTIDAD):\n"
        reporte += "=" * 70 + "\n\n"
        
        reporte += f"{'TOKEN':<20} {'TIPO':<25} {'CANTIDAD':<10}\n"
        reporte += "-" * 55 + "\n"
        
        # Ordenar por tipo y luego por token (INCLUYENDO DESCONOCIDOS)
        tokens_ordenados = sorted(contador_tokens.items(), key=lambda x: (x[0][1], x[0][0]))
        
        for (token, tipo), cantidad in tokens_ordenados:
            reporte += f"{token:<20} {tipo:<25} {cantidad:<10}\n"
        
        # Resumen por tipo (INCLUYENDO tokens no reconocidos)
        contador_tipos = Counter(tipo for _, tipo, _ in tokens)
        
        reporte += "\n" + "=" * 55 + "\n"
        reporte += "RESUMEN POR TIPO DE TOKEN (TODOS):\n"
        reporte += "-" * 40 + "\n"
        
        for tipo, cantidad in contador_tipos.items():
            reporte += f"{tipo}: {cantidad} tokens\n"
        
        # Separar tokens válidos y no reconocidos
        tokens_validos = [t for t in tokens if t[1] != "DESCONOCIDO"]
        tokens_no_reconocidos = [t for t in tokens if t[1] == "DESCONOCIDO"]
        
        reporte += "\n" + "=" * 55 + "\n"
        reporte += f"TOTAL DE TOKENS VÁLIDOS: {len(tokens_validos)}\n"
        reporte += f"TOTAL GENERAL: {len(tokens)}\n"
        
        # Mostrar ejemplos de tokens no reconocidos si hay
        if tokens_no_reconocidos:
            reporte += "\nEJEMPLOS DE TOKENS NO RECONOCIDOS:\n"
            reporte += "-" * 35 + "\n"
            # Mostrar solo algunos ejemplos únicos
            tokens_unicos_no_reconocidos = set(token for token, tipo, _ in tokens_no_reconocidos)
            for i, token in enumerate(list(tokens_unicos_no_reconocidos)[:5]):  # Mostrar máximo 5 ejemplos
                reporte += f"- '{token}'\n"
            if len(tokens_unicos_no_reconocidos) > 5:
                reporte += f"- ... y {len(tokens_unicos_no_reconocidos) - 5} más\n"
        
        return reporte
      
            
        
 
