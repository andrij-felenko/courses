#ifndef SAT_SOLVER_API_HPP
#define SAT_SOLVER_API_HPP

#include <vector>
#include <span>
#include <optional>
#include <cstdint>

namespace sat {

enum class State : uint8_t {
    Unknown = 0,
    Sat     = 10,
    Unsat   = 20
};

enum class LBool : int8_t {
    Undefined = -1,
    False     = 0,
    True      = 1
};

using Var = int32_t;
using Lit = int32_t;

inline Lit make_lit(Var v, bool sign) noexcept {
    return sign ? -v : v;
}

class ISatSolver {
public:
    virtual ~ISatSolver() = default;

    virtual Var new_var() = 0;
    virtual bool add_clause(std::span<const Lit> lits) = 0;
    virtual State solve() = 0;
    virtual State solve(std::span<const Lit> assumptions) = 0;
    [[nodiscard]] virtual std::vector<Lit> get_unsat_core() const = 0;
    [[nodiscard]] virtual LBool model_value(Var v) const = 0;
};

} // namespace sat

#endif /* SAT_SOLVER_API_HPP */
