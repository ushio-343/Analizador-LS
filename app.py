from flask import Flask, render_template, request
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definición de tokens
tokens = [
    'ID', 'NUMBER', 'EQUAL', 'PLUS', 'PLUSPLUS', 'SEMICOLON', 'OPEN_PAREN', 'CLOSE_PAREN',
    'OPEN_BRACE', 'CLOSE_BRACE', 'LESS_EQUAL', 'STRING', 'DOT', 'FOR', 'PRINTLN', 'INT'
]

# Reglas de expresión regular para tokens simples
t_EQUAL = r'='
t_PLUS = r'\+'
t_PLUSPLUS = r'\+\+'
t_SEMICOLON = r';'
t_OPEN_PAREN = r'\('
t_CLOSE_PAREN = r'\)'
t_OPEN_BRACE = r'\{'
t_CLOSE_BRACE = r'\}'
t_LESS_EQUAL = r'<='
t_DOT = r'\.'


def t_STRING(t):
    r'\".*?\"'
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value == 'for':
        t.type = 'FOR'
    elif t.value == 'println':
        t.type = 'PRINTLN'
    elif t.value == 'int':
        t.type = 'INT'
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


t_ignore = ' \t\n'

# Regla para manejar saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    t.type = 'ERROR'
    t.value = f"Carácter ilegal '{t.value[0]}'"
    t.lexer.skip(1)
    return t


lexer = lex.lex()


# Gramática para el análisis sintáctico
def p_program(p):
    'program : statement'
    p[0] = p[1]


def p_statement(p):
    '''statement : for_loop
                 | print_statement'''


def p_for_loop(p):
    'for_loop : FOR OPEN_PAREN INT ID EQUAL NUMBER SEMICOLON ID LESS_EQUAL NUMBER SEMICOLON ID PLUSPLUS CLOSE_PAREN OPEN_BRACE print_statement CLOSE_BRACE'
    p[0] = f'for ({p[3]} {p[4]}={p[6]}; {p[8]}<={p[10]}; {p[12]}++) {{ {p[15]} }}'


def p_print_statement(p):
    'print_statement : ID DOT ID DOT PRINTLN OPEN_PAREN STRING PLUS ID CLOSE_PAREN SEMICOLON'
    p[0] = f'{p[1]}.{p[3]}.{p[5]}({p[7]} + {p[9]});'


def p_error(p):
    raise SyntaxError(f"Error de sintaxis en '{p.value}'")


parser = yacc.yacc()


@app.route('/', methods=['GET', 'POST'])
def index():
    lex_output = ""
    syn_output = ""

    if request.method == 'POST':
        code = request.form.get('code', '')

        # Análisis léxico
        lexer.input(code)
        while True:
            tok = lexer.token()
            if not tok:
                break
            lex_output += f"{tok.type}: {tok.value}\n"

        # Análisis sintáctico
        try:
            parser.parse(code)
            syn_output = "La estructura del código es correcta."
        except SyntaxError as e:
            syn_output = str(e)

    return render_template('index.html', lex_output=lex_output, syn_output=syn_output)


if __name__ == "__main__":
    app.run(debug=True)
