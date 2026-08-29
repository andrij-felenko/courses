/* i2c_bus.hpp — контролер I2C1 і обхід зависання шини з Errata Sheet.
 *
 * Дефект: кінцевий автомат зупиняється посеред кадру, прапорець BUSY
 * лишається піднятим назавжди, ведений тримає SDA притиснутою до землі.
 * Записами в регістри блоку з цього стану не вийти.
 *
 * Обхід виробника: вимкнути блок, забрати ніжки в ручне керування, видати
 * такти на SCL, доки ведений не відпустить SDA, згенерувати STOP, повернути
 * ніжки в альтернативну функцію й перезапустити блок скиданням.
 */
#pragma once

#include <expected>

#include "hw/mmio.hpp"

namespace hw {

enum class BusError {
    bad_clock,      // частота APB1 поза діапазоном поля FREQ
    scl_stuck_low,  // SCL притиснута — це вже несправність плати
    sda_stuck_low,  // дев'ять тактів не звільнили лінію
    still_busy,     // блок перезапущено, а BUSY не впав
};

class I2cBus {
public:
    /* apb1 — частота шини, до якої підключений блок (поле CR2_FREQ);
     * cpu  — частота ядра, потрібна для відліку затримок під час ручного
     *        тактування ліній. */
    [[nodiscard]] static std::expected<I2cBus, BusError> open(Hertz apb1, Hertz cpu) noexcept;

    ~I2cBus();

    I2cBus(I2cBus&& other) noexcept;
    I2cBus& operator=(I2cBus&& other) noexcept;
    I2cBus(const I2cBus&) = delete;
    I2cBus& operator=(const I2cBus&) = delete;

    /* Прапорець BUSY регістра SR2 має тип доступу RO: ним керує лише кремній. */
    [[nodiscard]] bool busy() const noexcept;

    /* Повний обхід еррати. Успіх означає, що шина знову вільна. */
    [[nodiscard]] std::expected<void, BusError> recover() noexcept;

private:
    I2cBus(Hertz apb1, Hertz cpu) noexcept : apb1_{apb1}, cpu_{cpu} {}

    [[nodiscard]] std::expected<void, BusError> configure() noexcept;
    void release() noexcept;

    Hertz apb1_{};
    Hertz cpu_{};
    bool  owns_{true};
};

} // namespace hw
