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
