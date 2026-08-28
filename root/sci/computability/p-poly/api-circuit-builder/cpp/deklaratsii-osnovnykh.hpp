#include <span>
#include <cstdint>

namespace p_poly {

/**
 * @brief Безпечний C++20 контракт валідації та виконання оцінювача
 */
Status validate_circuit(
    const CircuitHeader& header,
    std::span<const std::uint8_t> gates_payload
);

Status evaluate(
    const CircuitHeader& header,
    std::span<const std::uint8_t> gates_payload,
    std::span<const std::uint8_t> input_x,
    std::span<const std::uint8_t> advice_a,
    bool& out_result
);

} // namespace p_poly
