// transport.hpp — Рівень 1 як концепти, а не як таблиця вказівників.
//
// Драйвер не знає ані типу шини, ані бібліотеки виробника: він вимагає лише
// три операції. Невідповідність контракту ловиться на етапі компіляції, а не
// нульовим вказівником у польоті.
#pragma once

#include <chrono>
#include <concepts>
#include <cstdint>
#include <span>

#include "status.hpp"

namespace accel {

// Транспорт сам знає адресу свого чипа: у C++ її природне місце — усередині
// об'єкта шини, а не окремим параметром кожного виклику.
template <typename T>
concept BusTransport = requires(T transport,
                                std::uint8_t reg,
                                std::span<std::uint8_t> rx,
                                std::span<const std::uint8_t> tx,
                                std::chrono::milliseconds pause) {
    { transport.read(reg, rx) } -> std::same_as<Result<void>>;
    { transport.write(reg, tx) } -> std::same_as<Result<void>>;
    { transport.delay(pause) } -> std::same_as<void>;
};

// Лінії SCL/SDA, віддані з периферії I2C у звичайний GPIO заради аварійного
// скидання шини. Виходи типу «відкритий стік»: false притискає лінію до
// землі, true лише відпускає її на резистор підтяжки.
template <typename T>
concept GpioLines = requires(T lines, bool level, std::chrono::microseconds pause) {
    { lines.scl(level) } -> std::same_as<void>;
    { lines.sda(level) } -> std::same_as<void>;
    { lines.sdaLevel() } -> std::same_as<bool>;
    { lines.delay(pause) } -> std::same_as<void>;
    { lines.releaseToPeripheral() } -> std::same_as<void>;
};

} // namespace accel
