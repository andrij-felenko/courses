#ifndef SAFETY_CONTROLLER_HPP
#define SAFETY_CONTROLLER_HPP

#include "safety_types.hpp"
#include "ossd_channel.hpp"
#include <cstdint>

namespace safety {

// Менеджер режимів Muting (приглушення) та Blanking (маскування)
class MutingBlankingManager {
public:
    explicit MutingBlankingManager(uint32_t muting_timeout_ms = 5000, uint32_t blanking_mask = 0);

    // Оновлення стану датчиків мутингу M1 і M2
    void update(bool sensor_m1, bool sensor_m2, uint64_t current_time_ms);

    // Перевірка чи активний режим Muting
    [[nodiscard]] bool is_muting_active() const noexcept;

    // Перевірка чи активовано режим Blanking
    [[nodiscard]] bool is_blanking_active() const noexcept;

    // Отримання поточного коду помилки мутингу
    [[nodiscard]] FaultCode get_fault() const noexcept;

    // Скидання помилок мутингу
    void reset();

    // Встановлення маски маскування променів
    void set_blanking_mask(uint32_t mask) noexcept;

private:
    uint32_t timeout_ms_{5000};
    uint32_t blanking_mask_{0};
    
    bool muting_active_{false};
    uint64_t muting_start_time_ms_{0};
    
    FaultCode fault_{FaultCode::None};
};

// Головний контролер безпеки об'єктно-орієнтованого модуля
class SafetyController {
public:
    explicit SafetyController(const SafetyConfig& config = SafetyConfig{});

    // Оновлення стану контролера в кожному циклі ПЛК / мікроконтролера
    void process_cycle(bool ossd_a, bool ossd_b, bool muting_s1, bool muting_s2, uint64_t current_time_ms);

    // Подання команди Reset (ручний перезапуск / скидання помилок)
    bool request_reset();

    // Отримання поточного стану системи безпеки
    [[nodiscard]] SafetyState get_state() const noexcept;

    // Отримання активного коду помилки
    [[nodiscard]] FaultCode get_fault_code() const noexcept;

    // Стан вихідних реле/контакторів безпеки (true = замкнено / безпечно)
    [[nodiscard]] bool get_safety_outputs() const noexcept;

    // Конфігурування маски Blanking під час роботи
    void set_blanking_mask(uint32_t mask);

private:
    SafetyConfig config_;
    SafetyState state_{SafetyState::Tripped};
    FaultCode active_fault_{FaultCode::None};

    OssdChannel ossd_;
    MutingBlankingManager muting_mgr_;

    bool outputs_enabled_{false};
    bool reset_pending_{false};

    void update_state_machine();
};

} // namespace safety

#endif // SAFETY_CONTROLLER_HPP
