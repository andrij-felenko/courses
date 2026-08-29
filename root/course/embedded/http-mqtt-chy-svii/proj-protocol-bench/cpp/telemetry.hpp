// Формат телеметрії вузла: спільні типи для передавача й приймача (C++23).
#pragma once

#include <cstddef>
#include <cstdint>
#include <string_view>

namespace telem {

// Виміри в фіксованій точці: цілі, бо перетворення в текст із комою — це
// найдорожча дія в усьому ланцюжку, і в бінарному кадрі її просто немає.
struct Sample {
    std::uint32_t timestamp_s{};   // Unix-час або uptime, секунди
    std::int16_t  temp_centi_c{};  // 2450 = 24.50 °C (буває відʼємна)
    std::uint16_t humidity_pct{};  // 6020 = 60.20 %
    std::uint16_t vbat_mv{};       // 3280 = 3.280 В
};

inline constexpr std::uint8_t  kMagic         = 0xAA;
inline constexpr std::uint8_t  kTypeTelemetry = 0x01;

// Розмір кадру — частина специфікації протоколу, а не наслідок того, як
// компілятор вирівняв структуру. Тому тут стоїть число, а поля кадру
// пишуться й читаються поодинці; жодного пакування структур і жодної
// залежності від порядку байтів платформи.
inline constexpr std::size_t kFrameSize   = 16;
inline constexpr std::size_t kFrameCrcLen = kFrameSize - sizeof(std::uint16_t);

enum class EncodeError {
    BufferTooSmall,
    Formatting,
    BadTopic,
    BadPacketId,
};

enum class DecodeError {
    TooShort,
    BadMagic,
    BadType,
    BadCrc,
    Replay,
};

[[nodiscard]] constexpr std::string_view describe(EncodeError e) noexcept
{
    switch (e) {
        case EncodeError::BufferTooSmall: return "буфер замалий";
        case EncodeError::Formatting:     return "не склалося форматування";
        case EncodeError::BadTopic:       return "недопустима тема MQTT";
        case EncodeError::BadPacketId:    return "недопустимий Packet Identifier";
    }
    return "?";
}

[[nodiscard]] constexpr std::string_view describe(DecodeError e) noexcept
{
    switch (e) {
        case DecodeError::TooShort: return "закоротка датаграма";
        case DecodeError::BadMagic: return "чужий синхробайт";
        case DecodeError::BadType:  return "невідомий тип";
        case DecodeError::BadCrc:   return "CRC не збігається";
        case DecodeError::Replay:   return "дублікат або повтор";
    }
    return "?";
}

}  // namespace telem
