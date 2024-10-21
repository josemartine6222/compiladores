import tkinter as tk
from tkinter import ttk
import re
import matplotlib.pyplot as plt
import networkx as nx

class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.hijos = []

    def __str__(self):
        return self.valor

class AnalizadorLexico:
    def __init__(self):
        self.token_regex = [
            ('NUMERO', r'\d+(\.\d*)?'),
            ('OPERADOR', r'[+\-*/]'),
            ('PARENTESIS', r'[()]'),
            ('ESPACIO', r'\s+'),
            ('DESCONOCIDO', r'.')
        ]

    def analizar(self, codigo):
        tokens = []
        pos = 0

        while pos < len(codigo):
            match = None
            for token_name, token_pattern in self.token_regex:
                regex = re.compile(token_pattern)
                match = regex.match(codigo, pos)
                if match:
                    valor = match.group(0)
                    if token_name != 'ESPACIO':
                        tokens.append((token_name, valor))
                    pos = match.end(0)
                    break

            if not match:
                pos += 1

        return tokens

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
        self.raiz = self.analizar_expresion()

    def analizar_expresion(self):
        pila_operadores = []
        pila_operandos = []

        def crear_nodo_operador():
            operador = pila_operadores.pop()
            derecho = pila_operandos.pop()
            izquierdo = pila_operandos.pop()
            nodo_operador = Nodo(operador)
            nodo_operador.hijos.append(izquierdo)
            nodo_operador.hijos.append(derecho)
            pila_operandos.append(nodo_operador)

        while self.posicion < len(self.tokens):
            token_actual = self.obtener_token_actual()
            if token_actual[0] == 'NUMERO':
                pila_operandos.append(Nodo(token_actual[1]))
                self.avanzar()
            elif token_actual[0] == 'OPERADOR':
                while (pila_operadores and pila_operadores[-1] in ['+', '-', '*', '/']
                       and self.precedencia(pila_operadores[-1]) >= self.precedencia(token_actual[1])):
                    crear_nodo_operador()
                pila_operadores.append(token_actual[1])
                self.avanzar()
            elif token_actual[0] == 'PARENTESIS':
                if token_actual[1] == '(':
                    pila_operadores.append(token_actual[1])
                elif token_actual[1] == ')':
                    while pila_operadores and pila_operadores[-1] != '(':
                        crear_nodo_operador()
                    pila_operadores.pop()  # Eliminar el paréntesis izquierdo
                self.avanzar()
            else:
                break

        while pila_operadores:
            crear_nodo_operador()

        return pila_operandos[0]

    def precedencia(self, operador):
        if operador in ['+', '-']:
            return 1
        if operador in ['*', '/']:
            return 2
        return 0

class InterfazAnalizador:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Léxico y Sintáctico")

        self.etiqueta_codigo = tk.Label(root, text="Ingresa la expresión matemática:")
        self.etiqueta_codigo.pack()

        self.texto_codigo = tk.Text(root, height=2, width=40)
        self.texto_codigo.pack()

        self.boton_analizar = tk.Button(root, text="Analizar", command=self.analizar)
        self.boton_analizar.pack()

        self.treeview = ttk.Treeview(root)
        self.treeview.pack()

        self.etiqueta_tokens = tk.Label(root, text="Tokens generados:")
        self.etiqueta_tokens.pack()

        self.texto_tokens = tk.Text(root, height=5, width=40)
        self.texto_tokens.pack()

    def analizar(self):
        codigo = self.texto_codigo.get("1.0", "end-1c")
        lexico = AnalizadorLexico()
        tokens = lexico.analizar(codigo)

        self.texto_tokens.delete("1.0", tk.END)
        for token in tokens:
            self.texto_tokens.insert(tk.END, f"{token[0]}: {token[1]}\n")

        sintactico = AnalizadorSintactico(tokens)
        sintactico.analizar()

        self.mostrar_arbol(sintactico.raiz)
        self.visualizar_arbol(sintactico.raiz)

    def mostrar_arbol(self, nodo, padre=''):
        item = self.treeview.insert(padre, 'end', text=nodo.valor)
        for hijo in nodo.hijos:
            self.mostrar_arbol(hijo, item)

    def visualizar_arbol(self, raiz):
        grafo = nx.DiGraph()

        def agregar_nodos(nodo, grafo, nivel=0, posicion=0):
            nodo_id = f"{nodo.valor}_{nivel}_{posicion}"
            grafo.add_node(nodo_id, label=nodo.valor, level=nivel)

            if nodo.hijos:
                for idx, hijo in enumerate(nodo.hijos):
                    hijo_id = agregar_nodos(hijo, grafo, nivel + 1, idx)
                    grafo.add_edge(nodo_id, hijo_id)

            return nodo_id

        agregar_nodos(raiz, grafo)

        pos = nx.planar_layout(grafo)

        
        for key, value in pos.items():
            pos[key] = (value[0], -value[1])

        plt.figure(figsize=(10, 6))
        labels = nx.get_node_attributes(grafo, 'label')

        
        color_map = []
        for node in grafo.nodes(data=True):
            if node[1]['level'] == 0:  
                color_map.append('red')
            elif node[1]['level'] == 1: 
                color_map.append('blue')
            else:  
                color_map.append('green')

        nx.draw_networkx_nodes(grafo, pos, node_color="lightblue", node_size=3000, edgecolors=color_map, linewidths=2)
        nx.draw_networkx_labels(grafo, pos, labels, font_size=10, font_weight='bold')

        nx.draw_networkx_edges(grafo, pos, edge_color='gray', style='solid', arrows=True, arrowsize=25)

        plt.title("ÁRBOL SINTACTICO KEILER RODRIGUEZ Y JOSE MARTINEZ")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    interfaz = InterfazAnalizador(root)
    root.mainloop()
