#ifndef OSSD_CHANNEL_HPP
#define OSSD_CHANNEL_HPP

#include "safety_types.hpp"
#include <chrono>

namespace safety {

// Клас обробки та валідації двоканальних OSSD-сигналів
class OssdChannel {
public:
    explicit OssdChannel(uint32_t discrepancy_time_ms = 200);

    // Оновлення стану каналів OSSD на поточному циклі (timestamp у мілісекундах)
    void update(bool ch_a_raw, bool ch_b_raw, uint64_t current_time_ms);

    // Перевірка чи перебувають OSSD-канали у безпечному активному стані (HIGH / HIGH)
    [[nodiscard]] bool is_safe() const noexcept;

    // Отримання поточного коду помилки каналів
    [[nodiscard]] FaultCode get_fault() const noexcept;

    // Скидання помилки каналу (повертає true, якщо сигнали у нормі)
    bool reset_fault();

    // Встановлення часу допустимого розходження між каналами
    void set_discrepancy_time(uint32_t time_ms) noexcept;

private:
    bool channel_a_{false};
    bool channel_b_{false};
    
    uint32_t discrepancy_limit_ms_{200};
    uint64_t discrepancy_start_time_ms_{0};
    bool in_discrepancy_{false};

    FaultCode fault_{FaultCode::None};
};

} // namespace safety

#endif // OSSD_CHANNEL_HPP
