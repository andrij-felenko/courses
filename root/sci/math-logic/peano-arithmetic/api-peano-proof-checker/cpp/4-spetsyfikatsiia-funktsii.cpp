#include <expected>
#include <string_view>

namespace peano::verifier {

// Перевірка одного кроку доведення
StatusCode verify_step(const ProofContext& ctx, size_t current_step_idx) noexcept;

// Повна перевірка доведення із поверненням детального статусу
std::expected<void, std::pair<uint32_t, StatusCode>> verify_proof(const ProofContext& ctx) noexcept;

// Аналіз формули на належність до схеми індукції
bool is_induction_instance(const void* formula_ast, std::string_view var_name) noexcept;

} // namespace peano::verifier
