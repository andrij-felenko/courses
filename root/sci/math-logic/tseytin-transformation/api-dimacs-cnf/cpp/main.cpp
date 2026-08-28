// Ідіоматичний C++20 API для Цейтін-кодера
#include <cstdint>
#include <vector>
#include <string_view>
#include <span>
#include <ostream>
#include <expected>

namespace tseytin {

enum class OpType : std::uint8_t {
    Var,
    Not,
    And,
    Or,
    Implies,
    Xor,
    Equiv
};

using Literal = std::int32_t;
using Variable = std::int32_t;
using Clause = std::vector<Literal>;

class Encoder {
    Variable m_maxVar;
    std::vector<Clause> m_clauses;

public:
    explicit Encoder(std::size_t numInputVars) 
        : m_maxVar(static_cast<Variable>(numInputVars)) {}

    [[nodiscard]] Variable freshVar() noexcept {
        return ++m_maxVar;
    }

    void addClause(std::span<const Literal> lits) {
        m_clauses.emplace_back(lits.begin(), lits.end());
    }

    void encodeAnd(Variable out, Variable in1, Variable in2) {
        addClause(std::array<Literal, 2>{-out, in1});
        addClause(std::array<Literal, 2>{-out, in2});
        addClause(std::array<Literal, 3>{out, -in1, -in2});
    }

    void encodeOr(Variable out, Variable in1, Variable in2) {
        addClause(std::array<Literal, 2>{out, -in1});
        addClause(std::array<Literal, 2>{out, -in2});
        addClause(std::array<Literal, 3>{-out, in1, in2});
    }

    void encodeNot(Variable out, Variable in1) {
        addClause(std::array<Literal, 2>{-out, -in1});
        addClause(std::array<Literal, 2>{out, in1});
    }

    [[nodiscard]] std::expected<void, std::string_view> 
    exportDimacs(std::ostream& os, Variable rootVar) const;
};

} // namespace tseytin
