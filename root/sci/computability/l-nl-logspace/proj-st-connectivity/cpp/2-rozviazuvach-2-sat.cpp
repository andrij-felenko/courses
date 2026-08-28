// C++20 implementation: Functional zero-alloc 2-SAT Evaluator
#include <iostream>
#include <span>
#include <array>
#include <cstdint>
#include <optional>

namespace space_complexity {

struct Literal {
    int32_t id; // Positive for x_i, negative for NOT x_i

    [[nodiscard]] constexpr Literal operator-() const noexcept {
        return Literal{-id};
    }
};

struct Clause2 {
    Literal first;
    Literal second;
};

class Formula2SATView {
public:
    constexpr Formula2SATView(uint32_t num_vars, std::span<const Clause2> clauses) noexcept
        : num_vars_(num_vars), clauses_(clauses) {}

    [[nodiscard]] constexpr uint32_t num_variables() const noexcept {
        return num_vars_;
    }

    [[nodiscard]] constexpr uint32_t total_nodes() const noexcept {
        return 2 * num_vars_;
    }

    [[nodiscard]] constexpr uint32_t literal_to_node(Literal lit) const noexcept {
        if (lit.id > 0) {
            return static_cast<uint32_t>(lit.id - 1);
        }
        return static_cast<uint32_t>(-lit.id - 1) + num_vars_;
    }

    [[nodiscard]] bool has_implication(uint32_t u, uint32_t v) const noexcept {
        for (const auto& clause : clauses_) {
            const uint32_t not_a = literal_to_node(-clause.first);
            const uint32_t pos_b = literal_to_node(clause.second);
            const uint32_t not_b = literal_to_node(-clause.second);
            const uint32_t pos_a = literal_to_node(clause.first);

            if ((u == not_a && v == pos_b) || (u == not_b && v == pos_a)) {
                return true;
            }
        }
        return false;
    }

private:
    uint32_t num_vars_;
    std::span<const Clause2> clauses_;
};

class Evaluator2SAT {
public:
    [[nodiscard]] static bool solve(const Formula2SATView& formula) noexcept {
        const uint32_t n_nodes = formula.total_nodes();

        for (uint32_t i = 1; i <= formula.num_variables(); ++i) {
            const Literal x{static_cast<int32_t>(i)};
            const uint32_t pos_node = formula.literal_to_node(x);
            const uint32_t neg_node = formula.literal_to_node(-x);

            if (can_reach(formula, pos_node, neg_node, n_nodes) &&
                can_reach(formula, neg_node, pos_node, n_nodes)) {
                return false;
            }
        }
        return true;
    }

private:
    static bool can_reach(const Formula2SATView& formula, uint32_t u, uint32_t v, uint32_t steps) noexcept {
        if (u == v) return true;
        if (steps == 1) return formula.has_implication(u, v);

        const uint32_t half = (steps + 1) / 2;
        const uint32_t total = formula.total_nodes();

        for (uint32_t w = 0; w < total; ++w) {
            if (can_reach(formula, u, w, half) && can_reach(formula, w, v, steps - half)) {
                return true;
            }
        }
        return false;
    }
};

} // namespace space_complexity

int main() {
    using namespace space_complexity;

    constexpr std::array<Clause2, 4> clauses = {{
        { Literal{1},  Literal{2} },
        { Literal{-1}, Literal{2} },
        { Literal{1},  Literal{-2} },
        { Literal{-1}, Literal{-2} }
    }};

    Formula2SATView formula(2, clauses);
    const bool is_satisfiable = Evaluator2SAT::solve(formula);

    std::cout << "2-SAT Evaluation Result: " 
              << (is_satisfiable ? "SATISFIABLE" : "UNSATISFIABLE") << "\n";

    return 0;
}
