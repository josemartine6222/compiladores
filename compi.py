import tkinter as tk
from tkinter import ttk
import re

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.hijos = []

    def __str__(self):
        return self.valor


class AnalizadorLexico:
    def __init__(self):
        self.token_regex = [
            ('PALABRA_CLAVE', r'\b(public|if|else|while|for|return|int|float|printf)\b'),
            ('NUMERO', r'\d+(\.\d*)?'),
            ('CADENA', r'"[^"]*"'),
            ('IDENTIFICADOR', r'[a-zA-Z_]\w*'),
            ('OPERADOR', r'[<>!=]=?|[+\-*/%]'), 
            ('SIMBOLO', r'[;,(){}]'),
            ('ESPACIO', r'\s+'),
            ('DESCONOCIDO', r'.')
        ]

    def analizar(self, codigo):
        tokens = []
        errores = []
        pos = 0

        while pos < len(codigo):
            match = None
            for token_name, token_pattern in self.token_regex:
                regex = re.compile(token_pattern)
                match = regex.match(codigo, pos)
                if match:
                    valor = match.group(0)
                    if token_name != 'ESPACIO':  
                        if token_name != 'DESCONOCIDO':
                            tokens.append((token_name, valor))
                        else:
                            errores.append((valor, pos))  
                    pos = match.end(0)
                    break

            if not match:
                errores.append((codigo[pos], pos))  
                pos += 1

        return tokens, errores

    def mostrar_tokens(self, tokens):
        print("\nTokens encontrados:")
        for token_name, valor in tokens:
            print(f"{token_name}: {valor}")

    def mostrar_errores(self, errores):
        if errores:
            print("\nErrores encontrados:")
            for error, posicion in errores:
                print(f"  Token desconocido '{error}' en la posición {posicion}")
        else:
            print("\nNo se encontraron errores.")


class AnalizadorSintactico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicion = 0
        self.raiz = None

    def obtener_token_actual(self):
        if self.posicion < len(self.tokens):
            return self.tokens[self.posicion]
        return None

    def avanzar(self):
        self.posicion += 1

    def analizar(self):
        self.raiz = Nodo("Programa")
        self.analizar_programa(self.raiz)

    def analizar_programa(self, padre):
        while self.posicion < len(self.tokens):
            token_actual = self.obtener_token_actual()
            if token_actual is None:
                break

            tipo_token, valor_token = token_actual

            if tipo_token == 'PALABRA_CLAVE' and valor_token in ['int', 'float']:
                nodo_variable = Nodo("Declaración Variable")
                padre.hijos.append(nodo_variable)
                self.analizar_declaracion_variable(nodo_variable)

            elif tipo_token == 'PALABRA_CLAVE' and valor_token == 'if':
                nodo_if = Nodo("Estructura if")
                padre.hijos.append(nodo_if)
                self.analizar_if(nodo_if)

            elif tipo_token == 'PALABRA_CLAVE' and valor_token == 'while':
                nodo_while = Nodo("Bucle while")
                padre.hijos.append(nodo_while)
                self.analizar_while(nodo_while)

            else:
                self.avanzar()

    def analizar_declaracion_variable(self, padre):
        self.avanzar()
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == 'IDENTIFICADOR':
            nodo_identificador = Nodo("Identificador: " + token_actual[1])
            padre.hijos.append(nodo_identificador)
            self.avanzar()
            token_actual = self.obtener_token_actual()
            if token_actual and token_actual[0] == 'SIMBOLO' and token_actual[1] == ';':
                nodo_punto_y_coma = Nodo("Punto y coma")
                padre.hijos.append(nodo_punto_y_coma)
                self.avanzar()
            else:
                nodo_error = Nodo("Error: Se esperaba ';' al final de la declaración")
                padre.hijos.append(nodo_error)
        else:
            nodo_error = Nodo("Error: Se esperaba un identificador")
            padre.hijos.append(nodo_error)

    def analizar_if(self, padre):
        self.avanzar()  # Avanzar para pasar 'if'
        # Aquí puedes agregar el análisis de la estructura 'if' si es necesario

    def analizar_while(self, padre):
        self.avanzar()  # Avanzar para pasar 'while'
        token_actual = self.obtener_token_actual()
        if token_actual and token_actual[0] == 'SIMBOLO' and token_actual[1] == '(':
            nodo_parentesis_abierto = Nodo("Paréntesis abierto")
            padre.hijos.append(nodo_parentesis_abierto)
            self.avanzar()
            self.analizar_expresion(padre)  # Aquí se analiza la expresión del while
            token_actual = self.obtener_token_actual()
            if token_actual and token_actual[0] == 'SIMBOLO' and token_actual[1] == ')':
                nodo_parentesis_cerrado = Nodo("Paréntesis cerrado")
                padre.hijos.append(nodo_parentesis_cerrado)
                self.avanzar()
                token_actual = self.obtener_token_actual()
                if token_actual and token_actual[0] == 'SIMBOLO' and token_actual[1] == '{':
                    nodo_llave_abierta = Nodo("Llave abierta")
                    padre.hijos.append(nodo_llave_abierta)
                    self.avanzar()
                    self.analizar_programa(padre)  # Analizar el cuerpo del while
                    token_actual = self.obtener_token_actual()
                    if token_actual and token_actual[0] == 'SIMBOLO' and token_actual[1] == '}':
                        nodo_llave_cerrada = Nodo("Llave cerrada")
                        padre.hijos.append(nodo_llave_cerrada)
                        self.avanzar()
                    else:
                        nodo_error = Nodo("Error: Se esperaba '}' después del bloque while")
                        padre.hijos.append(nodo_error)
                else:
                    nodo_error = Nodo("Error: Se esperaba '{' después del while")
                    padre.hijos.append(nodo_error)
            else:
                nodo_error = Nodo("Error: Se esperaba ')' al final de la condición while")
                padre.hijos.append(nodo_error)
        else:
            nodo_error = Nodo("Error: Se esperaba '(' después de while")
            padre.hijos.append(nodo_error)

    def analizar_expresion(self, padre):
        self.avanzar()
        while self.obtener_token_actual() and self.obtener_token_actual()[0] != 'SIMBOLO':
            self.avanzar()


class InterfazArbolSintactico:
    def __init__(self, arbol):
        self.arbol = arbol
        self.ventana = tk.Tk()
        self.ventana.title("Árbol Sintáctico")
        self.tree = ttk.Treeview(self.ventana)
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.agregar_nodo(self.arbol.raiz, "")
        self.ventana.mainloop()

    def agregar_nodo(self, nodo, padre):
        id_nodo = self.tree.insert(padre, tk.END, text=nodo.valor)
        for hijo in nodo.hijos:
            self.agregar_nodo(hijo, id_nodo)


if __name__ == "__main__":
    print("Introduce el código que deseas analizar:")
    lineas_codigo = []
    while True:
        linea = input()
        if linea == "":  
            break
        lineas_codigo.append(linea)
    
    codigo_usuario = "\n".join(lineas_codigo)

    analizador_lexico = AnalizadorLexico()
    tokens, errores = analizador_lexico.analizar(codigo_usuario)
    analizador_lexico.mostrar_tokens(tokens)
    analizador_lexico.mostrar_errores(errores)

    if not errores:
        print("\nIniciando análisis sintáctico...")
        analizador_sintactico = AnalizadorSintactico(tokens)
        analizador_sintactico.analizar()
        interfaz = InterfazArbolSintactico(analizador_sintactico)
    else:
        print("\nNo se puede realizar el análisis sintáctico debido a errores léxicos.")
