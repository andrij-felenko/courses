#pragma once

namespace gimbal {

/// @brief Цифровий режекторний фільтр другого порядку (Direct Form II)
/// Використовується для усунення механічних резонансів і вібрацій у контурі регулювання
class NotchFilter {
public:
    NotchFilter() = default;

    /// @brief Конструктор із миттєвою розрахунковою ініціалізацією
    /// @param center_freq_hz Центральна частота пригнічення (Гц)
    /// @param bandwidth_hz Ширина смуги затухання (Гц)
    /// @param sample_rate_hz Частота дискретизації контуру (Гц)
    NotchFilter(float center_freq_hz, float bandwidth_hz, float sample_rate_hz);

    /// @brief Обчислення коефіцієнтів режекторного фільтра за допомогою білінійного Z-перетворення
    /// @param center_freq_hz Центральна резонансна частота
    /// @param bandwidth_hz Ширина смуги режекції
    /// @param sample_rate_hz Частота оновлення системи
    void configure(float center_freq_hz, float bandwidth_hz, float sample_rate_hz);

    /// @brief Проходження одного відліку сигналу через різницеве рівняння фільтра
    /// @param input Вхідний зашумлений сигнал (наприклад, кутова швидкість)
    /// @return Фільтроване значення сигналу без резонансної компоненти
    float update(float input);

    /// @brief Очищення внутрішнього стану та затримок фільтра
    void reset();

private:
    // Коефіцієнти чисельника та знаменника передавальної функції
    float b0_{1.0f}, b1_{0.0f}, b2_{0.0f};
    float a1_{0.0f}, a2_{0.0f};

    // Змінні внутрішнього стану Direct Form II
    float w1_{0.0f};
    float w2_{0.0f};

    bool configured_{false};
};

} // namespace gimbal
