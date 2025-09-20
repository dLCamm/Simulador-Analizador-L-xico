import re
from collections import Counter

class AnalizadorLexico:
    def __init__(self):
        # Palabras reservadas 
        self.palabras_reservadas = {
            'entero', 'decimal', 'booleano', 'cadena', 'si', 'sino', 
            'mientras', 'hacer', 'verdadero', 'falso'
        }
        
        # Operadores
        self.operadores = {
            '+', '-', '*', '/', '%', '=', '==', '<', '>', '>=', '<='
        }
        
        # Signos
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
        
        # Dividir la línea en tokens considerando todos los delimitadores
        elementos = self._dividir_linea_avanzado(linea)
        
        for elemento in elementos:
            if not elemento.strip():  # Saltar espacios vacíos
                continue
                
            tipo = self._determinar_tipo(elemento)
            
            if tipo == "DESCONOCIDO":
                errores.append(f"Línea {num_linea}: Token no reconocido '{elemento}'")
            else:
                tokens.append((elemento, tipo, num_linea))
        
        return tokens, errores
    
    def _dividir_linea_avanzado(self, linea):
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
            
            # Verificar operadores y signos de un solo carácter
            elif linea[i] in self.operadores or linea[i] in self.signos:
                elementos.append(linea[i])
                i += 1
            
            # Palabras y números
            else:
                j = i
                # Avanzar hasta encontrar un delimitador
                while j < n and not linea[j].isspace() and linea[j] not in self.operadores and linea[j] not in self.signos and linea[j] != '"':
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
        
        # Verificar signos
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
        # Contar tokens por tipo
        contador = Counter(tipo for _, tipo, _ in tokens)
        
        reporte = "REPORTE DE TOKENS - ANALIZADOR LÉXICO\n"
        reporte += "=" * 60 + "\n\n"
        
        reporte += "RESUMEN POR TIPO:\n"
        reporte += "-" * 30 + "\n"
        for tipo, cantidad in contador.items():
            reporte += f"{tipo}: {cantidad} tokens\n"
        
        reporte += "\nDETALLE COMPLETO (por línea):\n"
        reporte += "-" * 40 + "\n"
        
        # Agrupar tokens por línea
        tokens_por_linea = {}
        for token, tipo, linea in tokens:
            if linea not in tokens_por_linea:
                tokens_por_linea[linea] = []
            tokens_por_linea[linea].append((token, tipo))
        
        for linea in sorted(tokens_por_linea.keys()):
            reporte += f"\nLÍNEA {linea}:\n"
            reporte += f"{'TOKEN':<20} {'TIPO':<20}\n"
            reporte += "-" * 40 + "\n"
            for token, tipo in tokens_por_linea[linea]:
                reporte += f"{token:<20} {tipo:<20}\n"
        
        return reporte