#include "EStopBlock.hpp"

namespace safety {

EStopBlock::EStopBlock(const EStopConfig& config)
    : config_(config), edm_monitor_(config.edm_config) {}

void EStopBlock::update(bool ch1_nc_input,
                        bool ch2_nc_input,
                        bool edm_feedback_input,
                        bool reset_button_input,
                        uint32_t delta_time_ms) {
    // 1. Детекція переднього фронту (rising edge) кнопки Reset
    const bool reset_rising_edge = (reset_button_input && !prev_reset_button_);
    prev_reset_button_ = reset_button_input;

    // 2. Аналіз часової розбіжності між двома каналами E-Stop
    process_discrepancy(ch1_nc_input, ch2_nc_input, delta_time_ms);

    // 3. Оновлення стану монітора зворотного зв'язку реле (EDM)
    edm_monitor_.update(output_active_, edm_feedback_input, delta_time_ms);

    // 4. Перевірка наявності апаратної помилки EDM
    if (edm_monitor_.is_fault() && state_ != SafetyState::EdmFault) {
        state_ = SafetyState::EdmFault;
        fault_ = EStopFault::EdmFailure;
        output_active_ = false;
    }

    // 5. Виконання автомата станів безпеки
    evaluate_state_machine(ch1_nc_input, ch2_nc_input, reset_rising_edge);
}

void EStopBlock::process_discrepancy(bool ch1, bool ch2, uint32_t delta_time_ms) noexcept {
    // Якщо обидва канали увімкнені або обидва вимкнені — розбіжності немає
    if ((ch1 && ch2) || (!ch1 && !ch2)) {
        discrepancy_timer_ms_ = 0;
        discrepancy_active_ = false;
        return;
    }

    // Канали розходяться (один замкнений, інший розімкнений)
    discrepancy_active_ = true;
    discrepancy_timer_ms_ += delta_time_ms;

    if (discrepancy_timer_ms_ >= config_.discrepancy_time_ms) {
        // Перевищено таймаут неузгодженості каналів
        state_ = SafetyState::DiscrepancyFault;
        fault_ = EStopFault::DiscrepancyTimeout;
        output_active_ = false;
    }
}

void EStopBlock::evaluate_state_machine(bool ch1, bool ch2, bool reset_edge) noexcept {
    switch (state_) {
        case SafetyState::Safe: {
            // У безпечному стані обидва канали мають бути підтверджені (true)
            if (!ch1 || !ch2) {
                output_active_ = false;
                if (!ch1 && !ch2) {
                    state_ = SafetyState::EStopActive;
                } else if (discrepancy_timer_ms_ >= config_.discrepancy_time_ms) {
                    state_ = SafetyState::DiscrepancyFault;
                    fault_ = EStopFault::DiscrepancyTimeout;
                } else {
                    // Тимчасовий розкид спрацьовування до вичерпання таймауту
                    state_ = SafetyState::EStopActive;
                }
            }
            break;
        }

        case SafetyState::EStopActive: {
            output_active_ = false;
            // Перевіряємо, чи розбіжність не переросла в помилку
            if (discrepancy_timer_ms_ >= config_.discrepancy_time_ms) {
                state_ = SafetyState::DiscrepancyFault;
                fault_ = EStopFault::DiscrepancyTimeout;
            } else if (ch1 && ch2) {
                // Обидва канали відновлено в норму
                if (config_.require_manual_reset) {
                    state_ = SafetyState::WaitingForReset;
                } else if (edm_monitor_.is_ok()) {
                    state_ = SafetyState::Safe;
                    output_active_ = true;
                }
            }
            break;
        }

        case SafetyState::WaitingForReset: {
            output_active_ = false;

            // Якщо під час очікування скидання знову розімкнули E-Stop
            if (!ch1 || !ch2) {
                state_ = SafetyState::EStopActive;
                break;
            }

            // Перевірка умови ручного скидання за наявності переднього фронту Reset
            if (reset_edge) {
                if (ch1 && ch2 && edm_monitor_.is_ok() && !discrepancy_active_) {
                    state_ = SafetyState::Safe;
                    output_active_ = true;
                    fault_ = EStopFault::None;
                }
            }
            break;
        }

        case SafetyState::DiscrepancyFault: {
            output_active_ = false;

            // Відновлення можливе тільки якщо ОБИДВА канали знову фізично замкнені
            // та отримано підтверджений фронт сигналу Reset
            if (reset_edge && ch1 && ch2 && edm_monitor_.is_ok()) {
                discrepancy_timer_ms_ = 0;
                discrepancy_active_ = false;
                fault_ = EStopFault::None;
                state_ = SafetyState::Safe;
                output_active_ = true;
            }
            break;
        }

        case SafetyState::EdmFault: {
            output_active_ = false;

            // Відновлення після помилки реле: вхідні канали E-Stop у нормі,
            // монітор EDM успішно скинуто, і натиснуто Reset
            if (reset_edge && ch1 && ch2) {
                edm_monitor_.reset();
                if (edm_monitor_.is_ok()) {
                    fault_ = EStopFault::None;
                    state_ = SafetyState::Safe;
                    output_active_ = true;
                }
            }
            break;
        }
    }
}

bool EStopBlock::is_output_active() const noexcept {
    return output_active_;
}

SafetyState EStopBlock::get_state() const noexcept {
    return state_;
}

EStopFault EStopBlock::get_fault() const noexcept {
    return fault_;
}

const EdmMonitor& EStopBlock::get_edm_monitor() const noexcept {
    return edm_monitor_;
}

bool EStopBlock::request_reset() noexcept {
    if (state_ == SafetyState::WaitingForReset ||
        state_ == SafetyState::DiscrepancyFault ||
        state_ == SafetyState::EdmFault) {
        // Симулюємо фронт кнопкою Reset для оновлення автомата
        prev_reset_button_ = false;
        return true;
    }
    return false;
}

const EStopConfig& EStopBlock::get_config() const noexcept {
    return config_;
}

void EStopBlock::set_config(const EStopConfig& config) {
    config_ = config;
    edm_monitor_.set_config(config.edm_config);
}

} // namespace safety
