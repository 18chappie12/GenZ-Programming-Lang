#!/usr/bin/env python3
"""
Flex Programming Language: Compiler, Semantic Analyzer, and Runtime Interpreter Engine.
Author: Flex Language Core Contributors
"""

import sys
import re
import os

# Lexer Token Types
T_KEYWORD = "KEYWORD"
T_IDENTIFIER = "IDENTIFIER"
T_NUMBER = "NUMBER"
T_STRING = "STRING"
T_OPERATOR = "OPERATOR"
T_BRACE = "BRACE"
T_ASSIGN = "ASSIGN"
T_EOF = "EOF"

KEYWORDS = {
    'programme', 'initialise', 'constant', 'spill', 'display', 'if', 'else', 
    'while', 'protocol', 'vibe', 'lock'
}

class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', Line {self.line})"


class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.length = len(source_code)

    def error(self, message):
        print(f"\n🚨 [Lexer Error] Line {self.line}: {message}")
        sys.exit(1)

    def next_token(self):
        while self.position < self.length:
            char = self.source[self.position]

            # Handle Line increments
            if char == '\n':
                self.line += 1
                self.position += 1
                continue

            # Handle Whitespace
            if char.isspace():
                self.position += 1
                continue

            # Handle Comments
            if char == '/' and self.position + 1 < self.length and self.source[self.position + 1] == '/':
                while self.position < self.length and self.source[self.position] != '\n':
                    self.position += 1
                continue

            # Check spelling safeguards (British English checks)
            # American variable initializations / styles trigger friendly warnings
            if char.isalpha():
                word = ""
                start_pos = self.position
                while self.position < self.length and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
                    word += self.source[self.position]
                    self.position += 1
                
                # Check for "initialize" instead of "initialise"
                if word == "initialize":
                    self.error("Found 'initialize'. Flex is strictly British English. Please use 'initialise'.")
                # Check for "color" instead of "colour"
                if word == "color":
                    self.error("Found 'color'. Did you forget the 'u'? Please use 'colour'.")

                if word in KEYWORDS:
                    return Token(T_KEYWORD, word, self.line)
                return Token(T_IDENTIFIER, word, self.line)

            # Numbers
            if char.isdigit():
                num = ""
                while self.position < self.length and self.source[self.position].isdigit():
                    num += self.source[self.position]
                    self.position += 1
                return Token(T_NUMBER, int(num), self.line)

            # Strings
            if char == '"':
                string_val = ""
                self.position += 1  # Skip opening quote
                while self.position < self.length and self.source[self.position] != '"':
                    if self.source[self.position] == '\n':
                        self.line += 1
                    string_val += self.source[self.position]
                    self.position += 1
                if self.position >= self.length:
                    self.error("Unterminated string literal.")
                self.position += 1  # Skip closing quote
                return Token(T_STRING, string_val, self.line)

            # Grouping brackets & Braces
            if char in {'{', '}', '(', ')'}:
                self.position += 1
                return Token(T_BRACE, char, self.line)

            # Operators
            if char in {'+', '-', '*', '/', '>', '<', '='}:
                op = char
                self.position += 1
                # Check for double character operators (e.g., '==', '>=', '<=')
                if self.position < self.length and self.source[self.position] == '=':
                    op += '='
                    self.position += 1
                
                if op == '=':
                    return Token(T_ASSIGN, op, self.line)
                return Token(T_OPERATOR, op, self.line)

            self.error(f"Unexpected character: '{char}'")
            
        return Token(T_EOF, None, self.line)


# AST Node Structures
class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class VarDeclNode(ASTNode):
    def __init__(self, is_const, name, expr_tokens):
        self.is_const = is_const
        self.name = name
        self.expr_tokens = expr_tokens  # Lazy evaluation tokens

class IfStatementNode(ASTNode):
    def __init__(self, left, op, right, body, else_body=None):
        self.left = left
        self.op = op
        self.right = right
        self.body = body
        self.else_body = else_body

class SpillNode(ASTNode):
    def __init__(self, expr_tokens):
        self.expr_tokens = expr_tokens


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def consume(self, token_type, value=None):
        if self.current_token.type == token_type and (value is None or self.current_token.value == value):
            self.current_token = self.lexer.next_token()
        else:
            raise SyntaxError(f"Line {self.current_token.line}: Expected token type '{token_type}' but got '{self.current_token.type}' (Value: '{self.current_token.value}')")

    def parse_expression_tokens(self):
        # Read tokens until finding a statement terminator block or braces
        expr = []
        while self.current_token.type not in {T_EOF} and not (self.current_token.type == T_BRACE and self.current_token.value in {'}', '{'}):
            # Check if it looks like a new statement keyword
            if self.current_token.type == T_KEYWORD and self.current_token.value in {'initialise', 'constant', 'spill', 'display', 'if'}:
                break
            expr.append(self.current_token)
            self.current_token = self.lexer.next_token()
        return expr

    def parse(self):
        body = []
        prog_name = "Main"
        
        # Parse program header
        if self.current_token.type == T_KEYWORD and self.current_token.value == "programme":
            self.consume(T_KEYWORD, "programme")
            if self.current_token.type == T_IDENTIFIER:
                prog_name = self.current_token.value
                self.consume(T_IDENTIFIER)
            self.consume(T_BRACE, "{")

        while self.current_token.type != T_EOF and not (self.current_token.type == T_BRACE and self.current_token.value == "}"):
            if self.current_token.type == T_KEYWORD:
                val = self.current_token.value
                
                # Variable Initialization
                if val in {"initialise", "constant"}:
                    is_const = (val == "constant")
                    self.consume(T_KEYWORD)
                    var_name = self.current_token.value
                    self.consume(T_IDENTIFIER)
                    self.consume(T_ASSIGN, "=")
                    expr_tokens = self.parse_expression_tokens()
                    body.append(VarDeclNode(is_const, var_name, expr_tokens))

                # Spilling/Displaying Out
                elif val in {"spill", "display"}:
                    self.consume(T_KEYWORD)
                    expr_tokens = self.parse_expression_tokens()
                    body.append(SpillNode(expr_tokens))

                # If Blocks
                elif val == "if":
                    self.consume(T_KEYWORD, "if")
                    self.consume(T_BRACE, "(")
                    
                    left = self.current_token.value
                    self.consume(self.current_token.type)
                    
                    op = self.current_token.value
                    self.consume(T_OPERATOR)
                    
                    right = self.current_token.value
                    self.consume(self.current_token.type)
                    
                    self.consume(T_BRACE, ")")
                    self.consume(T_BRACE, "{")
                    
                    if_body = []
                    while self.current_token.type != T_EOF and not (self.current_token.type == T_BRACE and self.current_token.value == "}"):
                        if_body.append(self.parse_statement())
                    self.consume(T_BRACE, "}")
                    
                    else_body = None
                    if self.current_token.type == T_KEYWORD and self.current_token.value == "else":
                        self.consume(T_KEYWORD, "else")
                        self.consume(T_BRACE, "{")
                        else_body = []
                        while self.current_token.type != T_EOF and not (self.current_token.type == T_BRACE and self.current_token.value == "}"):
                            else_body.append(self.parse_statement())
                        self.consume(T_BRACE, "}")
                        
                    body.append(IfStatementNode(left, op, right, if_body, else_body))
                else:
                    self.current_token = self.lexer.next_token()
            else:
                self.current_token = self.lexer.next_token()

        if prog_name != "Main":
            self.consume(T_BRACE, "}")

        return ProgramNode(prog_name, body)

    def parse_statement(self):
        # Inline statements parsing
        val = self.current_token.value
        if val in {"spill", "display"}:
            self.consume(T_KEYWORD)
            expr_tokens = self.parse_expression_tokens()
            return SpillNode(expr_tokens)
        elif val in {"initialise", "constant"}:
            is_const = (val == "constant")
            self.consume(T_KEYWORD)
            var_name = self.current_token.value
            self.consume(T_IDENTIFIER)
            self.consume(T_ASSIGN, "=")
            expr_tokens = self.parse_expression_tokens()
            return VarDeclNode(is_const, var_name, expr_tokens)
        else:
            tok = self.current_token
            self.current_token = self.lexer.next_token()
            return SpillNode([tok])


class SemanticAnalyzer:
    """ Checks variables, types, scope, and offers clean Genz corrections """
    def __init__(self, ast):
        self.ast = ast
        self.declared_variables = set()

    def analyze(self):
        for node in self.ast.body:
            if isinstance(node, VarDeclNode):
                self.declared_variables.add(node.name)
                # Analyze variable expressions references
                for t in node.expr_tokens:
                    if t.type == T_IDENTIFIER:
                        self.check_identifier(t.value, t.line)
            
            elif isinstance(node, SpillNode):
                for t in node.expr_tokens:
                    if t.type == T_IDENTIFIER:
                        self.check_identifier(t.value, t.line)
                        
            elif isinstance(node, IfStatementNode):
                if isinstance(node.left, str) and not node.left.startswith('"') and not node.left.isdigit():
                    self.check_identifier(node.left, 0)
                if isinstance(node.right, str) and not node.right.startswith('"') and not node.right.isdigit():
                    self.check_identifier(node.right, 0)
                
                # Check internal scopes
                for sub_node in node.body:
                    if isinstance(sub_node, VarDeclNode):
                        self.declared_variables.add(sub_node.name)

    def check_identifier(self, name, line):
        if name not in self.declared_variables and not name.isdigit():
            # Run similarity checks to suggest the correct identifier
            did_you_mean = self.suggest_closest(name)
            print(f"\n🚨 Vibe Check Failed on Line {line if line > 0 else 'Scope Check'}:")
            print(f"   Unknown variable '{name}' was referenced.")
            if did_you_mean:
                print(f"   💡 Did you mean: '{did_you_mean}'?")
            print("")
            sys.exit(1)

    def suggest_closest(self, name):
        import difflib
        matches = difflib.get_close_matches(name, list(self.declared_variables), n=1, cutoff=0.4)
        return matches[0] if matches else None


class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}

    def evaluate_expression(self, tokens):
        # Simplified parser and concatenator for basic expressions
        if not tokens:
            return None
        
        # Simple evaluation support for variable assignments or addition
        out_str = ""
        last_op = None
        current_val = None

        for t in tokens:
            val = t.value
            if t.type == T_IDENTIFIER:
                val = self.variables.get(t.value, "")
            
            if t.type == T_OPERATOR and val in {'+', '-'}:
                last_op = val
                continue

            if current_val is None:
                current_val = val
            else:
                if last_op == '+':
                    if isinstance(current_val, int) and isinstance(val, int):
                        current_val += val
                    else:
                        current_val = str(current_val) + str(val)
                elif last_op == '-':
                    if isinstance(current_val, int) and isinstance(val, int):
                        current_val -= val

        return current_val

    def execute(self):
        for node in self.ast.body:
            if isinstance(node, VarDeclNode):
                val = self.evaluate_expression(node.expr_tokens)
                self.variables[node.name] = val
                
            elif isinstance(node, SpillNode):
                val = self.evaluate_expression(node.expr_tokens)
                print(val)
                
            elif isinstance(node, IfStatementNode):
                left_val = self.variables.get(node.left, node.left)
                right_val = self.variables.get(node.right, node.right)
                
                # Coerce values safely
                if str(left_val).isdigit(): left_val = int(left_val)
                if str(right_val).isdigit(): right_val = int(right_val)

                condition_met = False
                if node.op == "==": condition_met = (left_val == right_val)
                elif node.op == ">=": condition_met = (left_val >= right_val)
                elif node.op == "<=": condition_met = (left_val <= right_val)
                elif node.op == ">": condition_met = (left_val > right_val)
                elif node.op == "<": condition_met = (left_val < right_val)

                if condition_met:
                    sub_interpreter = Interpreter(ProgramNode("Sub", node.body))
                    sub_interpreter.variables = self.variables
                    sub_interpreter.execute()
                elif node.else_body:
                    sub_interpreter = Interpreter(ProgramNode("Sub", node.else_body))
                    sub_interpreter.variables = self.variables
                    sub_interpreter.execute()


def main():
    if len(sys.argv) < 2:
        print("\n⚡ FLEX SYSTEM NATIVE CLI compiler")
        print("──────────────────────────────────")
        print("Usage: python compiler/flex.py [run/check/init] [filepath]\n")
        return

    command = sys.argv[1]

    if command == "init":
        print("✨ Initialising Flex Project structure...")
        os.makedirs("src", exist_ok=True)
        with open("flex.toml", "w") as f:
            f.write('[project]\nname = "MyFlexProject"\nversion = "1.0.0"\nauthors = ["Developer"]\n')
        with open("src/main.flex", "w") as f:
            f.write('programme Welcome {\n    initialise score = 95\n    spill "Build Successful! Score is: " + score\n}\n')
        print("✔ Project generated! Try running: python compiler/flex.py run src/main.flex")
        return

    if len(sys.argv) < 3:
        print("🚨 Please provide a path to a .flex file.")
        return

    filepath = sys.argv[2]
    if not os.path.exists(filepath):
        print(f"🚨 File path not found: {filepath}")
        return

    with open(filepath, 'r') as f:
        source_code = f.read()

    # Step 1: Lexical Analysis
    lexer = Lexer(source_code)
    
    # Step 2: Parsing
    try:
        parser = Parser(lexer)
        ast = parser.parse()
    except Exception as e:
        print(f"\n🚨 [Parser Crash]: {e}")
        sys.exit(1)

    # Step 3: Semantic Analysis
    analyzer = SemanticAnalyzer(ast)
    analyzer.analyze()

    if command == "check":
        print("✨ Build Successful")
        print("⚡ 0 Errors")
        print("🚀 Code is ready and fully vibe-checked.")
    
    elif command == "run":
        # Step 4: Execute
        interpreter = Interpreter(ast)
        interpreter.execute()


if __name__ == "__main__":
    main()