#ifndef EMA_FILTER_HPP
#define EMA_FILTER_HPP

#include <type_traits>
#include <algorithm>

/**
 * @file ema_filter.hpp
 * @brief Шаблонований клас експоненційного ковзного усереднення (EMA) для цифрового згладжування завад АЦП.
 */

/**
 * @brief Шаблонований фільтр Exponential Moving Average (EMA).
 *
 * Алгоритм фільтрації описується рівнянням:
 *   y[n] = alpha * x[n] + (1 - alpha) * y[n-1]
 *
 * де:
 * - x[n] — поточний сирий відлік (від потенціометра або магнітного енкодера);
 * - y[n] — відфільтроване значення;
 * - y[n-1] — попереднє відфільтроване значення;
 * - alpha (0.0 < alpha <= 1.0) — коефіцієнт згладжування.
 *
 * @tparam T Числовий тип даних для внутрішніх обчислень (float або double).
 */
template <typename T = float>
class EmaFilter {
    static_assert(std::is_floating_point_v<T>, "EmaFilter вимагає дійсного типу даних (float/double).");

public:
    /**
     * @brief Конструктор за замовчуванням / параметризований конструктор.
     * @param alpha Коефіцієнт фільтрації. Значення поблизу 0.1 дають сильне придушення завад,
     *              значення поблизу 1.0 мінімізують затримку відгуку.
     */
    explicit EmaFilter(T alpha = static_cast<T>(0.2)) noexcept
        : alpha_(std::clamp(alpha, static_cast<T>(0.001), static_cast<T>(1.0))),
          current_val_(static_cast<T>(0)),
          initialized_(false) {}

    /**
     * @brief Додавання нового відліку та перерахунок відфільтрованого значення.
     * @param raw_val Новий сирий відлік АЦП.
     * @return Поточне відфільтроване значення.
     */
    T update(T raw_val) noexcept {
        if (!initialized_) {
            // Перше значення ініціалізує стан, уникаючи перехідного стрибка від 0
            current_val_ = raw_val;
            initialized_ = true;
        } else {
            current_val_ = alpha_ * raw_val + (static_cast<T>(1.0) - alpha_) * current_val_;
        }
        return current_val_;
    }

    /**
     * @brief Отримання поточного відфільтрованого значення без внесення нових даних.
     */
    [[nodiscard]] T value() const noexcept {
        return current_val_;
    }

    /**
     * @brief Скидання стану фільтра до неініціалізованого.
     */
    void reset() noexcept {
        initialized_ = false;
        current_val_ = static_cast<T>(0);
    }

    /**
     * @brief Встановлення початкового значення фільтра та встановлення прапорця ініціалізації.
     * @param initial_val Початковий відлік для фільтра.
     */
    void reset(T initial_val) noexcept {
        current_val_ = initial_val;
        initialized_ = true;
    }

    /**
     * @brief Оновлення значення коефіцієнта alpha.
     * @param alpha Нове значення коефіцієнта згладжування [0.001, 1.0].
     */
    void set_alpha(T alpha) noexcept {
        alpha_ = std::clamp(alpha, static_cast<T>(0.001), static_cast<T>(1.0));
    }

    /**
     * @brief Отримання поточного значення alpha.
     */
    [[nodiscard]] T alpha() const noexcept {
        return alpha_;
    }

    /**
     * @brief Перевірка, чи був фільтр ініціалізований хоча б одним відліком.
     */
    [[nodiscard]] bool is_initialized() const noexcept {
        return initialized_;
    }

private:
    T alpha_;          ///< Коефіцієнт згладжування
    T current_val_;    ///< Поточне накопичене значення
    bool initialized_; ///< Прапорець первинної ініціалізації
};

#endif // EMA_FILTER_HPP
