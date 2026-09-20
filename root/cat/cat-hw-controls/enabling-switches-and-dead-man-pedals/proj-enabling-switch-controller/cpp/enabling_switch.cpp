#include "enabling_switch.hpp"

// Реалізація ChannelReader
void ChannelReader::update(bool raw_ch_a, bool raw_ch_b, uint32_t current_time_ms, const DriverConfig& config) {
    // Цифровий антибрязкіт для каналу A
    if (raw_ch_a != raw_ch_a_) {
        raw_ch_a_ = raw_ch_a;
        last_change_a_ms_ = current_time_ms;
    } else if ((current_time_ms - last_change_a_ms_) >= config.debounce_ms) {
        filtered_ch_a_ = raw_ch_a_;
    }

    // Цифровий антибрязкіт для каналу B
    if (raw_ch_b != raw_ch_b_) {
        raw_ch_b_ = raw_ch_b;
        last_change_b_ms_ = current_time_ms;
    } else if ((current_time_ms - last_change_b_ms_) >= config.debounce_ms) {
        filtered_ch_b_ = raw_ch_b_;
    }

    // Часова діагностика розсинхронізації паралельних контактів
    if (filtered_ch_a_ != filtered_ch_b_) {
        if (!discrepancy_active_) {
            discrepancy_active_ = true;
            discrepancy_start_ms_ = current_time_ms;
        } else if ((current_time_ms - discrepancy_start_ms_) > config.discrepancy_ms) {
            discrepancy_fault_ = true; // Фіксація апаратної несправності ліній
        }
    } else {
        discrepancy_active_ = false;
    }
}

// Реалізація VigilanceTimer
void VigilanceTimer::update(bool is_enabled, uint32_t current_time_ms, const DriverConfig& config) {
    if (!is_enabled) {
        reset();
        return;
    }

    if (!timer_active_) {
        timer_active_ = true;
        enabled_start_ms_ = current_time_ms;
        status_ = VigilanceStatus::Normal;
        return;
    }

    uint32_t elapsed_ms = current_time_ms - enabled_start_ms_;
    uint32_t warn_threshold_ms = config.hold_max_ms;
    uint32_t expire_threshold_ms = config.hold_max_ms + config.warn_ms + config.react_ms;

    if (elapsed_ms >= expire_threshold_ms) {
        status_ = VigilanceStatus::Expired;
    } else if (elapsed_ms >= warn_threshold_ms) {
        status_ = VigilanceStatus::Warning;
    } else {
        status_ = VigilanceStatus::Normal;
    }
}

void VigilanceTimer::reset() {
    status_ = VigilanceStatus::Normal;
    timer_active_ = false;
    enabled_start_ms_ = 0;
}

// Реалізація EnablingSwitchController
EnablingSwitchController::EnablingSwitchController(const DriverConfig& config)
    : config_(config) {}

void EnablingSwitchController::update(bool raw_pin_a, bool raw_pin_b, uint32_t current_time_ms) {
    // 1. Первинна обробка вхідних каналів
    channel_reader_.update(raw_pin_a, raw_pin_b, current_time_ms, config_);

    // 2. Перевірка наявності некритичної або критичної несправності
    if (channel_reader_.has_discrepancy_fault()) {
        current_state_ = EnablingState::Fault;
        require_full_release_ = true;
        vigilance_timer_.reset();
        vigilance_status_ = VigilanceStatus::Normal;
        return;
    }

    bool ch_a = channel_reader_.get_filtered_a();
    bool ch_b = channel_reader_.get_filtered_b();

    // 3. Якщо увімкнено вимогу перевідпускання — чекаємо повного розмикання обидвох контактів
    if (require_full_release_) {
        if (!ch_a && !ch_b) {
            require_full_release_ = false;
            channel_reader_.clear_fault();
            current_state_ = EnablingState::Released;
        } else {
            return; // Заблоковано до повного відпускання
        }
    }

    // 4. Визначення стану за фізичним положенням двоканальних контактів:
    if (!ch_a && !ch_b) {
        current_state_ = EnablingState::Released;
    } else if (ch_a && ch_b) {
        // У робочому стані перевіряємо таймер vigilance control
        vigilance_timer_.update(true, current_time_ms, config_);
        vigilance_status_ = vigilance_timer_.get_status();

        if (vigilance_status_ == VigilanceStatus::Expired) {
            current_state_ = EnablingState::Released; // Тайм-аут пильності вимикає дозвіл
            require_full_release_ = true;             // Вимагає перевідпускання важеля
        } else {
            current_state_ = EnablingState::Enabled;
        }
    }

    if (!is_enabled()) {
        vigilance_timer_.update(false, current_time_ms, config_);
    }
}
