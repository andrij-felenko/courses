// hal/i2c_bus.hpp — інверсія залежностей засобами мови.
// Там, де C будує таблицю покажчиків на функції руками, C++ бере чистий
// абстрактний клас: та сама непряма адресація через таблицю віртуальних
// методів, але за коректністю сигнатур стежить компілятор.
//
// Помилку віддаємо через std::expected, а не через -1 і errno: викликач
// не може забути її перевірити, бо значення позначене [[nodiscard]].
#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace hal {

enum class I2cError : std::uint8_t {
    Nack,      // мікросхема не підтвердила адресу чи байт
    BusError,  // втрата арбітражу, залипла лінія SDA, шум
    Timeout,   // контролер не дочекався готовності
    BadArgs    // аргументи виклику не мають сенсу
};

[[nodiscard]] constexpr std::string_view to_string(I2cError e) noexcept
{
    switch (e) {
    case I2cError::Nack:     return "NACK";
    case I2cError::BusError: return "BUS";
    case I2cError::Timeout:  return "TIMEOUT";
    case I2cError::BadArgs:  return "ARGS";
    }
    return "?";
}

// Реалізацію дає порт: контролер I2C1 на STM32, імітація в пам'яті на
// комп'ютері розробника. Драйвери бачать лише це посилання.
class II2cBus {
public:
    virtual ~II2cBus() = default;

    II2cBus(const II2cBus&) = delete;
    II2cBus& operator=(const II2cBus&) = delete;

    [[nodiscard]] virtual std::expected<void, I2cError>
    write(std::uint8_t address, std::span<const std::uint8_t> data) = 0;

    [[nodiscard]] virtual std::expected<void, I2cError>
    read(std::uint8_t address, std::span<std::uint8_t> data) = 0;

    // Передати й одразу прочитати без відпускання шини (повторний START).
    // Реалізація за замовчуванням складає це з двох окремих транзакцій —
    // повільніше, зате порт може її не писати.
    [[nodiscard]] virtual std::expected<void, I2cError>
    write_read(std::uint8_t address,
               std::span<const std::uint8_t> tx,
               std::span<std::uint8_t> rx)
    {
        if (auto res = write(address, tx); !res) {
            return res;
        }
        return read(address, rx);
    }

protected:
    II2cBus() = default;
};

} // namespace hal
