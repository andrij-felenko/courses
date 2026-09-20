#ifndef PHASE_FSM_HPP
#define PHASE_FSM_HPP

#include "voltage_sensor.hpp"
#include <cstdint>
#include <array>

namespace hw_controls {

/**
 * @brief Стани неблокуючого скінченного автомата перемикання фаз
 */
enum class FsmState : uint8_t {
    Init = 0,         ///< Початкова ініціалізація, відключення всіх контактів
    Monitoring,       ///< Безперервний моніторинг активної фази та вибір оптимальної
    BreakPause,       ///< Захисна пауза розмикання для гасіння дуги (Dead-Time)
    Connecting,       ///< Витримана затримка для перевірки стабільності нової фази
    Fault             ///< Аварія: відсутня жодна придатна фаза в мережі
};

/**
 * @brief Налаштування порогів напруги, гістерезису та часових затримок
 */
struct FsmConfig {
    float v_min = 195.0f;              ///< Нижній поріг напруги (В)
    float v_max = 253.0f;              ///< Верхній поріг напруги (В)
    float v_hysteresis = 5.0f;         ///< Гістерезис спрацьовування та відпускання (В)
    uint32_t break_delay_ms = 30;      ///< Пауза бездаркового розмикання контакторів (мс)
    uint32_t connect_delay_ms = 3000;  ///< Затримка підтвердження стабільності фази перед ввімкненням (мс)
    PhaseId priority_phase = PhaseId::L1; ///< Пріоритетна фаза за замовчуванням
};

/**
 * @brief Скінченний автомат логіки вибору та перемикання фаз
 */
class PhaseFSM {
public:
    explicit PhaseFSM(const FsmConfig& config = {})
        : config_(config) {
        phase_valid_.fill(false);
    }

    /**
     * @brief Оновлення FSM та отримання рішення про необхідну фазу
     * @param rms_voltages Масив поточних RMS напруг для L1, L2, L3
     * @param current_time_ms Поточний системний час у мілісекундах
     * @return Фаза, яка має бути підключена до навантаження
     */
    PhaseId update(const std::array<float, PHASE_COUNT>& rms_voltages, uint32_t current_time_ms) {
        // Step 1: Оцінка якості кожної фази з урахуванням гістерезису
        update_hysteresis(rms_voltages);

        // Step 2: Визначення найкращої доступної фази згідно із пріоритетом
        const PhaseId best_phase = select_best_phase();

        // Step 3: Виконання кроку автоматного стану
        switch (state_) {
        case FsmState::Init:
            active_phase_ = PhaseId::None;
            target_phase_ = PhaseId::None;
            state_timer_ms_ = current_time_ms;
            state_ = FsmState::Monitoring;
            break;

        case FsmState::Monitoring:
            if (active_phase_ == PhaseId::None) {
                if (best_phase != PhaseId::None) {
                    target_phase_ = best_phase;
                    state_timer_ms_ = current_time_ms;
                    state_ = FsmState::Connecting;
                } else {
                    state_ = FsmState::Fault;
                }
            } else {
                // Перевіряємо придатність поточної активної фази
                const auto active_idx = static_cast<std::size_t>(active_phase_);
                if (!phase_valid_[active_idx]) {
                    // Аварійне відхилення активної фази — негайне розмикання
                    active_phase_ = PhaseId::None;
                    target_phase_ = best_phase;
                    state_timer_ms_ = current_time_ms;
                    state_ = FsmState::BreakPause;
                } else if (best_phase != active_phase_ && best_phase == config_.priority_phase) {
                    // З'явилася пріоритетна фаза L1: плановий перехід
                    active_phase_ = PhaseId::None;
                    target_phase_ = best_phase;
                    state_timer_ms_ = current_time_ms;
                    state_ = FsmState::BreakPause;
                }
            }
            break;

        case FsmState::BreakPause:
            // Впевнюємося, що навантаження знеструмлене на час паузи
            active_phase_ = PhaseId::None;
            if ((current_time_ms - state_timer_ms_) >= config_.break_delay_ms) {
                if (target_phase_ != PhaseId::None && is_phase_valid(target_phase_)) {
                    state_timer_ms_ = current_time_ms;
                    state_ = FsmState::Connecting;
                } else {
                    target_phase_ = best_phase;
                    if (target_phase_ == PhaseId::None) {
                        state_ = FsmState::Fault;
                    }
                }
            }
            break;

        case FsmState::Connecting:
            if (target_phase_ == PhaseId::None || !is_phase_valid(target_phase_)) {
                // Напруга обраної фази зіпсувалася під час витримки затримки
                target_phase_ = best_phase;
                state_timer_ms_ = current_time_ms;
                state_ = FsmState::BreakPause;
                break;
            }

            if ((current_time_ms - state_timer_ms_) >= config_.connect_delay_ms) {
                active_phase_ = target_phase_;
                state_ = FsmState::Monitoring;
            }
            break;

        case FsmState::Fault:
            active_phase_ = PhaseId::None;
            if (best_phase != PhaseId::None) {
                target_phase_ = best_phase;
                state_timer_ms_ = current_time_ms;
                state_ = FsmState::Connecting;
            }
            break;
        }

        return active_phase_;
    }

    [[nodiscard]] FsmState get_state() const { return state_; }
    [[nodiscard]] PhaseId get_active_phase() const { return active_phase_; }
    [[nodiscard]] PhaseId get_target_phase() const { return target_phase_; }

    [[nodiscard]] bool is_phase_valid(PhaseId phase) const {
        if (phase == PhaseId::None || static_cast<std::size_t>(phase) >= PHASE_COUNT) {
            return false;
        }
        return phase_valid_[static_cast<std::size_t>(phase)];
    }

    void set_config(const FsmConfig& config) { config_ = config; }
    [[nodiscard]] FsmConfig get_config() const { return config_; }

private:
    void update_hysteresis(const std::array<float, PHASE_COUNT>& rms_voltages) {
        for (std::size_t i = 0; i < PHASE_COUNT; ++i) {
            const float v = rms_voltages[i];
            const bool currently_valid = phase_valid_[i];

            if (currently_valid) {
                // Якщо фаза була в нормі, вона стає недійсною лише за межами з гістерезисом
                if (v < (config_.v_min - config_.v_hysteresis) || v > (config_.v_max + config_.v_hysteresis)) {
                    phase_valid_[i] = false;
                }
            } else {
                // Відновлення фази відбувається лише при точному входженні у допустимий діапазон
                if (v >= config_.v_min && v <= config_.v_max) {
                    phase_valid_[i] = true;
                }
            }
        }
    }

    [[nodiscard]] PhaseId select_best_phase() const {
        // 1. Перевіряємо пріоритетну фазу (за замовчуванням L1)
        if (config_.priority_phase != PhaseId::None && is_phase_valid(config_.priority_phase)) {
            return config_.priority_phase;
        }

        // 2. Інакше шукаємо першу робочу резервну фазу (L1 -> L2 -> L3)
        const std::array<PhaseId, PHASE_COUNT> search_order{PhaseId::L1, PhaseId::L2, PhaseId::L3};
        for (const auto phase : search_order) {
            if (is_phase_valid(phase)) {
                return phase;
            }
        }

        return PhaseId::None;
    }

    FsmConfig config_;
    FsmState state_{FsmState::Init};
    PhaseId active_phase_{PhaseId::None};
    PhaseId target_phase_{PhaseId::None};
    uint32_t state_timer_ms_{0};
    std::array<bool, PHASE_COUNT> phase_valid_{};
};

} // namespace hw_controls

#endif // PHASE_FSM_HPP
