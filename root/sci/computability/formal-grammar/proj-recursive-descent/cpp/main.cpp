#include <iostream>
#include <string_view>
#include <charconv>
#include <cctype>
#include <expected>
#include <string>
#include <vector>

enum class TokenType {
    Eof,
    Number,
    Plus,
    Minus,
    Star,
    Slash,
    LParen,
    RParen
};

struct Token {
    TokenType type{TokenType::Eof};
    double value{0.0};
};

class ArithmeticParser {
public:
    explicit ArithmeticParser(std::string_view input) : src_(input) {
        advance();
    }

    std::expected<double, std::string> parse() {
        auto result = parse_expr();
        if (!result) {
            return result;
        }
        if (current_.type != TokenType::Eof) {
            return std::unexpected("Синтаксична помилка: зайві символи після завершення коректного виразу");
        }
        return result;
    }

private:
    std::string_view src_;
    size_t pos_{0};
    Token current_;

    void advance() {
        while (pos_ < src_.size() && std::isspace(static_cast<unsigned char>(src_[pos_]))) {
            pos_++;
        }

        if (pos_ >= src_.size()) {
            current_ = Token{TokenType::Eof, 0.0};
            return;
        }

        char c = src_[pos_];
        if (std::isdigit(static_cast<unsigned char>(c)) || c == '.') {
            const char* start = src_.data() + pos_;
            const char* end = src_.data() + src_.size();
            double val = 0.0;
            auto [ptr, ec] = std::from_chars(start, end, val);
            if (ec == std::errc{}) {
                pos_ += static_cast<size_t>(ptr - start);
                current_ = Token{TokenType::Number, val};
                return;
            }
        }

        pos_++;
        switch (c) {
            case '+': current_ = Token{TokenType::Plus, 0.0}; break;
            case '-': current_ = Token{TokenType::Minus, 0.0}; break;
            case '*': current_ = Token{TokenType::Star, 0.0}; break;
            case '/': current_ = Token{TokenType::Slash, 0.0}; break;
            case '(': current_ = Token{TokenType::LParen, 0.0}; break;
            case ')': current_ = Token{TokenType::RParen, 0.0}; break;
            default:
                current_ = Token{TokenType::Eof, 0.0};
                break;
        }
    }

    // <Factor> ::= <Number> | "(" <Expr> ")" | "-" <Factor>
    std::expected<double, std::string> parse_factor() {
        if (current_.type == TokenType::Minus) {
            advance();
            auto res = parse_factor();
            if (!res) return res;
            return -(*res);
        }

        if (current_.type == TokenType::Number) {
            double val = current_.value;
            advance();
            return val;
        }

        if (current_.type == TokenType::LParen) {
            advance();
            auto expr_res = parse_expr();
            if (!expr_res) return expr_res;

            if (current_.type != TokenType::RParen) {
                return std::unexpected("Синтаксична помилка: очікувалася закриваюча дужка ')'");
            }
            advance();
            return expr_res;
        }

        return std::unexpected("Синтаксична помилка: очікувалося число або '('");
    }

    // <Term> ::= <Factor> { ("*" | "/") <Factor> }
    std::expected<double, std::string> parse_term() {
        auto left_res = parse_factor();
        if (!left_res) return left_res;
        double left = *left_res;

        while (current_.type == TokenType::Star || current_.type == TokenType::Slash) {
            TokenType op = current_.type;
            advance();
            auto right_res = parse_factor();
            if (!right_res) return right_res;
            double right = *right_res;

            if (op == TokenType::Star) {
                left *= right;
            } else {
                if (right == 0.0) {
                    return std::unexpected("Арифметична помилка: ділення на нуль");
                }
                left /= right;
            }
        }
        return left;
    }

    // <Expr> ::= <Term> { ("+" | "-") <Term> }
    std::expected<double, std::string> parse_expr() {
        auto left_res = parse_term();
        if (!left_res) return left_res;
        double left = *left_res;

        while (current_.type == TokenType::Plus || current_.type == TokenType::Minus) {
            TokenType op = current_.type;
            advance();
            auto right_res = parse_term();
            if (!right_res) return right_res;
            double right = *right_res;

            if (op == TokenType::Plus) {
                left += right;
            } else {
                left -= right;
            }
        }
        return left;
    }
};

int main() {
    const std::vector<std::string_view> test_cases = {
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "100 / (2 + 3) * 4 - 5",
        "-5 * (2 + 3)",
        "3 + (4 * 2",
        "10 / 0",
        "42 abc"
    };

    for (const auto& expr : test_cases) {
        ArithmeticParser parser(expr);
        auto result = parser.parse();
        if (result) {
            std::cout << "[УСПІХ]   \"" << expr << "\" = " << *result << '\n';
        } else {
            std::cout << "[ПОМИЛКА] \"" << expr << "\" -> " << result.error() << '\n';
        }
    }
    return 0;
}
