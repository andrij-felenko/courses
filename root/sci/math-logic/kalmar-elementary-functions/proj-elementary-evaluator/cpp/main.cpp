#include <iostream>
#include <memory>
#include <vector>
#include <variant>
#include <cstdint>
#include <algorithm>
#include <span>
#include <expected>
#include <string_view>

namespace kalmar {

enum class OpType {
    Add, Sub, Mul, Div, Exp, BoundedSum, BoundedProd, BoundedSearch
};

class ExprNode;
using ExprPtr = std::unique_ptr<ExprNode>;

class ExprNode {
public:
    virtual ~ExprNode() = default;
    [[nodiscard]] virtual uint64_t evaluate(std::span<uint64_t> env) const = 0;
    [[nodiscard]] virtual size_t tower_height() const noexcept = 0;
};

class ConstantNode final : public ExprNode {
    uint64_t value_;
public:
    explicit ConstantNode(uint64_t val) noexcept : value_(val) {}
    [[nodiscard]] uint64_t evaluate(std::span<uint64_t>) const override { return value_; }
    [[nodiscard]] size_t tower_height() const noexcept override { return 0; }
};

class VariableNode final : public ExprNode {
    size_t var_idx_;
public:
    explicit VariableNode(size_t idx) noexcept : var_idx_(idx) {}
    [[nodiscard]] uint64_t evaluate(std::span<uint64_t> env) const override {
        return (var_idx_ < env.size()) ? env[var_idx_] : 0;
    }
    [[nodiscard]] size_t tower_height() const noexcept override { return 0; }
};

class BinaryOpNode final : public ExprNode {
    OpType op_;
    ExprPtr left_;
    ExprPtr right_;

    static uint64_t safe_pow(uint64_t base, uint64_t exp) noexcept {
        if (exp == 0) return 1;
        if (base == 0) return 0;
        uint64_t res = 1;
        uint64_t b = base;
        while (exp > 0) {
            if (exp & 1) res *= b;
            b *= b;
            exp >>= 1;
        }
        return res;
    }

public:
    BinaryOpNode(OpType op, ExprPtr l, ExprPtr r) noexcept
        : op_(op), left_(std::move(l)), right_(std::move(r)) {}

    [[nodiscard]] uint64_t evaluate(std::span<uint64_t> env) const override {
        const uint64_t l = left_->evaluate(env);
        const uint64_t r = right_->evaluate(env);

        switch (op_) {
            case OpType::Add: return l + r;
            case OpType::Sub: return (l >= r) ? (l - r) : 0; // Зрізане віднімання
            case OpType::Mul: return l * r;
            case OpType::Div: return (r != 0) ? (l / r) : 0; // Div(x, 0) = 0
            case OpType::Exp: return safe_pow(l, r);
            default: return 0;
        }
    }

    [[nodiscard]] size_t tower_height() const noexcept override {
        const size_t hl = left_->tower_height();
        const size_t hr = right_->tower_height();
        const size_t base_h = std::max(hl, hr);
        return (op_ == OpType::Exp) ? (base_h + 1) : base_h;
    }
};

class BoundedQuantifierNode final : public ExprNode {
    OpType op_;
    size_t var_idx_;
    ExprPtr bound_;
    ExprPtr body_;

public:
    BoundedQuantifierNode(OpType op, size_t var_idx, ExprPtr bound, ExprPtr body) noexcept
        : op_(op), var_idx_(var_idx), bound_(std::move(bound)), body_(std::move(body)) {}

    [[nodiscard]] uint64_t evaluate(std::span<uint64_t> env) const override {
        const uint64_t limit = bound_->evaluate(env);

        if (op_ == OpType::BoundedSum) {
            uint64_t sum = 0;
            for (uint64_t z = 0; z <= limit; ++z) {
                if (var_idx_ < env.size()) env[var_idx_] = z;
                sum += body_->evaluate(env);
            }
            return sum;
        }

        if (op_ == OpType::BoundedProd) {
            uint64_t prod = 1;
            for (uint64_t z = 0; z <= limit; ++z) {
                if (var_idx_ < env.size()) env[var_idx_] = z;
                prod *= body_->evaluate(env);
            }
            return prod;
        }

        if (op_ == OpType::BoundedSearch) {
            for (uint64_t z = 0; z <= limit; ++z) {
                if (var_idx_ < env.size()) env[var_idx_] = z;
                if (body_->evaluate(env) == 1) {
                    return z; // Знайдено корінь
                }
            }
            return limit; // Значення за замовчуванням
        }

        return 0;
    }

    [[nodiscard]] size_t tower_height() const noexcept override {
        if (op_ == OpType::BoundedSearch) {
            return bound_->tower_height();
        }
        return body_->tower_height() + 1;
    }
};

// Допоміжні функції-фабрики
inline ExprPtr make_c(uint64_t v) { return std::make_unique<ConstantNode>(v); }
inline ExprPtr make_v(size_t i) { return std::make_unique<VariableNode>(i); }
inline ExprPtr make_add(ExprPtr l, ExprPtr r) { return std::make_unique<BinaryOpNode>(OpType::Add, std::move(l), std::move(r)); }
inline ExprPtr make_sub(ExprPtr l, ExprPtr r) { return std::make_unique<BinaryOpNode>(OpType::Sub, std::move(l), std::move(r)); }
inline ExprPtr make_mul(ExprPtr l, ExprPtr r) { return std::make_unique<BinaryOpNode>(OpType::Mul, std::move(l), std::move(r)); }
inline ExprPtr make_div(ExprPtr l, ExprPtr r) { return std::make_unique<BinaryOpNode>(OpType::Div, std::move(l), std::move(r)); }
inline ExprPtr make_exp(ExprPtr l, ExprPtr r) { return std::make_unique<BinaryOpNode>(OpType::Exp, std::move(l), std::move(r)); }

inline ExprPtr make_sum(size_t var_idx, ExprPtr bound, ExprPtr body) {
    return std::make_unique<BoundedQuantifierNode>(OpType::BoundedSum, var_idx, std::move(bound), std::move(body));
}
inline ExprPtr make_prod(size_t var_idx, ExprPtr bound, ExprPtr body) {
    return std::make_unique<BoundedQuantifierNode>(OpType::BoundedProd, var_idx, std::move(bound), std::move(body));
}
inline ExprPtr make_search(size_t var_idx, ExprPtr bound, ExprPtr pred) {
    return std::make_unique<BoundedQuantifierNode>(OpType::BoundedSearch, var_idx, std::move(bound), std::move(pred));
}

} // namespace kalmar

int main() {
    using namespace kalmar;

    std::vector<uint64_t> env(8, 0);

    // Приклад 1. Факторіал n!
    // env[0] = n, env[1] = z
    ExprPtr fact_ast = make_prod(1, make_sub(make_v(0), make_c(1)), make_add(make_v(1), make_c(1)));

    std::cout << "Tower height of Factorial AST: " << fact_ast->tower_height() << "\n";

    env[0] = 6;
    std::cout << "6! = " << fact_ast->evaluate(env) << "\n";

    // Приклад 2. Пошук найменшого нетривіального дільника (> 1) для n
    ExprPtr div_term = make_mul(make_v(1), make_div(make_v(0), make_v(1)));
    ExprPtr rem_term = make_sub(make_v(0), std::move(div_term));
    ExprPtr rem_is_zero = make_sub(make_c(1), std::move(rem_term));
    ExprPtr z_gt_1 = make_sub(make_v(1), make_c(1));
    ExprPtr is_factor = make_mul(std::move(rem_is_zero),
                            make_sub(make_c(1), make_sub(make_c(1), std::move(z_gt_1))));

    ExprPtr find_factor_ast = make_search(1, make_v(0), std::move(is_factor));

    env[0] = 77; // 77 = 7 * 11
    std::cout << "Smallest divisor of 77 (> 1): " << find_factor_ast->evaluate(env) << "\n";

    return 0;
}
