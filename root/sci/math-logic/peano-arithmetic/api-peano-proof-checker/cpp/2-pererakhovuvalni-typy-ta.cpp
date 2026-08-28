#include <cstdint>
#include <cstddef>
#include <vector>
#include <memory>
#include <string_view>
#include <expected>

namespace peano::verifier {

enum class RuleType : uint32_t {
    AxiomEquality       = 101,  // Аксіоми рівності (=)
    AxiomPeano1         = 102,  // ¬(S(x) = 0)
    AxiomPeano2         = 103,  // S(x) = S(y) → x = y
    AxiomAddBase        = 104,  // x + 0 = x
    AxiomAddSucc        = 105,  // x + S(y) = S(x + y)
    AxiomMulBase        = 106,  // x · 0 = 0
    AxiomMulSucc        = 107,  // x · S(y) = (x · y) + x
    SchemeInduction     = 108,  // Схема індукції
    
    ModusPonens         = 201,  // З A та A → B виводиться B
    Generalization      = 202   // З A(x) виводиться ∀x A(x)
};

enum class StatusCode : uint32_t {
    Success             = 0,
    InvalidStepId       = 1001,
    NotAnAxiom          = 1002,
    MpMismatch          = 1003,
    InductionSchema     = 1004,
    UnboundVariable     = 1005,
    CircularProof       = 1006
};

struct ProofStep {
    uint32_t step_id;           // Номер кроку (1-indexed)
    const void* formula_ast;    // Вказник на AST формули
    RuleType rule;              // Правило виведення
    uint32_t ref_step_1;        // Посилання на 1-шу передумову
    uint32_t ref_step_2;        // Посилання на 2-гу передумову
};

struct ProofContext {
    std::vector<ProofStep> steps;
    uint32_t flags{0};
};

} // namespace peano::verifier
