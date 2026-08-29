// Три способи запакувати одну вибірку телеметрії (C++23).
//
// Жодна функція не володіє памʼяттю: буфер дає викликач, а назад приходить
// перегляд саме тієї частини буфера, яку справді заповнили. Помилка — це
// значення в std::expected, а не -1 з errno десь поруч.
#pragma once

#include "telemetry.hpp"

#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace telem {

// HTTP/1.1 POST із JSON-тілом, заголовком Bearer і Content-Length.
[[nodiscard]] std::expected<std::string_view, EncodeError>
buildHttpPost(const Sample& s,
              std::string_view host,
              std::string_view token,
              std::span<char> out) noexcept;

// MQTT 3.1.1 PUBLISH з QoS 1: фіксований заголовок, Remaining Length зі
// змінним кодуванням, тема, Packet Identifier, JSON-payload.
[[nodiscard]] std::expected<std::span<const std::uint8_t>, EncodeError>
buildMqttPublishQos1(const Sample& s,
                     std::string_view topic,
                     std::uint16_t packet_id,
                     std::span<std::uint8_t> out) noexcept;

// Власний бінарний кадр: 16 байтів, з них 10 корисних, плюс CRC-16.
[[nodiscard]] std::expected<std::span<const std::uint8_t>, EncodeError>
buildBinaryFrame(const Sample& s,
                 std::uint16_t seq,
                 std::span<std::uint8_t> out) noexcept;

}  // namespace telem
