/* PowerGovernor.hpp - Адаптивний менеджер живлення сонячного вузла (C++20) */
#pragma once

#include <cstdint>
#include <chrono>
#include <concepts>

namespace embedded::power {

enum class State : uint8_t {
    Normal = 0,    // SoC > 70%: повна функціональність
    Eco,           // 30% < SoC <= 70%: пакетування даних
    Survival,      // 10% < SoC <= 30%: лише маяк стану
    Hibernate,     // SoC <= 10%: глибока консервація
    Recovery       // Очікування заряду після аварійного виснаження
};

struct Config {
    uint16_t v_normal_mv{3350};
    uint16_t v_eco_mv{3250};
    uint16_t v_survival_mv{3100};
    uint16_t v_hibernate_mv{2900};
    uint16_t v_recovery_mv{3400};
    uint16_t v_hysteresis_mv{50};
    int8_t   temp_charge_min_c{0};
    std::chrono::seconds soak_time_required{900};
};

struct Telemetry {
    uint16_t voltage_mv{0};
    int8_t   temp_celsius{0};
    uint16_t charge_current_ma{0};
};

class PowerGovernor {
public:
    explicit constexpr PowerGovernor(const Config& cfg) noexcept 
        : config_(cfg), state_(State::Normal) {}

    void update(const Telemetry& telem, std::chrono::seconds elapsed) noexcept {
        update_temperature_protection(telem.temp_celsius);
        update_state_machine(telem, elapsed);
    }

    [[nodiscard]] constexpr State get_state() const noexcept { return state_; }
    [[nodiscard]] constexpr bool is_charge_enabled() const noexcept { return charge_enabled_; }
    [[nodiscard]] constexpr bool are_sensors_enabled() const noexcept { return sensors_enabled_; }
    [[nodiscard]] constexpr bool is_radio_enabled() const noexcept { return radio_enabled_; }

    [[nodiscard]] constexpr std::chrono::seconds get_sleep_interval() const noexcept {
        using namespace std::chrono_literals;
        switch (state_) {
            case State::Normal:    return 300s;   // 5 хвилин
            case State::Eco:       return 2700s;  // 45 хвилин
            case State::Survival:  return 28800s; // 8 годин
            case State::Hibernate: return 86400s; // 24 години
            case State::Recovery:  return 1800s;  // 30 хвилин
        }
        return 300s;
    }

private:
    void update_temperature_protection(int8_t temp_c) noexcept {
        // Сувора заборона заряду при температурі нижче заданого порогу
        charge_enabled_ = (temp_c >= config_.temp_charge_min_c);
    }

    void update_state_machine(const Telemetry& t, std::chrono::seconds elapsed) noexcept {
        switch (state_) {
            case State::Normal:
                sensors_enabled_ = true;
                radio_enabled_ = true;
                if (t.voltage_mv <= config_.v_normal_mv) {
                    state_ = State::Eco;
                }
                break;

            case State::Eco:
                sensors_enabled_ = true;
                radio_enabled_ = true;
                if (t.voltage_mv > (config_.v_normal_mv + config_.v_hysteresis_mv)) {
                    state_ = State::Normal;
                } else if (t.voltage_mv <= config_.v_eco_mv) {
                    state_ = State::Survival;
                }
                break;

            case State::Survival:
                sensors_enabled_ = false; // Вимикаємо зовнішні сенсори
                radio_enabled_ = true;    // Дозволяємо лише маяк
                if (t.voltage_mv > (config_.v_eco_mv + config_.v_hysteresis_mv)) {
                    state_ = State::Eco;
                } else if (t.voltage_mv <= config_.v_hibernate_mv) {
                    state_ = State::Hibernate;
                    soak_counter_ = std::chrono::seconds{0};
                }
                break;

            case State::Hibernate:
                sensors_enabled_ = false;
                radio_enabled_ = false; // Повне відключення зв'язку
                // Перевірка початку заряду для переходу в Recovery
                if (t.voltage_mv >= config_.v_hibernate_mv + config_.v_hysteresis_mv && 
                    t.charge_current_ma > 10) {
                    state_ = State::Recovery;
                    soak_counter_ = std::chrono::seconds{0};
                }
                break;

            case State::Recovery:
                sensors_enabled_ = false;
                radio_enabled_ = false;
                if (t.charge_current_ma > 15) {
                    soak_counter_ += elapsed;
                } else {
                    soak_counter_ = std::chrono::seconds{0};
                }

                // Вихід з блекауту лише при повному заряді та стабільному сонці
                if (t.voltage_mv >= config_.v_recovery_mv && 
                    soak_counter_ >= config_.soak_time_required) {
                    state_ = State::Eco;
                    soak_counter_ = std::chrono::seconds{0};
                } else if (t.voltage_mv < config_.v_hibernate_mv) {
                    state_ = State::Hibernate;
                }
                break;
        }
    }

    Config config_;
    State state_{State::Normal};
    std::chrono::seconds soak_counter_{0};
    bool charge_enabled_{false};
    bool sensors_enabled_{true};
    bool radio_enabled_{true};
};

} // namespace embedded::power
