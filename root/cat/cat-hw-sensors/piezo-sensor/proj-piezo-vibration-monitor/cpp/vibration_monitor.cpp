#include "vibration_monitor.hpp"

VibrationMonitor::VibrationMonitor(const PeakFilterConfig& filter_cfg, const RelayProtectionConfig& relay_cfg)
    : filter_cfg_(filter_cfg),
      relay_cfg_(relay_cfg),
      peak_envelope_(0.0f),
      state_(RelayState::NORMAL),
      state_timer_ms_(0) {
}

void VibrationMonitor::update(uint16_t raw_adc_value, uint32_t current_time_ms) {
    processPeakFilter(raw_adc_value);
    updateFSM(current_time_ms);
}

void VibrationMonitor::processPeakFilter(uint16_t raw_adc_value) {
    uint16_t sample_signal = 0;
    if (raw_adc_value > filter_cfg_.noise_floor) {
        sample_signal = raw_adc_value - filter_cfg_.noise_floor;
    }

    float current_val = static_cast<float>(sample_signal);

    if (current_val > peak_envelope_) {
        // Миттєва фіксація нового амплітудного піку
        peak_envelope_ = current_val;
    } else {
        // Експоненціальне загасання пікової огинаючої між сплесками
        peak_envelope_ *= filter_cfg_.decay_factor;
        if (peak_envelope_ < 0.01f) {
            peak_envelope_ = 0.0f;
        }
    }
}

void VibrationMonitor::updateFSM(uint32_t current_time_ms) {
    switch (state_) {
        case RelayState::NORMAL:
            if (peak_envelope_ >= static_cast<float>(relay_cfg_.alarm_threshold)) {
                if (relay_cfg_.trip_delay_ms > 0) {
                    state_ = RelayState::TRIP_DELAY;
                    state_timer_ms_ = current_time_ms;
                } else {
                    state_ = RelayState::ALARM;
                }
            }
            break;

        case RelayState::TRIP_DELAY:
            if (peak_envelope_ < static_cast<float>(relay_cfg_.alarm_threshold)) {
                // Вібраційний сплеск виявився короткочасним (попередня тривога скасовується)
                state_ = RelayState::NORMAL;
            } else if ((current_time_ms - state_timer_ms_) >= relay_cfg_.trip_delay_ms) {
                // Перевищення порогу утримувалося достатньо довго — перехід в аварію
                state_ = RelayState::ALARM;
            }
            break;

        case RelayState::ALARM:
            if (peak_envelope_ < static_cast<float>(relay_cfg_.recovery_threshold)) {
                if (relay_cfg_.recovery_delay_ms > 0) {
                    state_ = RelayState::RECOVERY_DELAY;
                    state_timer_ms_ = current_time_ms;
                } else {
                    state_ = RelayState::NORMAL;
                }
            }
            break;

        case RelayState::RECOVERY_DELAY:
            if (peak_envelope_ >= static_cast<float>(relay_cfg_.recovery_threshold)) {
                // Рівень вібрації знову зріс під час паузи відновлення
                state_ = RelayState::ALARM;
            } else if ((current_time_ms - state_timer_ms_) >= relay_cfg_.recovery_delay_ms) {
                // Вібрація залишалася низькою впродовж всієї затримки відновлення
                state_ = RelayState::NORMAL;
            }
            break;
    }
}

float VibrationMonitor::getPeakEnvelope() const {
    return peak_envelope_;
}

RelayState VibrationMonitor::getRelayState() const {
    return state_;
}

bool VibrationMonitor::isRelayActive() const {
    return state_ == RelayState::ALARM;
}

void VibrationMonitor::reset(uint32_t current_time_ms) {
    peak_envelope_ = 0.0f;
    state_ = RelayState::NORMAL;
    state_timer_ms_ = current_time_ms;
}
