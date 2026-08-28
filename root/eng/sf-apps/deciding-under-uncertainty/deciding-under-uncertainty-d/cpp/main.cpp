// Спайк: одноразова проба ОДНІЄЇ небезпеки — пропускної здатності.
// Мета не «код у прод», а факт: витримує чи ні. Після заміру — викинути.
#include <cstdint>

struct SpikeResult {
    std::uint32_t target_rate;   // цільовий потік, повідомлень/с
    std::uint32_t observed_rate; // що показав замір під навантаженням
    double        observed_p99;  // 99-й перцентиль затримки, мс
};

// Пороги — з бюджету якісних атрибутів, а не «на око».
constexpr std::uint32_t RATE_BUDGET = 10000;   // менше — гіпотеза провалена
constexpr double        P99_BUDGET  = 50.0;    // більше — теж провал

bool hypothesis_holds(const SpikeResult &r) {
    return (r.observed_rate >= RATE_BUDGET)
        && (r.observed_p99  <= P99_BUDGET);
}

// Рішення керує не думка, а результат спайка:
void decide_broker(const SpikeResult &r) {
    if (hypothesis_holds(r))
        commit_broker();          // факт підтвердив — будуємо на ньому
    else
        reject_and_try_next(r);   // факт спростував — гілка закрита за день
}
