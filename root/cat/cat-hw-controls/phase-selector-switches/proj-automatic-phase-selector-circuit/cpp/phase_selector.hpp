#ifndef PHASE_SELECTOR_HPP
#define PHASE_SELECTOR_HPP

#include "voltage_sensor.hpp"
#include "phase_fsm.hpp"
#include "contactor_driver.hpp"
#include <array>
#include <span>

namespace hw_controls {

/**
 * @brief Головний контролер селектора фаз, що інтегрує вимірювання, FSM та силове керування
 */
class PhaseSelectorController {
public:
    PhaseSelectorController(const AdcConfig& adc_cfg,
                            const FsmConfig& fsm_cfg,
                            ContactorDriver::OutputCallback hw_callback)
        : sensor_(adc_cfg),
          fsm_(fsm_cfg),
          driver_(std::move(hw_callback), fsm_cfg.break_delay_ms) {}

    /**
     * @brief Основний крок обробки циклу керування (Spin once)
     * @param current_time_ms Поточний системний час у мілісекундах
     * @param phase_buffers Сирі буфери вибірок АЦП для трьох фаз L1, L2, L3
     */
    void process(uint32_t current_time_ms,
                 const std::array<std::span<const uint16_t>, PHASE_COUNT>& phase_buffers) {
        // 1. Дискретизація та розрахунок True RMS по кожному із трьох фазних каналів
        sensor_.process_samples(PhaseId::L1, phase_buffers[0]);
        sensor_.process_samples(PhaseId::L2, phase_buffers[1]);
        sensor_.process_samples(PhaseId::L3, phase_buffers[2]);

        // 2. Оновлення неблокуючого скінченного автомата логіки вибору фаз
        const auto rms_values = sensor_.get_all_rms();
        const PhaseId requested_phase = fsm_.update(rms_values, current_time_ms);

        // 3. Безпечна передача рішення до драйвера контакторів з урахуванням Dead-Time та блокування
        driver_.apply_phase(requested_phase, current_time_ms);
    }

    /**
     * @brief Примусове аварійне вимкнення всіх фаз
     */
    void emergency_stop() {
        driver_.force_disconnect_all();
    }

    /**
     * @brief Отримання інформації про поточну активну фазу на силових контактах
     */
    [[nodiscard]] PhaseId get_active_phase() const {
        return driver_.get_active_phase();
    }

    /**
     * @brief Отримання True RMS напруги заданої фази
     */
    [[nodiscard]] float get_phase_voltage(PhaseId phase) const {
        return sensor_.get_rms(phase);
    }

    /**
     * @brief Перевірка, чи знаходиться напруга фази в допустимому робочому діапазоні
     */
    [[nodiscard]] bool is_phase_valid(PhaseId phase) const {
        return fsm_.is_phase_valid(phase);
    }

    /**
     * @brief Отримання поточного стану FSM
     */
    [[nodiscard]] FsmState get_fsm_state() const {
        return fsm_.get_state();
    }

    /**
     * @brief Доступ до підсистеми сенсорів напруги
     */
    [[nodiscard]] const VoltageSensor& get_sensor() const { return sensor_; }
    [[nodiscard]] VoltageSensor& get_sensor() { return sensor_; }

    /**
     * @brief Доступ до підсистеми скінченного автомата
     */
    [[nodiscard]] const PhaseFSM& get_fsm() const { return fsm_; }
    [[nodiscard]] PhaseFSM& get_fsm() { return fsm_; }

    /**
     * @brief Доступ до драйвера силових контакторів
     */
    [[nodiscard]] const ContactorDriver& get_driver() const { return driver_; }
    [[nodiscard]] ContactorDriver& get_driver() { return driver_; }

private:
    VoltageSensor sensor_;
    PhaseFSM fsm_;
    ContactorDriver driver_;
};

} // namespace hw_controls

#endif // PHASE_SELECTOR_HPP
