#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <cstdint>
#include <span>

enum class OpType {
    Var,
    Not,
    And,
    Or,
    Xor,
    Implies
};

// Базовий абстрактний вузол синтаксичного дерева з RAII
class ExprNode {
public:
    virtual ~ExprNode() = default;
    [[nodiscard]] virtual bool evaluate(uint32_t stateMask) const noexcept = 0;
};

// Вузол логічної змінної
class VariableNode final : public ExprNode {
    int varIndex;
public:
    explicit VariableNode(int index) noexcept : varIndex(index) {}
    
    [[nodiscard]] bool evaluate(uint32_t stateMask) const noexcept override {
        return (stateMask & (1U << varIndex)) != 0;
    }
};

// Вузол унарного заперечення (NOT)
class NotNode final : public ExprNode {
    std::unique_ptr<ExprNode> operand;
public:
    explicit NotNode(std::unique_ptr<ExprNode> op) noexcept : operand(std::move(op)) {}
    
    [[nodiscard]] bool evaluate(uint32_t stateMask) const noexcept override {
        return !operand->evaluate(stateMask);
    }
};

// Вузол бінарних логічних операцій
class BinaryOpNode final : public ExprNode {
    OpType op;
    std::unique_ptr<ExprNode> left;
    std::unique_ptr<ExprNode> right;
public:
    BinaryOpNode(OpType operation, std::unique_ptr<ExprNode> lhs, std::unique_ptr<ExprNode> rhs) noexcept
        : op(operation), left(std::move(lhs)), right(std::move(rhs)) {}

    [[nodiscard]] bool evaluate(uint32_t stateMask) const noexcept override {
        const bool l = left->evaluate(stateMask);
        const bool r = right->evaluate(stateMask);
        switch (op) {
            case OpType::And:     return l && r;
            case OpType::Or:      return l || r;
            case OpType::Xor:     return l ^ r;
            case OpType::Implies: return !l || r;
            default:              return false;
        }
    }
};

// Клас генератора таблиць та верифікатора формул
class TruthTableEngine {
public:
    static void generateAndVerify(const ExprNode& root, std::span<const std::string_view> varNames) {
        const size_t numVars = varNames.size();
        if (numVars > 31) {
            std::cerr << "Помилка: підтримується не більше 31 змінної.\n";
            return;
        }

        // Вивід заголовка
        for (const auto& name : varNames) {
            std::cout << name << '\t';
        }
        std::cout << "| Результат\n";
        std::cout << std::string(numVars * 8 + 12, '-') << '\n';

        const uint32_t totalRows = 1U << numVars;
        uint32_t trueCount = 0;

        for (uint32_t mask = 0; mask < totalRows; ++mask) {
            for (size_t i = 0; i < numVars; ++i) {
                const bool bit = (mask & (1U << i)) != 0;
                std::cout << (bit ? 1 : 0) << '\t';
            }
            const bool result = root.evaluate(mask);
            if (result) {
                trueCount++;
            }
            std::cout << "| " << (result ? 1 : 0) << '\n';
        }

        std::cout << "\nСтатистика: " << trueCount << "/" << totalRows << " істинних наборів.\n";
        if (trueCount == totalRows) {
            std::cout << "Висновок: Формула є ТАВТОЛОГІЄЮ (завжди істинна).\n";
        } else if (trueCount == 0) {
            std::cout << "Висновок: Формула є СУПЕРЕЧНІСТЮ (тотожна хиба).\n";
        } else {
            std::cout << "Висновок: Формула є ЗДІЙСНЮВАНОЮ (випадкова логічна функція).\n";
        }
    }
};

int main() {
    // Верифікуємо Закон Контрапозиції: (P => Q) => (!Q => !P)
    const std::vector<std::string_view> varNames = {"P", "Q"};

    // Ліва частина: P => Q
    auto p1 = std::make_unique<VariableNode>(0);
    auto q1 = std::make_unique<VariableNode>(1);
    auto leftSide = std::make_unique<BinaryOpNode>(OpType::Implies, std::move(p1), std::move(q1));

    // Права частина: !Q => !P
    auto q2 = std::make_unique<VariableNode>(1);
    auto notQ = std::make_unique<NotNode>(std::move(q2));
    auto p2 = std::make_unique<VariableNode>(0);
    auto notP = std::make_unique<NotNode>(std::move(p2));
    auto rightSide = std::make_unique<BinaryOpNode>(OpType::Implies, std::move(notQ), std::move(notP));

    // Повна формула
    auto root = std::make_unique<BinaryOpNode>(OpType::Implies, std::move(leftSide), std::move(rightSide));

    std::cout << "Перевірка формули закону контрапозиції:\n\n";
    TruthTableEngine::generateAndVerify(*root, varNames);

    return 0;
}
