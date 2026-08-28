#include <cstdint>

namespace p_poly {

/**
 * @brief Структурний опис метаданих булевої схеми C_n (C++ API)
 */
struct CircuitHeader {
    std::uint32_t input_length{0};   // Довжина входу n = |x|
    std::uint32_t advice_length{0};  // Довжина підказки |a_n| <= p(n)
    std::uint32_t gate_count{0};     // Загальна кількість гейтів у схемі
    std::uint32_t max_depth{0};      // Максимальна глибина DAG
};

} // namespace p_poly
