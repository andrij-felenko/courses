// Шина живлення датчиків: програмний standby по I2C, силовий ключ, розряд.
//
// Порядок тут не косметичний. Спершу датчик просять заснути командою, потім
// зупиняють шину, і лише тоді розмикають ключ — інакше ведений лишається з
// недоказаним байтом і тримає SDA у нулі.
#pragma once

#include <cstdint>
#include <expected>
#include <span>

#include "mcu.hpp"
#include "status.hpp"

namespace lowpower {

class SensorRail {
public:
    // Силовий ключ P-MOSFET на PB12: нуль відкриває, одиниця закриває.
    explicit SensorRail(mcu::Pin gate) noexcept : gate_{gate} {}

    // Standby датчикам, зупинка шин, розмикання ключа, витримка на розряд.
    [[nodiscard]] Status shutdown();

    // Ключ, час наростання, перевірка ідентифікатора, повторна конфігурація.
    [[nodiscard]] Status power_up();

    // Один вимір температури — щоб цикл сну мав що робити між снами.
    [[nodiscard]] std::expected<std::int32_t, Error> read_temperature_raw();

    [[nodiscard]] bool powered() const noexcept { return powered_; }

    // Обмін по I2C. Адреса семибітна, як у даташиті.
    [[nodiscard]] Status write_reg(std::uint8_t addr7, std::uint8_t reg, std::uint8_t value);
    [[nodiscard]] Status read_regs(std::uint8_t addr7, std::uint8_t reg,
                                   std::span<std::uint8_t> dst);

private:
    [[nodiscard]] Status wait_isr(mcu::u32 flag);
    [[nodiscard]] Status finish_transfer();

    mcu::Pin gate_;
    bool powered_{false};
};

} // namespace lowpower
