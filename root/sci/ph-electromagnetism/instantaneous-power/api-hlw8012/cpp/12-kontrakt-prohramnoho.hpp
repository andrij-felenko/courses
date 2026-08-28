#pragma once
#include <cstdint>
#include <optional>
#include <algorithm>

namespace drivers {

// Структура конфігурації калібрувальних коефіцієнтів
struct Hlw8012Config {
    double k_p{0.0};                     // Калібрувальний множник потужності (Вт/Гц)
    double k_v{0.0};                     // Калібрувальний множник напруги (В/Гц)
    double k_i{0.0};                     // Калібрувальний множник струму (А/Гц)
    uint32_t pulse_timeout_us{2000000};  // Таймаут відсутності імпульсів (2 сек -> 0 Вт)
    double min_power_w{0.5};             // Поріг відсічки малого навантаження (Вт)
};

// Структура підсумкових розрахованих метрик
struct Hlw8012Readings {
    double active_power{0.0};   // Активна потужність, Вт
    double v_rms{0.0};          // Діюча напруга, В
    double i_rms{0.0};          // Діючий струм, А
    double apparent_power{0.0}; // Повна потужність, В·А
    double power_factor{1.0};   // Коефіцієнт потужності, cos φ
};

class Hlw8012Driver {
public:
    explicit Hlw8012Driver(const Hlw8012Config& config) noexcept;

    // Обробка апаратного переривання по фронту імпульсу CF (Active Power)
    void on_cf_pulse(uint32_t timestamp_us) noexcept;

    // Обробка апаратного переривання по фронту імпульсу CF1 (Voltage/Current)
    void on_cf1_pulse(uint32_t timestamp_us) noexcept;

    // Переключення режиму виходу CF1 (SEL pin state)
    void set_sel_state(bool is_voltage_mode) noexcept;

    // Отримання поточного стану вибору SEL
    [[nodiscard]] bool is_voltage_mode() const noexcept { return is_voltage_mode_; }

    // Обчислення поточних метрологічних метрик
    [[nodiscard]] Hlw8012Readings get_readings(uint32_t current_time_us) noexcept;

private:
    Hlw8012Config config_;
    bool is_voltage_mode_{true};

    uint32_t last_cf_time_{0};
    uint32_t cf_period_us_{0};

    uint32_t last_cf1_time_{0};
    uint32_t cf1_v_period_us_{0};
    uint32_t cf1_i_period_us_{0};
};

} // namespace drivers
