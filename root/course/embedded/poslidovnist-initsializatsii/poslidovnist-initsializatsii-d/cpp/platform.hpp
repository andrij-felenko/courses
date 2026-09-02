#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <string_view>

// Контракт платформного шару. Помилка приходить значенням у std::expected,
// а виводи шини віддаються під ручне тактування через RAII-захоплення.
namespace platform {

enum class BusError { Nack, Stuck };
std::string_view to_string(BusError error);

// Годинник платформи: на платі це SysTick, у хостовій моделі — віртуальний лічильник.
struct Clock {
    using duration = std::chrono::milliseconds;
    using rep = duration::rep;
    using period = duration::period;
    using time_point = std::chrono::time_point<Clock>;
    static constexpr bool is_steady = true;
    static time_point now() noexcept;
};

void sleep(std::chrono::milliseconds duration);
void sleep(std::chrono::microseconds duration);
void watchdog_kick() noexcept;

class I2cBus {
public:
    [[nodiscard]] std::expected<std::uint8_t, BusError> read(std::uint8_t dev,
                                                             std::uint8_t reg) noexcept;
    [[nodiscard]] std::expected<void, BusError> write(std::uint8_t dev, std::uint8_t reg,
                                                      std::uint8_t value) noexcept;
};

// Ключ живлення периферійної лінії (обидва давачі сидять на одному VDD).
class PowerRail {
public:
    void on() noexcept;
    void off() noexcept;
    // Повний перезапуск живлення: розряд декаплінгу, подача, витримка POR.
    void cycle(std::chrono::milliseconds discharge, std::chrono::milliseconds boot);
};

// Захоплення виводів шини під ручне тактування. Периферії вони повертаються
// у деструкторі — з будь-якої гілки виходу, без ручного відновлення.
class GpioTakeover {
public:
    GpioTakeover() noexcept;
    ~GpioTakeover();
    GpioTakeover(const GpioTakeover&) = delete;
    GpioTakeover& operator=(const GpioTakeover&) = delete;

    void scl(bool level) noexcept;
    void sda(bool level) noexcept;
    [[nodiscard]] bool sda_is_high() const noexcept;
};

[[nodiscard]] bool has_nrst(std::uint8_t dev) noexcept;
void pulse_nrst(std::uint8_t dev) noexcept;

void fault_led(bool on);
void disable_actuators();

// Тільки для хостової моделі: розкладка стенда й сценарій завад.
void sim_reset_board() noexcept;

}  // namespace platform
