// frame.hpp — формат кадру телеметрії: 16 байтів на дроті, без вирівнювання.
//
// Тип на дроті й тип у програмі — це той самий тип. Ніякого серіалізатора,
// ніякої динамічної пам'яті: структура лягає в датаграму як послідовність байтів.
#pragma once

#include <bit>
#include <cstddef>
#include <cstdint>
#include <type_traits>

namespace telemetry {

// Порядок байтів у кадрі фіксований — little-endian: і Cortex-M, і x86-шлюз
// зберігають числа однаково, тож перестановки не потрібні нікому.
static_assert(std::endian::native == std::endian::little,
              "формат кадру little-endian: на big-endian потрібні перестановки");

inline constexpr std::uint8_t kMagic = 0xA5;  // відсіює чужі датаграми на порті

enum class MsgType : std::uint8_t {
    Telemetry = 0x01,
    Ack       = 0x02,
};

#pragma pack(push, 1)
struct Packet {
    std::uint8_t  magic{kMagic};
    std::uint8_t  type{static_cast<std::uint8_t>(MsgType::Telemetry)};
    std::uint16_t seq{0};          // лічильник кадру: втрати й дублікати видно
    std::uint32_t timestamp{0};    // Unix time вимірювання
    std::int16_t  temperature{0};  // °C * 100
    std::uint16_t humidity{0};     // % * 100
    std::uint16_t vbat_mv{0};      // напруга батареї, мВ
    std::uint16_t crc{0};          // CRC-16-CCITT по перших 14 байтах
};
#pragma pack(pop)

// Якщо компілятор проігнорує упакування, кадр роз'їдеться — ловимо на збірці.
static_assert(sizeof(Packet) == 16, "кадр телеметрії мусить бути рівно 16 байтів");
static_assert(std::is_trivially_copyable_v<Packet>, "кадр має копіюватися побайтово");

inline constexpr std::size_t kTelemetrySize = sizeof(Packet);
inline constexpr std::size_t kAckSize = 4;

// Вимір у тому вигляді, в якому його віддав давач.
struct Sample {
    std::uint32_t timestamp{0};
    std::int16_t  temperature{0};
    std::uint16_t humidity{0};
    std::uint16_t vbat_mv{0};
};

enum class FrameError {
    TooShort,        // датаграма коротша за кадр
    BadMagic,        // не наш протокол
    BadType,         // не той тип повідомлення
    BadCrc,          // кадр побився в дорозі
    BufferTooSmall,  // немає куди складати
};

}  // namespace telemetry
