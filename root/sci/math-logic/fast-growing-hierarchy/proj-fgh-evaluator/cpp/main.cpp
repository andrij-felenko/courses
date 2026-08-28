#include <iostream>
#include <memory>
#include <variant>
#include <vector>
#include <cstdint>
#include <optional>

enum class OrdinalKind { Zero, Finite, Term };

struct OrdinalNode;
using OrdinalPtr = std::unique_ptr<OrdinalNode>;

struct OrdinalNode {
    OrdinalKind kind{OrdinalKind::Zero};
    uint64_t finite_val{0};
    OrdinalPtr exponent{nullptr};
    uint64_t coeff{0};
    OrdinalPtr tail{nullptr};

    OrdinalNode() = default;
    
    static OrdinalPtr make_zero() {
        return std::make_unique<OrdinalNode>();
    }

    static OrdinalPtr make_finite(uint64_t val) {
        if (val == 0) return make_zero();
        auto node = std::make_unique<OrdinalNode>();
        node->kind = OrdinalKind::Finite;
        node->finite_val = val;
        return node;
    }

    static OrdinalPtr make_term(OrdinalPtr exp, uint64_t c, OrdinalPtr t = nullptr) {
        auto node = std::make_unique<OrdinalNode>();
        node->kind = OrdinalKind::Term;
        node->exponent = std::move(exp);
        node->coeff = c;
        node->tail = std::move(t);
        return node;
    }

    OrdinalPtr clone() const {
        auto node = std::make_unique<OrdinalNode>();
        node->kind = kind;
        node->finite_val = finite_val;
        node->coeff = coeff;
        if (exponent) node->exponent = exponent->clone();
        if (tail) node->tail = tail->clone();
        return node;
    }
};

struct EvalStats {
    uint64_t total_steps{0};
    uint64_t max_depth{0};
    uint64_t current_depth{0};
    bool limit_exceeded{false};
};

class FGHInterpreter {
public:
    static bool is_limit(const OrdinalNode* node) {
        if (!node || node->kind != OrdinalKind::Term) return false;
        if (node->tail && node->tail->kind != OrdinalKind::Zero) {
            return is_limit(node->tail.get());
        }
        return (node->exponent->kind != OrdinalKind::Zero);
    }

    static OrdinalPtr fundamental_sequence(const OrdinalNode* lambda, uint64_t n) {
        if (!lambda || lambda->kind != OrdinalKind::Term) {
            return OrdinalNode::make_zero();
        }

        if (lambda->tail && lambda->tail->kind != OrdinalKind::Zero) {
            return OrdinalNode::make_term(
                lambda->exponent->clone(),
                lambda->coeff,
                fundamental_sequence(lambda->tail.get(), n)
            );
        }

        if (lambda->coeff > 1) {
            auto single = OrdinalNode::make_term(lambda->exponent->clone(), 1);
            auto reduced = fundamental_sequence(single.get(), n);
            return OrdinalNode::make_term(lambda->exponent->clone(), lambda->coeff - 1, std::move(reduced));
        }

        if (lambda->exponent->kind == OrdinalKind::Finite && lambda->exponent->finite_val == 1) {
            return OrdinalNode::make_finite(n);
        }

        if (!is_limit(lambda->exponent.get())) {
            auto exp_minus_1 = fundamental_sequence(lambda->exponent.get(), 1);
            return OrdinalNode::make_term(std::move(exp_minus_1), n);
        } else {
            auto exp_fund = fundamental_sequence(lambda->exponent.get(), n);
            return OrdinalNode::make_term(std::move(exp_fund), 1);
        }
    }

    uint64_t eval(const OrdinalNode* alpha, uint64_t n, EvalStats& stats, uint64_t max_steps = 1000000) {
        stats.total_steps++;
        stats.current_depth++;
        if (stats.current_depth > stats.max_depth) {
            stats.max_depth = stats.current_depth;
        }

        if (stats.total_steps > max_steps) {
            stats.limit_exceeded = true;
            stats.current_depth--;
            return n;
        }

        if (!alpha || alpha->kind == OrdinalKind::Zero) {
            stats.current_depth--;
            return n + 1;
        }

        if (alpha->kind == OrdinalKind::Finite) {
            if (alpha->finite_val == 0) {
                stats.current_depth--;
                return n + 1;
            }
            auto prev = OrdinalNode::make_finite(alpha->finite_val - 1);
            uint64_t acc = n;
            for (uint64_t i = 0; i < n; ++i) {
                acc = eval(prev.get(), acc, stats, max_steps);
                if (stats.limit_exceeded) break;
            }
            stats.current_depth--;
            return acc;
        }

        auto fund = fundamental_sequence(alpha, n);
        uint64_t res = eval(fund.get(), n, stats, max_steps);
        stats.current_depth--;
        return res;
    }
};

int main() {
    FGHInterpreter interpreter;
    EvalStats stats;

    // Створення ординала ω = ω^1 * 1
    auto omega = OrdinalNode::make_term(OrdinalNode::make_finite(1), 1);

    std::cout << "--- Двигун обчислення FGH (C++) ---\n";
    uint64_t res = interpreter.eval(omega.get(), 3, stats);
    std::cout << "F_omega(3) = " << res 
              << " (Кроків: " << stats.total_steps 
              << ", Макс. глибина: " << stats.max_depth << ")\n";

    return 0;
}
