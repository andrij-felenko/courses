#include <variant>
#include <memory>
#include <iostream>
#include <string>
#include <cmath>

// Структури вузлів синтаксичного дерева
struct Literal {
    double value;
};

struct Add;
struct Multiply;
struct Negate;

// Тип-сума для представлення будь-якого вузла AST
using ExprNode = std::variant<
    Literal,
    std::unique_ptr<Add>,
    std::unique_ptr<Multiply>,
    std::unique_ptr<Negate>
>;

struct Add {
    ExprNode left;
    ExprNode right;
};

struct Multiply {
    ExprNode left;
    ExprNode right;
};

struct Negate {
    ExprNode child;
};

// Ідіома Overloaded для патерн-матчингу
template <typename... Ts>
struct overloaded : Ts... {
    using Ts::operator()...;
};

template <typename... Ts>
overloaded(Ts...) -> overloaded<Ts...>;

// Обчислювач значення AST-дерева через std::visit
double evaluate(const ExprNode& expr) {
    return std::visit(overloaded{
        [](const Literal& num) -> double {
            return num.value;
        },
        [](const std::unique_ptr<Add>& bin) -> double {
            return evaluate(bin->left) + evaluate(bin->right);
        },
        [](const std::unique_ptr<Multiply>& bin) -> double {
            return evaluate(bin->left) * evaluate(bin->right);
        },
        [](const std::unique_ptr<Negate>& un) -> double {
            return -evaluate(un->child);
        }
    }, expr);
}

// Оптимізаційний прохід: Згортання констант (Constant Folding)
ExprNode fold_constants(ExprNode expr) {
    return std::visit(overloaded{
        [](Literal num) -> ExprNode {
            return num;
        },
        [](std::unique_ptr<Add>& bin) -> ExprNode {
            bin->left = fold_constants(std::move(bin->left));
            bin->right = fold_constants(std::move(bin->right));
            
            // Якщо обидва операнди є літералами — обчислюємо їх під час оптимізації!
            if (std::holds_alternative<Literal>(bin->left) && 
                std::holds_alternative<Literal>(bin->right)) {
                double l_val = std::get<Literal>(bin->left).value;
                double r_val = std::get<Literal>(bin->right).value;
                return Literal{l_val + r_val};
            }
            return std::move(bin);
        },
        [](std::unique_ptr<Multiply>& bin) -> ExprNode {
            bin->left = fold_constants(std::move(bin->left));
            bin->right = fold_constants(std::move(bin->right));
            
            if (std::holds_alternative<Literal>(bin->left) && 
                std::holds_alternative<Literal>(bin->right)) {
                double l_val = std::get<Literal>(bin->left).value;
                double r_val = std::get<Literal>(bin->right).value;
                return Literal{l_val * r_val};
            }
            return std::move(bin);
        },
        [](std::unique_ptr<Negate>& un) -> ExprNode {
            un->child = fold_constants(std::move(un->child));
            if (std::holds_alternative<Literal>(un->child)) {
                return Literal{-std::get<Literal>(un->child).value};
            }
            return std::move(un);
        }
    }, expr);
}

int main() {
    // Побудова виразу: (5 + 3) * -2
    ExprNode expr = std::make_unique<Multiply>(Multiply{
        std::make_unique<Add>(Add{ Literal{5.0}, Literal{3.0} }),
        std::make_unique<Negate>(Negate{ Literal{2.0} })
    });

    std::cout << "Результат обчислення AST: " << evaluate(expr) << "\n"; // Друкує -16

    // Виконання оптимізації згортання констант
    ExprNode folded = fold_constants(std::move(expr));

    if (std::holds_alternative<Literal>(folded)) {
        std::cout << "Дерево повністю згорнуто у єдиний літерал: " 
                  << std::get<Literal>(folded).value << "\n";
    }
}
