// cpp
#include <cstdint>
#include <chrono>

namespace bpp {

enum class Status : int32_t {
    SuccessAccept    =  1, // Слово належить мові (прийнято)
    SuccessReject    =  0, // Слово не належить мові (відхилено)
    ErrorInvalidParam = -1, // Некоректні параметри (eps >= 0.5)
    ErrorEntropyFail  = -2, // Збій джерела випадкових чисел
    ErrorTimeout      = -3  // Перевищено часовий ліміт
};

struct ExecutionStats {
    std::uint32_t total_rounds_executed{0}; // Загальна кількість раундів k
    std::uint32_t accept_votes{0};          // Кількість раундів з відповіддю 1
    std::uint32_t reject_votes{0};          // Кількість раундів з відповіддю 0
    double        estimated_error_bound{1.0}; // Межа помилки Чернова
    std::uint64_t entropy_bytes_used{0};    // Обсяг використаної ентропії
    std::chrono::microseconds execution_time{0}; // Час виконання
};

} // namespace bpp
