#ifndef CONTACTOR_DRIVER_HPP
#define CONTACTOR_DRIVER_HPP

#include "voltage_sensor.hpp"
#include <cstdint>
#include <functional>
#include <array>

namespace hw_controls {

/**
 * @brief Драйвер силових контакторів або напівпровідникових ключів з програмним та апаратним взаємним блокуванням
 */
class ContactorDriver {
public:
    using OutputCallback = std::function<void(PhaseId phase, bool enable)>;

    explicit ContactorDriver(OutputCallback hw_callback = nullptr, uint32_t dead_time_ms = 30)
        : hw_callback_(std::move(hw_callback)), dead_time_ms_(dead_time_ms) {
        hardware_states_.fill(false);
    }

    /**
     * @brief Запит на увімкнення контактора конкретної фази із гарантією взаємного блокування
     * @param target_phase Фаза для підключення навантаження (або PhaseId::None для відключення)
     * @param current_time_ms Поточний системний час (мс)
     * @return true якщо підключення успішно виконано або збережено стан, false якщо триває Dead-Time
     */
    bool apply_phase(PhaseId target_phase, uint32_t current_time_ms) {
        // Якщо запитано відключення всіх фаз
        if (target_phase == PhaseId::None || static_cast<std::size_t>(target_phase) >= PHASE_COUNT) {
            force_disconnect_all();
            return true;
        }

        // Якщо target_phase вже увімкнена і жодна інша не горить — нічого не робимо
        if (current_active_phase_ == target_phase && hardware_states_[static_cast<std::size_t>(target_phase)]) {
            return true;
        }

        // Якщо поточна фаза відрізняється, спочатку вимикаємо все і фіксуємо час розмикання
        if (current_active_phase_ != PhaseId::None) {
            force_disconnect_all();
            last_switch_time_ms_ = current_time_ms;
            return false;
        }

        // Перевірка витримки безпечного інтервалу Dead-Time
        if ((current_time_ms - last_switch_time_ms_) < dead_time_ms_) {
            return false; // Захисний інтервал ще не вичерпано
        }

        // КРИТИЧНЕ ПРОГРАМНЕ БЛОКУВАННЯ: Гарантовано вимикаємо всі інші канали перед увімкненням нового
        for (std::size_t i = 0; i < PHASE_COUNT; ++i) {
            if (i != static_cast<std::size_t>(target_phase)) {
                set_contactor_hardware(static_cast<PhaseId>(i), false);
            }
        }

        // Подаємо сигнал на увімкнення цільової фази
        set_contactor_hardware(target_phase, true);
        current_active_phase_ = target_phase;
        return true;
    }

    /**
     * @brief Аварійне негайне знеструмлення всіх силових каналів
     */
    void force_disconnect_all() {
        for (std::size_t i = 0; i < PHASE_COUNT; ++i) {
            set_contactor_hardware(static_cast<PhaseId>(i), false);
        }
        current_active_phase_ = PhaseId::None;
    }

    /**
     * @brief Отримання поточно увімкненої фази на силових виходах
     */
    [[nodiscard]] PhaseId get_active_phase() const {
        return current_active_phase_;
    }

    /**
     * @brief Перевірка стану фіксованого контактора
     */
    [[nodiscard]] bool is_contactor_closed(PhaseId phase) const {
        if (phase == PhaseId::None || static_cast<std::size_t>(phase) >= PHASE_COUNT) {
            return false;
        }
        return hardware_states_[static_cast<std::size_t>(phase)];
    }

    /**
     * @brief Встановлення колбеку апаратного виходу GPIO
     */
    void set_output_callback(OutputCallback hw_callback) {
        hw_callback_ = std::move(hw_callback);
    }

    /**
     * @brief Налаштування затримки Dead-Time
     */
    void set_dead_time_ms(uint32_t dead_time_ms) {
        dead_time_ms_ = dead_time_ms;
    }

private:
    void set_contactor_hardware(PhaseId phase, bool enable) {
        const auto idx = static_cast<std::size_t>(phase);
        hardware_states_[idx] = enable;
        if (hw_callback_) {
            hw_callback_(phase, enable);
        }
    }

    OutputCallback hw_callback_{nullptr};
    uint32_t dead_time_ms_{30};
    uint32_t last_switch_time_ms_{0};
    PhaseId current_active_phase_{PhaseId::None};
    std::array<bool, PHASE_COUNT> hardware_states_{};
};

} // namespace hw_controls

#endif // CONTACTOR_DRIVER_HPP
