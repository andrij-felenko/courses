#include <cstdint>
#include <cstddef>

namespace ribbon {

struct Options {
    std::uint16_t width{64};                    // Ширина ковзного вікна стрічки (32, 64, 128)
    std::uint8_t fingerprint_bits{8};           // Кількість бітів відбитка r (4..16)
    std::uint8_t overhead_percent{5};           // Надлишковість слотів у відсотках (2..15%)
    std::uint16_t max_retries{10};              // Максимальна кількість спроб розв'язання
    std::uint64_t initial_seed{0x9e3779b97f4a7c15ULL}; // Початковий seed
    bool use_homogeneous_scaling{true};         // Усунення крайових ефектів
    bool use_interleaved_layout{false};         // Оптимізація кеш-ліній (Interleaved)
};

} // namespace ribbon
