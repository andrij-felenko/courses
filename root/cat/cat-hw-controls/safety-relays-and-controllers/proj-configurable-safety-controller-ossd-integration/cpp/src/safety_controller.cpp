#include "safety_controller.hpp"
#include "ossd_channel.hpp"

namespace safety {

// Реалізація OssdChannel
OssdChannel::OssdChannel(uint32_t discrepancy_time_ms)
    : discrepancy_limit_ms_(discrepancy_time_ms) {}

void OssdChannel::update(bool ch_a_raw, bool ch_b_raw, uint64_t current_time_ms) {
    channel_a_ = ch_a_raw;
    channel_b_ = ch_b_raw;

    // Перевірка на однаковий стан обох каналів
    if (channel_a_ == channel_b_) {
        in_discrepancy_ = false;
        discrepancy_start_time_ms_ = 0;
        // Якщо помилка була DiscrepancyFault, вона залишається до скидання reset_fault()
    } else {
        // Канали розходяться
        if (!in_discrepancy_) {
            in_discrepancy_ = true;
            discrepancy_start_time_ms_ = current_time_ms;
        } else {
            // Перевірка виходу за допустимий часовий ліміт розходження
            if (current_time_ms - discrepancy_start_time_ms_ > discrepancy_limit_ms_) {
                fault_ = FaultCode::DiscrepancyFault;
            }
        }
    }
}

bool OssdChannel::is_safe() const noexcept {
    return (fault_ == FaultCode::None) && channel_a_ && channel_b_;
}

FaultCode OssdChannel::get_fault() const noexcept {
    return fault_;
}

bool OssdChannel::reset_fault() {
    // Скидання помилки можливе тільки якщо обидва канали перебувають у високому стані
    if (channel_a_ && channel_b_) {
        fault_ = FaultCode::None;
        in_discrepancy_ = false;
        return true;
    }
    return false;
}

void OssdChannel::set_discrepancy_time(uint32_t time_ms) noexcept {
    discrepancy_limit_ms_ = time_ms;
}


// Реалізація MutingBlankingManager
MutingBlankingManager::MutingBlankingManager(uint32_t muting_timeout_ms, uint32_t blanking_mask)
    : timeout_ms_(muting_timeout_ms), blanking_mask_(blanking_mask) {}

void MutingBlankingManager::update(bool sensor_m1, bool sensor_m2, uint64_t current_time_ms) {
    // Логіка переходу в Muting: датчики M1 та M2 мають активуватися послідовно/одночасно
    if (sensor_m1 && sensor_m2) {
        if (!muting_active_) {
            muting_active_ = true;
            muting_start_time_ms_ = current_time_ms;
        } else {
            // Перевірка на перевищення таймауту Muting
            if (current_time_ms - muting_start_time_ms_ > timeout_ms_) {
                fault_ = FaultCode::MutingTimeout;
                muting_active_ = false;
            }
        }
    } else {
        // Якщо хоча б один датчик вимкнувся — вихід з режиму Muting
        muting_active_ = false;
        muting_start_time_ms_ = 0;
    }
}

bool MutingBlankingManager::is_muting_active() const noexcept {
    return muting_active_ && (fault_ == FaultCode::None);
}

bool MutingBlankingManager::is_blanking_active() const noexcept {
    return blanking_mask_ != 0;
}

FaultCode MutingBlankingManager::get_fault() const noexcept {
    return fault_;
}

void MutingBlankingManager::reset() {
    fault_ = FaultCode::None;
    muting_active_ = false;
    muting_start_time_ms_ = 0;
}

void MutingBlankingManager::set_blanking_mask(uint32_t mask) noexcept {
    blanking_mask_ = mask;
}


// Реалізація SafetyController
SafetyController::SafetyController(const SafetyConfig& config)
    : config_(config),
      ossd_(config.discrepancy_time_ms),
      muting_mgr_(config.muting_timeout_ms, config.blanking_mask) {}

void SafetyController::process_cycle(bool ossd_a, bool ossd_b, bool muting_s1, bool muting_s2, uint64_t current_time_ms) {
    // 1. Оновлення стану каналів OSSD
    ossd_.update(ossd_a, ossd_b, current_time_ms);

    // 2. Оновлення стану датчиків Muting
    muting_mgr_.update(muting_s1, muting_s2, current_time_ms);

    // 3. Збір та фіксація активних помилок
    if (ossd_.get_fault() != FaultCode::None) {
        active_fault_ = ossd_.get_fault();
    } else if (muting_mgr_.get_fault() != FaultCode::None) {
        active_fault_ = muting_mgr_.get_fault();
    }

    // 4. Оновлення автомата станів
    update_state_machine();
}

void SafetyController::update_state_machine() {
    // Якщо зафіксовано апаратну помилку — перехід у стабільний стан Fault
    if (active_fault_ != FaultCode::None) {
        state_ = SafetyState::Fault;
        outputs_enabled_ = false;
        return;
    }

    bool ossd_ok = ossd_.is_safe();
    bool muting_ok = muting_mgr_.is_muting_active();
    bool blanking_ok = muting_mgr_.is_blanking_active();

    switch (state_) {
        case SafetyState::Fault:
            // Перехід з Fault у Tripped можливий лише при успішному виконанні request_reset()
            outputs_enabled_ = false;
            break;

        case SafetyState::Tripped:
            outputs_enabled_ = false;
            if (ossd_ok || muting_ok) {
                if (config_.reset_mode == ResetMode::Auto) {
                    state_ = muting_ok ? SafetyState::Muting : SafetyState::Safe;
                    outputs_enabled_ = true;
                } else if (reset_pending_) {
                    reset_pending_ = false;
                    state_ = muting_ok ? SafetyState::Muting : SafetyState::Safe;
                    outputs_enabled_ = true;
                }
            }
            break;

        case SafetyState::Safe:
        case SafetyState::Muting:
        case SafetyState::BlankingActive:
            if (muting_ok) {
                state_ = SafetyState::Muting;
                outputs_enabled_ = true;
            } else if (ossd_ok) {
                state_ = blanking_ok ? SafetyState::BlankingActive : SafetyState::Safe;
                outputs_enabled_ = true;
            } else {
                // OSSD перервано без активного Muting -> Аварійне відключення
                state_ = SafetyState::Tripped;
                outputs_enabled_ = false;
            }
            break;
    }
}

bool SafetyController::request_reset() {
    reset_pending_ = true;

    if (state_ == SafetyState::Fault) {
        // Пробуємо скинути помилки в компонентах
        bool ossd_reset = ossd_.reset_fault();
        muting_mgr_.reset();

        if (ossd_reset) {
            active_fault_ = FaultCode::None;
            state_ = SafetyState::Tripped;
            return true;
        }
        return false;
    }

    return true;
}

SafetyState SafetyController::get_state() const noexcept {
    return state_;
}

FaultCode SafetyController::get_fault_code() const noexcept {
    return active_fault_;
}

bool SafetyController::get_safety_outputs() const noexcept {
    return outputs_enabled_;
}

void SafetyController::set_blanking_mask(uint32_t mask) {
    config_.blanking_mask = mask;
    muting_mgr_.set_blanking_mask(mask);
}

} // namespace safety
