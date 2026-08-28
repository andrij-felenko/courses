#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <variant>
#include <cmath>
#include <cctype>
#include <stdexcept>
#include <expected>

enum class TokenType {
    Number,
    Operator,
    UnaryMinus,
    Function,
    LParen,
    RParen,
    Comma
};

enum class Associativity {
    Left,
    Right
};

struct OpInfo {
    int precedence;
    Associativity associativity;
};

inline OpInfo get_op_info(char op) {
    switch (op) {
        case '+':
        case '-': return {1, Associativity::Left};
        case '*':
        case '/': return {2, Associativity::Left};
        case '^': return {3, Associativity::Right};
        default:  return {0, Associativity::Left};
    }
}

struct Token {
    TokenType type;
    double number{0.0};
    char op{'\0'};
    std::string func_name;
    int arg_count{1};
};

/* ── 1. Вузол абстрактного синтаксичного дерева (AST) ── */
struct AstNode {
    std::string value;
    std::vector<std::unique_ptr<AstNode>> children;

    explicit AstNode(std::string val) : value(std::move(val)) {}

    double evaluate() const {
        if (children.empty()) {
            return std::stod(value);
        }
        if (value == "neg") {
            return -children[0]->evaluate();
        }
        if (value == "+") return children[0]->evaluate() + children[1]->evaluate();
        if (value == "-") return children[0]->evaluate() - children[1]->evaluate();
        if (value == "*") return children[0]->evaluate() * children[1]->evaluate();
        if (value == "/") {
            double den = children[1]->evaluate();
            if (den == 0.0) throw std::runtime_error("Ділення на нуль у дереві AST");
            return children[0]->evaluate() / den;
        }
        if (value == "^") return std::pow(children[0]->evaluate(), children[1]->evaluate());
        if (value == "sin") return std::sin(children[0]->evaluate());
        if (value == "cos") return std::cos(children[0]->evaluate());
        if (value == "max") return std::max(children[0]->evaluate(), children[1]->evaluate());
        if (value == "pow") return std::pow(children[0]->evaluate(), children[1]->evaluate());

        throw std::runtime_error("Невідома операція у вузлі: " + value);
    }
};

/* ── 2. Лексер на std::string_view ── */
class Lexer {
public:
    explicit Lexer(std::string_view source) : src_(source) {}

    std::vector<Token> tokenize() {
        std::vector<Token> tokens;
        TokenType prev_type = TokenType::Comma; // початок виразу поводиться як після коми

        while (cursor_ < src_.size()) {
            skip_whitespace();
            if (cursor_ >= src_.size()) break;

            char c = src_[cursor_];

            if (std::isdigit(static_cast<unsigned char>(c)) || c == '.') {
                size_t start = cursor_;
                while (cursor_ < src_.size() && (std::isdigit(static_cast<unsigned char>(src_[cursor_])) || src_[cursor_] == '.')) {
                    cursor_++;
                }
                double val = std::stod(std::string(src_.substr(start, cursor_ - start)));
                tokens.push_back(Token{.type = TokenType::Number, .number = val});
                prev_type = TokenType::Number;
            }
            else if (std::isalpha(static_cast<unsigned char>(c))) {
                size_t start = cursor_;
                while (cursor_ < src_.size() && (std::isalnum(static_cast<unsigned char>(src_[cursor_])) || src_[cursor_] == '_')) {
                    cursor_++;
                }
                std::string name(src_.substr(start, cursor_ - start));
                tokens.push_back(Token{.type = TokenType::Function, .func_name = std::move(name), .arg_count = 1});
                prev_type = TokenType::Function;
            }
            else if (c == '(') {
                tokens.push_back(Token{.type = TokenType::LParen});
                cursor_++;
                prev_type = TokenType::LParen;
            }
            else if (c == ')') {
                tokens.push_back(Token{.type = TokenType::RParen});
                cursor_++;
                prev_type = TokenType::RParen;
            }
            else if (c == ',') {
                tokens.push_back(Token{.type = TokenType::Comma});
                cursor_++;
                prev_type = TokenType::Comma;
            }
            else if (c == '-') {
                bool is_unary = (prev_type == TokenType::Operator ||
                                 prev_type == TokenType::UnaryMinus ||
                                 prev_type == TokenType::LParen ||
                                 prev_type == TokenType::Comma);
                cursor_++;
                if (is_unary) {
                    tokens.push_back(Token{.type = TokenType::UnaryMinus, .op = '~'});
                    prev_type = TokenType::UnaryMinus;
                } else {
                    tokens.push_back(Token{.type = TokenType::Operator, .op = '-'});
                    prev_type = TokenType::Operator;
                }
            }
            else if (std::string_view("+*/^").find(c) != std::string_view::npos) {
                tokens.push_back(Token{.type = TokenType::Operator, .op = c});
                cursor_++;
                prev_type = TokenType::Operator;
            }
            else {
                throw std::runtime_error(std::string("Невідомий символ у виразі: ") + c);
            }
        }
        return tokens;
    }

private:
    void skip_whitespace() {
        while (cursor_ < src_.size() && std::isspace(static_cast<unsigned char>(src_[cursor_]))) {
            cursor_++;
        }
    }

    std::string_view src_;
    size_t cursor_{0};
};

/* ── 3. Побудова AST на льоту через Shunting-Yard ── */
class ExpressionParser {
public:
    static std::unique_ptr<AstNode> parse_to_ast(std::string_view expr) {
        Lexer lexer(expr);
        auto tokens = lexer.tokenize();

        std::vector<Token> op_stack;
        std::vector<std::unique_ptr<AstNode>> node_stack;
        std::vector<int> arg_stack;

        auto pop_operator_to_node = [&]() {
            if (op_stack.empty()) return;
            Token op = op_stack.back();
            op_stack.pop_back();

            if (op.type == TokenType::UnaryMinus) {
                if (node_stack.empty()) throw std::runtime_error("Бракує операнда для унарного мінуса");
                auto child = std::move(node_stack.back());
                node_stack.pop_back();

                auto node = std::make_unique<AstNode>("neg");
                node->children.push_back(std::move(child));
                node_stack.push_back(std::move(node));
            }
            else if (op.type == TokenType::Operator) {
                if (node_stack.size() < 2) throw std::runtime_error("Бракує операндів для бінарного оператора");
                auto right = std::move(node_stack.back()); node_stack.pop_back();
                auto left  = std::move(node_stack.back()); node_stack.pop_back();

                auto node = std::make_unique<AstNode>(std::string(1, op.op));
                node->children.push_back(std::move(left));
                node->children.push_back(std::move(right));
                node_stack.push_back(std::move(node));
            }
            else if (op.type == TokenType::Function) {
                int args = arg_stack.back();
                arg_stack.pop_back();
                if (static_cast<int>(node_stack.size()) < args) {
                    throw std::runtime_error("Бракує аргументів для функції " + op.func_name);
                }
                auto node = std::make_unique<AstNode>(op.func_name);
                node->children.resize(args);
                for (int i = args - 1; i >= 0; --i) {
                    node->children[i] = std::move(node_stack.back());
                    node_stack.pop_back();
                }
                node_stack.push_back(std::move(node));
            }
        };

        for (const auto& tok : tokens) {
            if (tok.type == TokenType::Number) {
                node_stack.push_back(std::make_unique<AstNode>(std::to_string(tok.number)));
            }
            else if (tok.type == TokenType::Function) {
                op_stack.push_back(tok);
                arg_stack.push_back(1);
            }
            else if (tok.type == TokenType::Comma) {
                while (!op_stack.empty() && op_stack.back().type != TokenType::LParen) {
                    pop_operator_to_node();
                }
                if (op_stack.empty()) throw std::runtime_error("Кома поза круглими дужками");
                if (!arg_stack.empty()) arg_stack.back()++;
            }
            else if (tok.type == TokenType::UnaryMinus) {
                op_stack.push_back(tok);
            }
            else if (tok.type == TokenType::Operator) {
                OpInfo in_info = get_op_info(tok.op);
                while (!op_stack.empty()) {
                    const auto& top = op_stack.back();
                    if (top.type == TokenType::Function || top.type == TokenType::UnaryMinus) {
                        pop_operator_to_node();
                        continue;
                    }
                    if (top.type == TokenType::Operator) {
                        OpInfo top_info = get_op_info(top.op);
                        if (top_info.precedence > in_info.precedence ||
                           (top_info.precedence == in_info.precedence && in_info.associativity == Associativity::Left)) {
                            pop_operator_to_node();
                            continue;
                        }
                    }
                    break;
                }
                op_stack.push_back(tok);
            }
            else if (tok.type == TokenType::LParen) {
                op_stack.push_back(tok);
            }
            else if (tok.type == TokenType::RParen) {
                while (!op_stack.empty() && op_stack.back().type != TokenType::LParen) {
                    pop_operator_to_node();
                }
                if (op_stack.empty()) throw std::runtime_error("Непарна закриваюча дужка ')'");
                op_stack.pop_back(); // видаляємо '('

                if (!op_stack.empty() && op_stack.back().type == TokenType::Function) {
                    pop_operator_to_node();
                }
            }
        }

        while (!op_stack.empty()) {
            if (op_stack.back().type == TokenType::LParen) {
                throw std::runtime_error("Незакрита кругла дужка '('");
            }
            pop_operator_to_node();
        }

        if (node_stack.size() != 1) {
            throw std::runtime_error("Некоректний синтаксис виразу");
        }

        return std::move(node_stack.front());
    }
};

int main() {
    try {
        std::string expr = "3 + 4 * 2 / ( 1 - 5 ) ^ 2 + max(10, 20)";
        std::cout << "Вираз: " << expr << "\n";

        auto ast = ExpressionParser::parse_to_ast(expr);
        double result = ast->evaluate();

        std::cout << "Результат обчислення через AST: " << result << "\n";
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
