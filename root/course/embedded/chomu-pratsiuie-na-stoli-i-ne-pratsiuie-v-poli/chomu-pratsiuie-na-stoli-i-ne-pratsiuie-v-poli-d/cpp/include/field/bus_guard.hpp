// bus_guard.hpp — нагляд за зовнішньою шиною та її розчепірювання.
//
// Класичне польове зависання: раб посеред віддавання байта побачив на
// живленні просадку й перезапустився, а майстер — ні. Раб тримає SDA внизу,
// чекаючи на такти, яких уже ніхто не дасть; майстер бачить зайняту шину
// й не може навіть почати. Периферія сама з цього не вийде — рятує лише
// ручне тактування ніжками.
#pragma once

#include <cstdint>
#include <expected>
#include <span>

#include "field/fault_log.hpp"

namespace field {

enum class BusHealth : std::uint8_t {
    Ok = 0,
    Silent,     // раб не відповідає, але лінії вільні
    Stuck,      // тримали, розчепірили, а він і далі мовчить
    Recovered,  // тримали, розчепірили, зараз відповідає
    Dead        // порятунок не допоміг: лінію тримає не раб
};

class BusGuard {
public:
    BusGuard(FaultLog& log, std::uint8_t address);

    // Перевіряє шину й, коли треба, сама її рятує.
    [[nodiscard]] BusHealth check();

    // Читання з обліком: невдача веде лічильники так само, як і перевірка.
    [[nodiscard]] bool read(std::uint8_t reg, std::span<std::uint8_t> buf);

    // Скільки порятунків поспіль не дали результату. Головний цикл за цим
    // числом вирішує, коли перестати пробувати те саме.
    [[nodiscard]] std::uint16_t hopelessStreak() const noexcept { return hopeless_; }
    [[nodiscard]] std::uint32_t recoveriesTotal() const noexcept { return recoveries_; }

private:
    [[nodiscard]] bool rescue();

    FaultLog& log_;
    std::uint8_t address_;
    std::uint16_t failStreak_{0};
    std::uint16_t hopeless_{0};
    std::uint32_t recoveries_{0};
};

}  // namespace field
