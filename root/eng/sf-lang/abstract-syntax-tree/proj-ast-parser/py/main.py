from dataclasses import dataclass
from typing import List, Union

# ============================================================================
# 1. ЛЕКСЕР (TOKENIZER)
# ============================================================================
@dataclass
class Token:
    type: str
    val: float = 0.0

def tokenize(expr: str) -> List[Token]:
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
            continue
        if expr[i] in "+-*/()":
            mapping = {'+': 'PLUS', '-': 'MINUS', '*': 'MUL', '/': 'DIV', '(': 'LPAREN', ')': 'RPAREN'}
            tokens.append(Token(mapping[expr[i]]))
            i += 1
        elif expr[i].isdigit() or expr[i] == '.':
            start = i
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                i += 1
            tokens.append(Token('NUMBER', float(expr[start:i])))
        else:
            raise ValueError(f"Невідомий символ: {expr[i]}")
    tokens.append(Token('END'))
    return tokens

# ============================================================================
# 2. ВУЗЛИ AST ТА ОЦІНЮВАЧ
# ============================================================================
class ASTNode:
    def eval(self) -> float:
        raise NotImplementedError
    def to_string(self) -> str:
        raise NotImplementedError

@dataclass
class NumberNode(ASTNode):
    value: float
    def eval(self) -> float:
        return self.value
    def to_string(self) -> str:
        return str(self.value)

@dataclass
class BinaryOpNode(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

    def eval(self) -> float:
        l = self.left.eval()
        r = self.right.eval()
        if self.op == '+': return l + r
        if self.op == '-': return l - r
        if self.op == '*': return l * r
        if self.op == '/':
            if r == 0: raise ZeroDivisionError("Ділення на нуль!")
            return l / r
        return 0.0

    def to_string(self) -> str:
        return f"({self.op} {self.left.to_string()} {self.right.to_string()})"

# ============================================================================
# 3. РЕКУРСИВНИЙ ПАРСЕР
# ============================================================================
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def get(self) -> Token:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def parse_factor(self) -> ASTNode:
        t = self.get()
        if t.type == 'NUMBER':
            return NumberNode(t.val)
        if t.type == 'LPAREN':
            node = self.parse_expression()
            if self.get().type != 'RPAREN':
                raise ValueError("Очікувалась закриваюча дужка ')'")
            return node
        raise ValueError("Очікувалось число або відкриваюча дужка")

    def parse_term(self) -> ASTNode:
        left = self.parse_factor()
        while self.peek().type in ('MUL', 'DIV'):
            op = self.get()
            op_char = '*' if op.type == 'MUL' else '/'
            right = self.parse_factor()
            left = BinaryOpNode(op_char, left, right)
        return left

    def parse_expression(self) -> ASTNode:
        left = self.parse_term()
        while self.peek().type in ('PLUS', 'MINUS'):
            op = self.get()
            op_char = '+' if op.type == 'PLUS' else '-'
            right = self.parse_term()
            left = BinaryOpNode(op_char, left, right)
        return left

# ============================================================================
# ГОЛОВНА ПРОГРАМА
# ============================================================================
if __name__ == "__main__":
    expr_text = "3 + 4 * (10 - 2) / 4"
    print(f"Вихідний вираз: {expr_text}")

    tokens = tokenize(expr_text)
    parser = Parser(tokens)
    ast = parser.parse_expression()

    print(f"Префіксна форма AST: {ast.to_string()}")
    print(f"Результат обчислення: {ast.eval()}")
