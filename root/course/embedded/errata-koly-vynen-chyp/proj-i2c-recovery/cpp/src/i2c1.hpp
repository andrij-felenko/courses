#pragma once

#include <cstdint>
#include <expected>

namespace hw {

enum class I2cError : std::uint8_t {
    BusBusy,    /* BUSY не знімається — той самий симптом заклиненої шини */
    Timeout,    /* подія не настала: ведений мовчить або тримає такт */
    Nack,       /* чип на шині є, але адресу не підтвердив */
    BusError,   /* BERR: контролер побачив START/STOP не на своєму місці */
};

/* Модуль I2C1 як ресурс: конструктор вмикає й налаштовує, деструктор гасить.
   Виводи PB6/PB7 має вже перевести в Alternate Function recover_i2c1_bus() —
   тут їх не чіпаємо, щоб два власники не сперечалися за той самий CRL. */
class I2c1 {
public:
    explicit I2c1(std::uint32_t bus_hz) noexcept;
    ~I2c1();

    I2c1(const I2c1&) = delete;
    I2c1& operator=(const I2c1&) = delete;

    /* Читання одного регістра: запис номера, повторний START, байт із NACK і STOP */
    [[nodiscard]] std::expected<std::uint8_t, I2cError>
    read_register(std::uint8_t addr7, std::uint8_t reg) noexcept;
};

} // namespace hw
