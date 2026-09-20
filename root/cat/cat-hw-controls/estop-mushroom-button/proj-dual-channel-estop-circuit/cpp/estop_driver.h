#ifndef ESTOP_DRIVER_H
#define ESTOP_DRIVER_H

#include "estop_types.h"
#include <iostream>
#include <mutex>
#include <string>
#include <string_view>

// Клас логера подій ПЛК (PlcSystemLogger)
class PlcSystemLogger {
public:
    static PlcSystemLogger& getInstance();

    void log(LogLevel level, std::string_view message);

private:
    PlcSystemLogger() = default;
    std::mutex log_mutex_;
};

// Клас драйвера двоканальної кнопки аварійного стопу (EStopDriver)
class EStopDriver {
public:
    explicit EStopDriver(EStopConfig config = {});

    // Оновлення стану драйвера при отриманні сигналів з двох NC-каналів
    void update(bool channel1_raw, bool channel2_raw, uint32_t current_time_ms);

    // Отримання поточного стану контуру E-Stop
    [[nodiscard]] EStopState getState() const noexcept { return current_state_; }

    // Перевірка, чи перебуває система в стані аварійного вимкнення
    [[nodiscard]] bool isTripped() const noexcept { return current_state_ != EStopState::Normal; }

    // Ручне скидання тривоги (рестарт контуру безпеки після усунення причини)
    bool reset(uint32_t current_time_ms);

private:
    EStopConfig config_;
    EStopState current_state_{EStopState::Normal};

    bool ch1_filtered_{true}; // Нормальний стан NC — замкнено (true)
    bool ch2_filtered_{true};

    uint32_t ch1_last_change_ms_{0};
    uint32_t ch2_last_change_ms_{0};

    uint32_t discrepancy_start_ms_{0};
    bool discrepancy_timer_active_{false};
};

#endif // ESTOP_DRIVER_H
