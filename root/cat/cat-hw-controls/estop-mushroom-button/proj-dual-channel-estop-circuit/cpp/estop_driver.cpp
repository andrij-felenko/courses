#include "estop_driver.h"

PlcSystemLogger& PlcSystemLogger::getInstance() {
    static PlcSystemLogger instance;
    return instance;
}

void PlcSystemLogger::log(LogLevel level, std::string_view message) {
    std::lock_guard<std::mutex> lock(log_mutex_);
    const char* level_str = "[INFO]";
    if (level == LogLevel::Warning) {
        level_str = "[WARN]";
    } else if (level == LogLevel::Critical) {
        level_str = "[CRIT]";
    }
    std::cout << "[ПЛК-ЖУРНАЛ] " << level_str << " " << message << std::endl;
}

EStopDriver::EStopDriver(EStopConfig config)
    : config_(config) {}

void EStopDriver::update(bool channel1_raw, bool channel2_raw, uint32_t current_time_ms) {
    // 1. Програмна фільтрація брязкоту контактів (Debounce) для каналу 1
    if (channel1_raw != ch1_filtered_) {
        if (ch1_last_change_ms_ == 0) {
            ch1_last_change_ms_ = current_time_ms;
        } else if (current_time_ms - ch1_last_change_ms_ >= config_.debounce_ms) {
            ch1_filtered_ = channel1_raw;
            ch1_last_change_ms_ = 0;
        }
    } else {
        ch1_last_change_ms_ = 0;
    }

    // 2. Програмна фільтрація брязкоту контактів (Debounce) для каналу 2
    if (channel2_raw != ch2_filtered_) {
        if (ch2_last_change_ms_ == 0) {
            ch2_last_change_ms_ = current_time_ms;
        } else if (current_time_ms - ch2_last_change_ms_ >= config_.debounce_ms) {
            ch2_filtered_ = channel2_raw;
            ch2_last_change_ms_ = 0;
        }
    } else {
        ch2_last_change_ms_ = 0;
    }

    // Якщо вже зафіксовано апаратний розсинхрон, заблокувати до скидання
    if (current_state_ == EStopState::DiscrepancyError) {
        return;
    }

    // 3. Перевірка синхронності спрацьовування двох NC-каналів (NC = true у нормі, false при натиску)
    bool ch1_active = !ch1_filtered_; // true = розімкнено (натиснуто)
    bool ch2_active = !ch2_filtered_;

    if (ch1_active == ch2_active) {
        // Обидва канали в одинаковому стані
        discrepancy_timer_active_ = false;

        if (ch1_active && current_state_ != EStopState::Tripped) {
            current_state_ = EStopState::Tripped;
            PlcSystemLogger::getInstance().log(
                LogLevel::Critical,
                "Аварійний стоп спрацював! Обидва NC-контакти розімкнено."
            );
        }
    } else {
        // Канали у розсинхронізованому стані (один розімкнено, інший замкнено)
        if (!discrepancy_timer_active_) {
            discrepancy_timer_active_ = true;
            discrepancy_start_ms_ = current_time_ms;
        } else if (current_time_ms - discrepancy_start_ms_ > config_.max_discrepancy_ms) {
            current_state_ = EStopState::DiscrepancyError;
            PlcSystemLogger::getInstance().log(
                LogLevel::Critical,
                "Помилка розсинхронізації каналів E-Stop (Discrepancy Error)! Порушено вимоги ISO 13849."
            );
        }
    }
}

bool EStopDriver::reset(uint32_t current_time_ms) {
    // Скидання можливе тільки якщо обидва фізичні контакти відновлено у закритий NC-стан (true)
    if (ch1_filtered_ && ch2_filtered_) {
        current_state_ = EStopState::Normal;
        discrepancy_timer_active_ = false;
        PlcSystemLogger::getInstance().log(
            LogLevel::Info,
            "Контур безпеки успішно відновлено та активовано."
        );
        return true;
    }

    PlcSystemLogger::getInstance().log(
        LogLevel::Warning,
        "Неможливо скинути аварію: кнопки E-Stop не повернуто у вихідний стан."
    );
    return false;
}
