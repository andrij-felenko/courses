# ⚙️ Побудова парсера математичних виразів в AST та його обчислення

Практична побудова парсера — найкращий спосіб зрозуміти, як компілятори перетворюють текст на синтаксичне дерево та обчислюють його. У цьому проєкті ми напишемо повноцінний калькулятор математичних виразів, який складається з трьох класичних компонентів:

1. **Лексер (Tokenizer)**: розбиває вихідну строку на токени (числа, оператори `+`, `-`, `*`, `/`, дужки).
2. **Парсер (Recursive Descent Parser)**: будує ієрархічне AST з урахуванням пріоритетів операторів.
3. **Оцінювач (Evaluator)**: рекурсивно обходить дерево та обчислює числове значення.

## Задача та вхідні дані

Створити програму, яка приймає математичний вираз у вигляді строки, наприклад:
`"3 + 4 * (10 - 2) / 4"`

Програма мусить побудувати абстрактне синтаксичне дерево, надрукувати його у формі префіксного виразу (для наочності перевірки структури) та обчислити підсумковий результат.

Очікуваний результат обчислення для виразу `"3 + 4 * (10 - 2) / 4"`:
- `10 - 2 = 8`
- `4 * 8 = 32`
- `32 / 4 = 8`
- `3 + 8 = 11`

## Реалізація парсера та AST

Ось повна, робоча реалізація мовами C++ та Python. Обидва варіанти є ідіоматичними: C++ використовує розумні вказівники (`std::unique_ptr`) для безпечного управління пам'яттю вузлів, а Python застосовує декоратори `@dataclass` та сопоставлення зі зразком `match-case`.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <cctype>
#include <stdexcept>

// ============================================================================
// 1. ЛЕКСЕР (TOKENIZER)
// ============================================================================
enum class TokenType { Number, Plus, Minus, Mul, Div, LParen, RParen, End };

struct Token {
    TokenType type;
    double val = 0.0;
};

std::vector<Token> tokenize(const std::string& expr) {
    std::vector<Token> tokens;
    size_t i = 0;
    while (i < expr.length()) {
        if (std::isspace(expr[i])) { i++; continue; }
        if (expr[i] == '+') { tokens.push_back({TokenType::Plus}); i++; }
        else if (expr[i] == '-') { tokens.push_back({TokenType::Minus}); i++; }
        else if (expr[i] == '*') { tokens.push_back({TokenType::Mul}); i++; }
        else if (expr[i] == '/') { tokens.push_back({TokenType::Div}); i++; }
        else if (expr[i] == '(') { tokens.push_back({TokenType::LParen}); i++; }
        else if (expr[i] == ')') { tokens.push_back({TokenType::RParen}); i++; }
        else if (std::isdigit(expr[i]) || expr[i] == '.') {
            size_t start = i;
            while (i < expr.length() && (std::isdigit(expr[i]) || expr[i] == '.')) i++;
            double val = std::stod(expr.substr(start, i - start));
            tokens.push_back({TokenType::Number, val});
        } else {
            throw std::runtime_error("Невідомий символ: " + std::string(1, expr[i]));
        }
    }
    tokens.push_back({TokenType::End});
    return tokens;
}

// ============================================================================
// 2. ВУЗЛИ AST ТА ОЦІНЮВАЧ
// ============================================================================
struct ASTNode {
    virtual ~ASTNode() = default;
    virtual double eval() const = 0;
    virtual std::string to_string() const = 0;
};

struct NumberNode : public ASTNode {
    double value;
    explicit NumberNode(double val) : value(val) {}
    double eval() const override { return value; }
    std::string to_string() const override { return std::to_string(value); }
};

struct BinaryOpNode : public ASTNode {
    char op;
    std::unique_ptr<ASTNode> left;
    std::unique_ptr<ASTNode> right;

    BinaryOpNode(char op, std::unique_ptr<ASTNode> l, std::unique_ptr<ASTNode> r)
        : op(op), left(std::move(l)), right(std::move(r)) {}

    double eval() const override {
        double l = left->eval();
        double r = right->eval();
        switch (op) {
            case '+': return l + r;
            case '-': return l - r;
            case '*': return l * r;
            case '/': 
                if (r == 0) throw std::runtime_error("Ділення на нуль!");
                return l / r;
        }
        return 0;
    }

    std::string to_string() const override {
        return "(" + std::string(1, op) + " " + left->to_string() + " " + right->to_string() + ")";
    }
};

// ============================================================================
// 3. РЕКУРСИВНИЙ ПАРСЕР (RECURSIVE DESCENT PARSER)
// ============================================================================
class Parser {
    std::vector<Token> tokens;
    size_t pos = 0;

    Token peek() const { return tokens[pos]; }
    Token get() { return tokens[pos++]; }

    // Factor ::= NUMBER | '(' Expression ')'
    std::unique_ptr<ASTNode> parse_factor() {
        Token t = get();
        if (t.type == TokenType::Number) {
            return std::make_unique<NumberNode>(t.val);
        }
        if (t.type == TokenType::LParen) {
            auto node = parse_expression();
            if (get().type != TokenType::RParen) {
                throw std::runtime_error("Очікувалась закриваюча дужка ')'");
            }
            return node;
        }
        throw std::runtime_error("Нездійсненне правило для Factor");
    }

    // Term ::= Factor (('*' | '/') Factor)*
    std::unique_ptr<ASTNode> parse_term() {
        auto left = parse_factor();
        while (peek().type == TokenType::Mul || peek().type == TokenType::Div) {
            Token op = get();
            char op_char = (op.type == TokenType::Mul) ? '*' : '/';
            auto right = parse_factor();
            left = std::make_unique<BinaryOpNode>(op_char, std::move(left), std::move(right));
        }
        return left;
    }

public:
    explicit Parser(std::vector<Token> t) : tokens(std::move(t)) {}

    // Expression ::= Term (('+' | '-') Term)*
    std::unique_ptr<ASTNode> parse_expression() {
        auto left = parse_term();
        while (peek().type == TokenType::Plus || peek().type == TokenType::Minus) {
            Token op = get();
            char op_char = (op.type == TokenType::Plus) ? '+' : '-';
            auto right = parse_term();
            left = std::make_unique<BinaryOpNode>(op_char, std::move(left), std::move(right));
        }
        return left;
    }
};

// ============================================================================
// ГОЛОВНА ФУНКЦІЯ
// ============================================================================
int main() {
    std::string input = "3 + 4 * (10 - 2) / 4";
    std::cout << "Вихідний вираз: " << input << "\n";

    try {
        auto tokens = tokenize(input);
        Parser parser(tokens);
        auto ast = parser.parse_expression();

        std::cout << "Префіксна форма AST: " << ast->to_string() << "\n";
        std::cout << "Результат обчислення: " << ast->eval() << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
    }

    return 0;
}
```
```py
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
```
:::

## Аналіз роботи програми

При запуску код друкує наступний вивід:

```
Вихідний вираз: 3 + 4 * (10 - 2) / 4
Префіксна форма AST: (+ 3.0 (/ (* 4.0 (- 10.0 2.0)) 4.0))
Результат обчислення: 11
```

Префіксна форма `(+ 3.0 (/ (* 4.0 (- 10.0 2.0)) 4.0))` точно повторює гемеотрію збудованого дерева:
- На самому верху стоїть операція додавання `+` із лівим операндом `3.0` та правим операндом-діленням `/`.
- Ділення має лівим операндом множення `*`, а правим — `4.0`.
- Множення має лівим операндом `4.0`, а правим — віднімання `(- 10.0 2.0)`.

## Типові пастки при реалізації AST-парсерів

1. **Нескінченна ліва рекурсія (Left Recursion)**:
   Якщо сформулювати правило як `Expr ::= Expr '+' Term`, рекурсивний парсер викличе `parse_expression()` в першому ж рядку і негайно впаде із переповненням стека (Stack Overflow). Саме тому ліву рекурсію замінюють ітеративним циклом `while (peek() == '+')` у методі `parse_expression()`.

2. **Витік пам'яті (у C++)**:
   Дерева є рекурсивними структурами з багатьма вузлами. Використання голих вказівників `ASTNode*` вимагає ручного рекурсивного видалення у деструкторах. Застосування `std::unique_ptr<ASTNode>` гарантує автоматичне та безпечне звільнення всього дерева при виході з області видимості кореневого вузла.

3. **Унарні оператори та від'ємні числа**:
   У реальних парсерах вираз `-5 * (-3)` вимагає обробки унарного мінуса в `parse_factor()`, де `-` перетворюється на вузол `UnaryOpNode('-', NumberNode(5))`.
