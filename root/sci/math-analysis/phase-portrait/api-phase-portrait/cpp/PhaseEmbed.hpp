// PhaseEmbed.hpp — Високорівневий C++20 модуль фазової реконструкції
#ifndef PHASE_EMBED_HPP
#define PHASE_EMBED_HPP

#include <span>
#include <vector>
#include <expected>
#include <cstddef>

namespace phase {

struct EmbedConfig {
    double delay_tau{1.0};
    std::size_t dim{2};
};

/**
 * @brief Оцінити оптимальну часову затримку tau за першим нулем автокореляції.
 * @param signal Вхідний часовий ряд у вигляді span.
 * @return Оптимальне значення tau у відліках або код помилки.
 */
[[nodiscard]] std::expected<std::size_t, ErrorCode>
estimate_delay_tau(std::span<const double> signal) noexcept;

/**
 * @brief Реконструювати фазову траєкторію за допомогою вектора затримок.
 * @param signal Скалярний сигнал x(t).
 * @param config Параметри вкладення.
 * @return Масив реконструйованих векторів Y(t) або код помилки.
 */
[[nodiscard]] std::expected<std::vector<double>, ErrorCode>
reconstruct_portrait(std::span<const double> signal, const EmbedConfig& config);

} // namespace phase

#endif // PHASE_EMBED_HPP
