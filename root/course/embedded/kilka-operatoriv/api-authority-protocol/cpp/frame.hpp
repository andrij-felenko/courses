#pragma once

#include <cstddef>
#include <cstring>
#include <expected>
#include <optional>
#include <span>
#include <type_traits>
#include <vector>

#include "protocol.hpp"

namespace auth {

inline constexpr std::size_t HeaderSize = 20;
inline constexpr std::size_t MaxPayload = 64;

// CRC16-CCITT, поліном 0x1021. seed дозволяє рахувати суму двома шматками:
// спершу заголовок без поля CRC, далі корисне навантаження.
[[nodiscard]] std::uint16_t crc16_ccitt(std::span<const std::byte> data,
                                        std::uint16_t seed = 0xFFFF) noexcept;

// payload дивиться всередину розібраного буфера — живе рівно стільки, скільки він.
struct Frame {
    PacketHeader header{};
    std::span<const std::byte> payload{};
};

[[nodiscard]] std::expected<Frame, StatusCode> decode(std::span<const std::byte> raw) noexcept;

// magic, version, payload_len і crc16 виставляє сама функція.
[[nodiscard]] std::vector<std::byte> encode(PacketHeader header,
                                            std::span<const std::byte> payload);

template <class T>
    requires std::is_trivially_copyable_v<T>
[[nodiscard]] std::vector<std::byte> encode_message(PacketHeader header, const T& body) {
    header.msg_id = MessageTraits<T>::id;
    std::byte raw[sizeof(T)];
    std::memcpy(raw, &body, sizeof(T));
    return encode(header, std::span<const std::byte>{raw, sizeof(T)});
}

template <class T>
    requires std::is_trivially_copyable_v<T>
[[nodiscard]] std::expected<T, StatusCode> body_as(const Frame& frame) noexcept {
    if (frame.header.msg_id != MessageTraits<T>::id || frame.payload.size() != sizeof(T)) {
        return std::unexpected(StatusCode::BadLength);
    }
    T out{};
    std::memcpy(&out, frame.payload.data(), sizeof(T));
    return out;
}

// Пошук межі кадру в потоці послідовного порту.
[[nodiscard]] std::optional<std::size_t> find_start(std::span<const std::byte> raw) noexcept;

// Сурогат підпису командирського кадру: детермінована згортка спільного
// ключа з полями, які неможливо повторити (seq і час відправника).
// У бойовій системі тут HMAC-SHA256 за схемою підпису MAVLink v2.
[[nodiscard]] std::uint32_t sign_override(std::uint32_t key, std::uint8_t src,
                                          std::uint16_t seq, std::uint32_t ts) noexcept;

}  // namespace auth
