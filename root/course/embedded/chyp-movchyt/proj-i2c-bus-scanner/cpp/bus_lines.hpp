/* Контракт ліній I2C у режимі GPIO з відкритим стоком.
   Замість таблиці вказівників на функції — концепт: плата підставляє
   свій тип, і невідповідність контракту ловить компілятор, а не таймаут. */
#pragma once

#include <concepts>
#include <cstdint>
#include <string_view>

enum class BusError {
    nack,             /* адресний байт видано, підтвердження на 9-му такті немає */
    lines_busy,       /* SDA лежить у нулі ще до умови START */
    stretch_timeout,  /* SCL не піднімається: немає підтяжки або ведений тримає такт */
    stop_failed       /* після умови STOP лінія SDA не піднялася */
};

[[nodiscard]] constexpr std::string_view describe(BusError error) noexcept {
    switch (error) {
    case BusError::nack:            return "NACK: адресу видано, підтвердження немає";
    case BusError::lines_busy:      return "SDA лежить у нулі ще до умови START";
    case BusError::stretch_timeout: return "SCL не піднімається: немає підтяжки або ведений тримає такт";
    case BusError::stop_failed:     return "після умови STOP лінія SDA не піднялася";
    }
    return "невідома помилка шини";
}

template <typename T>
concept OpenDrainLines = requires(T& io, std::uint32_t us) {
    { io.take_pins() } -> std::same_as<void>;          /* забрати виводи в GPIO */
    { io.give_pins_back() } -> std::same_as<void>;     /* віддати їх апаратному блоку */
    { io.scl_release() } -> std::same_as<void>;
    { io.scl_drive_low() } -> std::same_as<void>;
    { io.scl_read() } -> std::same_as<bool>;
    { io.sda_release() } -> std::same_as<void>;
    { io.sda_drive_low() } -> std::same_as<void>;
    { io.sda_read() } -> std::same_as<bool>;
    { io.delay_us(us) } -> std::same_as<void>;
};
