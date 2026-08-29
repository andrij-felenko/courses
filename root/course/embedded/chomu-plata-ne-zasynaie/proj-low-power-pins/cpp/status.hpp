// Спільний словник відмов усього ходу присипляння.
//
// Замість -1 та errno тут std::expected: виклик або зробив свою частину, або
// повернув, ЩО САМЕ не вдалося, і викликач не може мовчки цього не помітити.
#pragma once

#include <expected>
#include <string_view>

namespace lowpower {

enum class Error {
    UartNotDrained,   // TC так і не виставився: кадр обірвався б посеред байта
    SpiBusy,          // зсувний регістр SPI досі крутить біти
    I2cBusy,          // транзакція не завершилася
    I2cStuck,         // ведений тримає SDA у нулі й після дев'яти тактів
    SensorNack,       // за адресою ніхто не відповів
    SensorTimeout,    // модуль не дійшов до наступного стану
    SensorWrongId,    // після подання живлення на шині не той датчик
};

// Порожній успіх: усе, що ці операції повертають, — це факт «вдалося».
using Status = std::expected<void, Error>;

[[nodiscard]] constexpr std::string_view describe(Error e) noexcept
{
    switch (e) {
    case Error::UartNotDrained: return "uart: TC не виставився";
    case Error::SpiBusy:        return "spi: BSY не знявся";
    case Error::I2cBusy:        return "i2c: BUSY не знявся";
    case Error::I2cStuck:       return "i2c: SDA лишилася в нулі";
    case Error::SensorNack:     return "датчик не відповів (NACK)";
    case Error::SensorTimeout:  return "датчик: таймаут кроку";
    case Error::SensorWrongId:  return "на шині не той датчик";
    }
    return "?";
}

} // namespace lowpower
