import re

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
        tokens = {}
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
                            if token_name not in tokens:
                                tokens[token_name] = set()  
                            tokens[token_name].add(valor)
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
        for categoria, valores in tokens.items():
            print(f"{categoria} ({len(valores)}):")
            for valor in valores:
                print(f"  {valor}")

    def mostrar_errores(self, errores):
        if errores:
            print("\nErrores encontrados:")
            for error, posicion in errores:
                print(f"  Token desconocido '{error}' en la posición {posicion}")
        else:
            print("\nNo se encontraron errores.")

if __name__ == "__main__":
    codigo_usuario = input("Introduce el código que deseas analizar: ")

    analizador = AnalizadorLexico()
    tokens, errores = analizador.analizar(codigo_usuario)

    analizador.mostrar_tokens(tokens)
    analizador.mostrar_errores(errores)