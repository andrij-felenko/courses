// cpp
#include <cstdint>
#include <functional>

namespace bpp {

enum class AmplificationMode : std::uint8_t {
    FixedRounds = 0, // Фіксоване число раундів k
    TargetError = 1  // Автоматична ампліфікація до заданої хиби epsilon
};

struct BppConfig {
    AmplificationMode mode{AmplificationMode::FixedRounds};
    std::uint32_t     rounds_k{30};         // Кількість повторень
    double            max_error_eps{1e-9};  // Максимальна допустима хиба (наприклад, 1e-12)
    void*             rng_context{nullptr}; // Контекст генератора випадкових чисел
    std::function<std::uint64_t(void*)> rng_next_u64{}; // Функція вибірки 64 випадкових бітів
};

} // namespace bpp
