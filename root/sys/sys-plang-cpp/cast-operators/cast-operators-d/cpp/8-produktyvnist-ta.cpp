#include <concepts>
#include <memory>
#include <iostream>

class ASTNode {
public:
    enum class Kind {
        kExpr,
        kStmt,
        kDecl
    };

    explicit constexpr ASTNode(Kind k) noexcept : kind_(k) {}
    [[nodiscard]] constexpr Kind get_kind() const noexcept { return kind_; }
    virtual ~ASTNode() = default;

private:
    Kind kind_;
};

class ExprNode final : public ASTNode {
public:
    explicit constexpr ExprNode(int val) noexcept
        : ASTNode(Kind::kExpr), value_(val) {}

    // Метод перевірки типу для системи LLVM-style RTTI
    static bool classof(const ASTNode* node) noexcept {
        return node && node->get_kind() == Kind::kExpr;
    }

    [[nodiscard]] int get_value() const noexcept { return value_; }

private:
    int value_;
};

// Реалізація власного шаблону dyn_cast
template <typename Target, typename Source>
Target* fast_dyn_cast(Source* src) noexcept {
    if (Target::classof(src)) {
        // Оскільки перевірку тегу пройдено, static_cast є на 100% безпечним і безкоштовним!
        return static_cast<Target*>(src);
    }
    return nullptr;
}
