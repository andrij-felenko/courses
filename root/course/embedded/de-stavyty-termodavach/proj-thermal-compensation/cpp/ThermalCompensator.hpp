// ThermalCompensator.hpp - Ідіоматична C++17/20 реалізація
#pragma once

#include <algorithm>
#include <chrono>
#include <cmath>

namespace embedded::thermal {

/**
 * @brief Калібрувальні константи теплової моделі друкованої плати
 */
struct ThermalConfig {
    float r_th1{12.0f};         // Тепловий опір 1-ї ланки (корпус), К/Вт
    float tau1{8.0f};           // Постійна часу 1-ї ланки, секунди
    float r_th2{45.0f};         // Тепловий опір 2-ї ланки (текстоліт плати), К/Вт
    float tau2{120.0f};         // Постійна часу 2-ї ланки, секунди
    float p_quiescent{0.080f};  // Базова теплова потужність у спокої, Вт
    float p_wifi_tx{0.650f};    // Теплова потужність радіопередавача під час TX, Вт
    float p_cpu_active{0.200f}; // Тепловиділення CPU при повному завантаженні, Вт
};

/**
 * @brief Клас динамічного спостерігача теплового стану
 */
class ThermalCompensator {
public:
    explicit ThermalCompensator(const ThermalConfig& config, std::chrono::milliseconds sample_period)
        : config_(config), dt_(std::chrono::duration<float>(sample_period).count()) {
        recalculate_coefficients();
    }

    void reset() noexcept {
        state_t1_ = 0.0f;
        state_t2_ = 0.0f;
    }

    void set_state(float initial_self_heat) noexcept {
        const float r_total = config_.r_th1 + config_.r_th2;
        if (r_total > 0.0f) {
            state_t1_ = initial_self_heat * (config_.r_th1 / r_total);
            state_t2_ = initial_self_heat * (config_.r_th2 / r_total);
        } else {
            state_t1_ = 0.0f;
            state_t2_ = initial_self_heat;
        }
    }

    void set_sample_period(std::chrono::milliseconds period) noexcept {
        dt_ = std::chrono::duration<float>(period).count();
        recalculate_coefficients();
    }

    [[nodiscard]] float update(float raw_temperature_celsius,
                               float cpu_load,
                               float tx_duty_cycle) noexcept {
        const float clamped_cpu = std::clamp(cpu_load, 0.0f, 1.0f);
        const float clamped_tx = std::clamp(tx_duty_cycle, 0.0f, 1.0f);

        // 1. Оцінка сумарної теплової потужності компонентів
        const float p_total = config_.p_quiescent +
                              (config_.p_cpu_active * clamped_cpu) +
                              (config_.p_wifi_tx * clamped_tx);

        // 2. Чисельне оновлення швидкої ланки кристала
        const float target_t1 = config_.r_th1 * p_total;
        state_t1_ = (alpha1_ * state_t1_) + ((1.0f - alpha1_) * target_t1);

        // 3. Чисельне оновлення повільної ланки масиву плати
        const float target_t2 = config_.r_th2 * p_total;
        state_t2_ = (alpha2_ * state_t2_) + ((1.0f - alpha2_) * target_t2);

        // 4. Віднімання динамічної поправки від показань сенсора
        const float self_heat_delta = state_t1_ + state_t2_;
        return raw_temperature_celsius - self_heat_delta;
    }

    [[nodiscard]] float estimated_self_heating() const noexcept {
        return state_t1_ + state_t2_;
    }

private:
    void recalculate_coefficients() noexcept {
        alpha1_ = (config_.tau1 > 0.0f) ? std::exp(-dt_ / config_.tau1) : 0.0f;
        alpha2_ = (config_.tau2 > 0.0f) ? std::exp(-dt_ / config_.tau2) : 0.0f;
    }

    ThermalConfig config_;
    float dt_{1.0f};
    float alpha1_{0.0f};
    float alpha2_{0.0f};
    float state_t1_{0.0f};
    float state_t2_{0.0f};
};

} // namespace embedded::thermal
