#include <iostream>
#include <string>
#include <variant>
#include <memory>
#include <compare>

struct BinaryOp;

using ExprPayload = std::variant<
    int64_t,
    std::string,
    std::unique_ptr<BinaryOp>
>;

struct ExprNode {
    ExprPayload payload;

    // Глибоке тричленне порівняння вузлів дерева
    friend std::strong_ordering operator<=>(const ExprNode& a, const ExprNode& b);
    friend bool operator==(const ExprNode& a, const ExprNode& b);
};

struct BinaryOp {
    char     op{'+'};
    ExprNode left;
    ExprNode right;

    auto operator<=>(const BinaryOp& other) const = default;
};

std::strong_ordering operator<=>(const ExprNode& a, const ExprNode& b) {
    if (a.payload.index() != b.payload.index()) {
        return a.payload.index() <=> b.payload.index();
    }

    return std::visit([&](const auto& valA) -> std::strong_ordering {
        using T = std::decay_t<decltype(valA)>;
        const auto& valB = std::get<T>(b.payload);

        if constexpr (std::is_same_v<T, std::unique_ptr<BinaryOp>>) {
            if (!valA && !valB) return std::strong_ordering::equal;
            if (!valA) return std::strong_ordering::less;
            if (!valB) return std::strong_ordering::greater;
            // Рекурсивне глибоке розіменування
            return *valA <=> *valB;
        } else {
            return valA <=> valB;
        }
    }, a.payload);
}

bool operator==(const ExprNode& a, const ExprNode& b) {
    return (a <=> b) == 0;
}
