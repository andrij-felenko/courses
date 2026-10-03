#ifndef ESP8266_RELAY_DRIVER_HPP
#define ESP8266_RELAY_DRIVER_HPP

#include <cstdint>
#include <cstddef>
#include <string_view>
#include "uart_ring_buffer.hpp"

// Режими робочих виводів GPIO ESP8266
enum class GpioMode : uint8_t {
    Input = 0,
    Output = 1,
    InputPullup = 2
};

// Логічні рівні на виводах GPIO
enum class LogicLevel : uint8_t {
    Low = 0,
    High = 1
};

// Статуси виконання операцій драйвера
enum class DriverStatus : uint8_t {
    Ok,
    Timeout,
    ErrorResponse,
    InvalidPin,
    HardwareError
};

// Типи зворотних викликів для абстрагування апаратури хост-контролера
using UartTxCallback = void(*)(std::string_view data);
using GetTickMsFn = uint32_t(*)();
using DelayMsFn = void(*)(uint32_t ms);

class Esp8266RelayDriver;

/**
 * @brief RAII-обгортка для гарантування безпечного стану силового реле.
 * Забезпечує автоматичне повернення GPIO виводу у безпечний вихідний стан
 * при знищенні об'єкта або виникненні аварійних ситуацій.
 */
class RelayPinGuard {
public:
    RelayPinGuard(Esp8266RelayDriver& driver, uint8_t pin, LogicLevel safe_level = LogicLevel::Low);
    ~RelayPinGuard();

    // Забороняємо копіювання для запобігання подвійному керуванню ресурсом
    RelayPinGuard(const RelayPinGuard&) = delete;
    RelayPinGuard& operator=(const RelayPinGuard&) = delete;

    // Переміщення дозволено
    RelayPinGuard(RelayPinGuard&& other) noexcept;
    RelayPinGuard& operator=(RelayPinGuard&& other) noexcept;

    DriverStatus setState(LogicLevel level);
    DriverStatus toggle();

    LogicLevel currentLevel() const noexcept { return current_level_; }
    uint8_t pin() const noexcept { return pin_; }
    bool isActive() const noexcept { return active_; }

    void release() noexcept { active_ = false; }

private:
    Esp8266RelayDriver* driver_{nullptr};
    uint8_t pin_{0};
    LogicLevel safe_level_{LogicLevel::Low};
    LogicLevel current_level_{LogicLevel::Low};
    bool active_{false};
};

/**
 * @brief Клас-драйвер керування GPIO виводами ESP8266 через AT-команди.
 * Реалізує формування AT-інструкцій без динамічних алокацій, неблокуючий
 * розбір відповідей та врахування strapping pins (GPIO0, GPIO2, GPIO15).
 */
class Esp8266RelayDriver {
public:
    Esp8266RelayDriver(UartRingBuffer<256>& rx_buffer,
                       UartTxCallback tx_cb,
                       GetTickMsFn tick_cb,
                       DelayMsFn delay_cb);

    /**
     * @brief Перевірка, чи належить вивід до конфігураційних (strapping pins: GPIO0, GPIO2, GPIO15).
     */
    static bool isStrappingPin(uint8_t pin) noexcept;

    /**
     * @brief Ініціалізація виводу GPIO з урахуванням затримок завантаження strapping pins.
     */
    DriverStatus initPin(uint8_t pin, GpioMode mode, LogicLevel initial_level = LogicLevel::Low);

    /**
     * @brief Запис логічного рівня у вивід GPIO (AT+PINWRITE).
     */
    DriverStatus writePin(uint8_t pin, LogicLevel level);

    /**
     * @brief Зчитування поточного логічного рівня виводу GPIO (AT+PINREAD).
     */
    DriverStatus readPin(uint8_t pin, LogicLevel& out_level);

    /**
     * @brief Передача довільної AT-команди та неблокуюче очікування відповіді.
     */
    DriverStatus sendAtCommand(std::string_view cmd, uint32_t timeout_ms = 1000);

private:
    UartRingBuffer<256>& rx_buffer_;
    UartTxCallback tx_cb_;
    GetTickMsFn tick_cb_;
    DelayMsFn delay_cb_;

    // Форматування AT-команд у стаціонарний буфер без алокацій у динамічній пам'яті
    static std::string_view formatPinModeCmd(uint8_t pin, GpioMode mode, char* buf, size_t buf_size) noexcept;
    static std::string_view formatPinWriteCmd(uint8_t pin, LogicLevel level, char* buf, size_t buf_size) noexcept;
    static std::string_view formatPinReadCmd(uint8_t pin, char* buf, size_t buf_size) noexcept;

    // Парсинг відповіді на команду читання виводу (+PINREAD:<pin>,<level>)
    static bool parsePinReadResponse(std::string_view response, uint8_t pin, LogicLevel& out_level) noexcept;
};

#endif // ESP8266_RELAY_DRIVER_HPP
