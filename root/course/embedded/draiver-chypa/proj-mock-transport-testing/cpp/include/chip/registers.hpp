// registers.hpp — регістрова карта й фізичні коефіцієнти еталонного чипа.
//
// Усе тут constexpr: перерахунок діапазону в ціну відліку відбувається під
// час компіляції, тож у прошивці не лишається ні таблиці, ні ділення.
#pragma once

#include <cstdint>

namespace chip::reg {

inline constexpr std::uint8_t WhoAmI  = 0x0F; // заводський ID, лише читання
inline constexpr std::uint8_t Ctrl1   = 0x20; // ODR, споживання, дозвіл осей
inline constexpr std::uint8_t Ctrl4   = 0x23; // BDU, шкала, роздільність
inline constexpr std::uint8_t Status  = 0x27; // готовність і перезапис даних
inline constexpr std::uint8_t OutXL   = 0x28; // перший байт блоку X/Y/Z
inline constexpr std::uint8_t OutZH   = 0x2D; // останній байт того ж блоку

// Старший біт адреси просить чип рухати внутрішній вказівник після кожного
// байта. Без нього пакетне читання шість разів віддасть OutXL.
inline constexpr std::uint8_t AutoIncrement = 0x80;

inline constexpr std::uint8_t WhoAmIValue = 0x33;

// CTRL1
inline constexpr std::uint8_t Ctrl1OdrMask  = 0xF0;
inline constexpr std::uint8_t Ctrl1OdrShift = 4;
inline constexpr std::uint8_t Ctrl1LowPower = 1U << 3;
inline constexpr std::uint8_t Ctrl1AxesMask = 0x07; // X | Y | Z

// CTRL4
inline constexpr std::uint8_t Ctrl4Bdu     = 1U << 7; // блокування оновлення
inline constexpr std::uint8_t Ctrl4FsMask  = 0x30;
inline constexpr std::uint8_t Ctrl4FsShift = 4;
inline constexpr std::uint8_t Ctrl4HighRes = 1U << 3;

// STATUS
inline constexpr std::uint8_t StatusZyxda = 1U << 3; // готові дані трьох осей
inline constexpr std::uint8_t StatusZyxor = 1U << 7; // відлік не встигли взяти

inline constexpr std::uint8_t OdrPowerDown = 0x0;
inline constexpr std::uint8_t Odr100Hz     = 0x5;

} // namespace chip::reg

namespace chip {

inline constexpr float kGravity = 9.80665F; // м/с²

enum class Range : std::uint8_t { G2 = 0, G4 = 1, G8 = 2, G16 = 3 };

// Повна шкала діапазону в одиницях g.
[[nodiscard]] constexpr int fullScaleG(Range range) noexcept
{
    switch (range) {
    case Range::G2:  return 2;
    case Range::G4:  return 4;
    case Range::G8:  return 8;
    case Range::G16: return 16;
    }
    return 2;
}

// Ціна одного відліку в м/с²: шкала розкладена на весь знаковий 16-бітний
// діапазон, тому при ±2 g одиниця g — це рівно 16384 відліки.
[[nodiscard]] constexpr float sensitivity(Range range) noexcept
{
    return static_cast<float>(fullScaleG(range)) * kGravity / 32768.0F;
}

// Прискорення в SI. Іменована структура, а не три голі float: переплутати
// осі місцями в аргументах — класика драйверів давачів.
struct Sample {
    float x{}; // м/с²
    float y{};
    float z{};
};

} // namespace chip
