namespace godel::api {

enum class StatusCode : uint32_t {
    Success = 0,
    InvalidTokenSequence = 1,
    UnbalancedParentheses = 2,
    FreeVariableMismatch = 3,
    ModusPonensViolation = 4,
    AxiomMismatch = 5,
    IntegerOverflow = 6,
    EmptyProof = 7
};

struct VerificationResult {
    StatusCode code;
    size_t failed_step_index;
    std::string_view error_message;

    [[nodiscard]] bool is_valid() const noexcept {
        return code == StatusCode::Success;
    }
};

using GodelInt = uint64_t;

struct ASTNode {
    uint32_t token_code;
    std::vector<ASTNode> children;
};

struct ProofStep {
    size_t step_id;
    std::vector<uint32_t> tokens;
    GodelInt godel_number;
    std::vector<size_t> premise_indices; // Індекси передумов для Modus Ponens
};

} // namespace godel::api
