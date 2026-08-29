// types.hpp — словник предметної області: діапазон, частота, відлік, калібрування.
#pragma once

#include <array>
#include <cstdint>

namespace accel {

enum class Range : std::uint8_t { G2 = 0, G4 = 1, G8 = 2, G16 = 3 };

enum class Odr : std::uint8_t {
    PowerDown = 0x0,
    Hz1       = 0x1,
    Hz10      = 0x2,
    Hz25      = 0x3,
    Hz50      = 0x4,
    Hz100     = 0x5,
    Hz200     = 0x6,
    Hz400     = 0x7
};

// Значення дорівнює зсуву вправо перед розширенням знака: 12-бітний відлік
// лежить у старших бітах 16-бітного слова, молодші чотири — сміття.
enum class Resolution : std::uint8_t { Bits16 = 0, Bits12LeftAligned = 4 };

enum class FifoMode : std::uint8_t {
    Bypass       = 0, // буфер вимкнено, лише останній відлік
    Fifo         = 1, // набирає до кінця й зупиняється
    Stream       = 2, // кільце: нове затирає найстаріше
    StreamToFifo = 3  // кільце до події, далі добір до кінця
};

// Прискорення у метрах на секунду в квадраті.
struct Acceleration {
    float x{};
    float y{};
    float z{};
};

// Той самий відлік для ядер без FPU — цілі мілігравітації.
struct MilliG {
    std::int32_t x{};
    std::int32_t y{};
    std::int32_t z{};
};

// Він же одразу в SI, але теж цілим: міліметри на секунду в квадраті.
struct MilliMetrePerSecond2 {
    std::int32_t x{};
    std::int32_t y{};
    std::int32_t z{};
};

using RawSample = std::array<std::int16_t, 3>;

// Корекція конкретного екземпляра: зміщення нуля в сирих відліках і
// підсилення осі. Ціла копія підсилення потрібна шляху без плаваючої коми.
struct Calibration {
    std::array<std::int16_t, 3> offset{0, 0, 0};
    std::array<float, 3>        gain{1.0F, 1.0F, 1.0F};
    std::array<std::int32_t, 3> gainMilli{1000, 1000, 1000};
};

struct FifoConfig {
    FifoMode     mode{FifoMode::Bypass};
    std::uint8_t watermark{0}; // поріг у вибірках, менший за глибину буфера
};

struct FifoStatus {
    std::uint8_t samples{0};
    bool         watermarkHit{false};
    bool         overrun{false};
};

struct DataStatus {
    bool ready{false};
    bool overrun{false}; // попередній відлік забрати не встигли
};

// Чутливість у мікро-g на молодший розряд — з даташита, одна на обидва шляхи
// перетворення (з плаваючою й фіксованою комою).
[[nodiscard]] constexpr std::int32_t sensitivityMicroG(Range range) noexcept
{
    switch (range) {
    case Range::G2:  return 61;
    case Range::G4:  return 122;
    case Range::G8:  return 244;
    case Range::G16: return 732;
    }
    return 61;
}

inline constexpr float kStandardGravity = 9.80665F;

} // namespace accel
