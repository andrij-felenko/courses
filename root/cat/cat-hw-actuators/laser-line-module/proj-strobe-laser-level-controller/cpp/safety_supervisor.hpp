#ifndef SAFETY_SUPERVISOR_HPP_
#define SAFETY_SUPERVISOR_HPP_

#include "laser_output.hpp"
#include "thermal_guard.hpp"
#include <cstdint>

namespace laser {

/**
 * @brief Причини спрацювання системи безпеки лазерної платформи.
 */
enum class SafetyFault : uint8_t {
    None = 0,               // Система в нормі
    InterlockOpen = 1,      // Розірвано фізичний контур безпеки (Interlock)
    VoltageOutOfRange = 2,  // Напруга живлення поза допустимими межами
    ThermalShutdown = 3,    // Критичний перегрів лазерного діода
    WatchdogFault = 4       // Втрата контролю від хост-системи
};

/**
 * @brief Інтерфейс апаратного сенсорного моніторингу платформи.
 */
class ISafetyHardware {
public:
    virtual ~ISafetyHardware() = default;
    virtual bool read_interlock_closed() = 0; // true = ланцюг безпеки замкнено (безпечно)
    virtual uint16_t read_voltage_mv() = 0;   // Виміряна напруга живлення у мілівольтах
};

/**
 * @brief Головний супервізор безпеки лазерної системи.
 * 
 * Безперервно опитує стан контуру апаратного захисту (Interlock loop), контролює
 * напругу живлення діода та тепловий стан. У разі будь-якого відхилення здійснює
 * миттєве апаратне блокування випромінювання (emergency lockout).
 */
class SafetySupervisor {
public:
    struct VoltageLimits {
        uint16_t min_voltage_mv{4600}; // Мінімальна напруга (4.6 В)
        uint16_t max_voltage_mv{5400}; // Максимальна напруга (5.4 В)
    };

    explicit SafetySupervisor(LaserOutput& output,
                              ThermalGuard& thermal,
                              ISafetyHardware& hw,
                              const VoltageLimits& limits = {}) noexcept
        : output_(output), thermal_(thermal), hw_(hw), limits_(limits) {}

    /**
     * @brief Регулярний цикл діагностики та перевірки безпеки.
     * Повинен викликатися з високим пріоритетом у головному циклі.
     */
    bool evaluate_safety() noexcept {
        // Перевірка 1: Фізичний контур блокування (Interlock switch / двері захисного кожуха)
        if (!hw_.read_interlock_closed()) {
            trip(SafetyFault::InterlockOpen);
            return false;
        }

        // Перевірка 2: Допустимість напруги живлення драйвера діода
        const uint16_t v_mv = hw_.read_voltage_mv();
        if (v_mv < limits_.min_voltage_mv || v_mv > limits_.max_voltage_mv) {
            trip(SafetyFault::VoltageOutOfRange);
            return false;
        }

        // Перевірка 3: Критичний тепловий бюджет
        if (thermal_.is_critical_overheat()) {
            trip(SafetyFault::ThermalShutdown);
            return false;
        }

        return true;
    }

    /**
     * @brief Скидання аварійного стану блокування після усунення першопричини.
     */
    bool try_clear_fault() noexcept {
        if (!hw_.read_interlock_closed() || thermal_.is_critical_overheat()) {
            return false; // Відмова у скиданні, якщо небезпечний фактор досі присутній
        }

        fault_ = SafetyFault::None;
        return true;
    }

    [[nodiscard]] bool is_armed() const noexcept { return fault_ == SafetyFault::None; }
    [[nodiscard]] SafetyFault current_fault() const noexcept { return fault_; }

private:
    void trip(SafetyFault fault) noexcept {
        fault_ = fault;
        output_.shutdown(); // Негайне апаратне вимкнення виходу затвора
    }

    LaserOutput& output_;
    ThermalGuard& thermal_;
    ISafetyHardware& hw_;
    VoltageLimits limits_{};
    SafetyFault fault_{SafetyFault::None};
};

} // namespace laser

#endif // SAFETY_SUPERVISOR_HPP_
