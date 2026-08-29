// registers.hpp — регістрова карта чипа як типи, а не як #define.
//
// Маска й зсув кожного поля живуть у типі Field<>, тому вираз
// «покласти код частоти в біти [7:4] регістру CTRL1» перевіряється
// компілятором, а не уважністю читача.
#pragma once

#include <cstdint>

namespace accel::regs {

enum class Reg : std::uint8_t {
    WhoAmI   = 0x0F,
    Ctrl1    = 0x20, // ODR, режим низького споживання, дозвіл осей
    Ctrl3    = 0x22, // маршрутизація переривань на вивід INT1
    Ctrl4    = 0x23, // BDU, діапазон повної шкали, роздільність
    Ctrl5    = 0x24, // вмикання апаратного буфера
    Status   = 0x27,
    OutXL    = 0x28, // початок блоку X/Y/Z — шість байтів
    FifoCtrl = 0x2E,
    FifoSrc  = 0x2F
};

[[nodiscard]] constexpr std::uint8_t raw(Reg reg) noexcept
{
    return static_cast<std::uint8_t>(reg);
}

// Старший біт адреси вмикає автоінкремент усередині транзакції.
inline constexpr std::uint8_t kAutoIncrement = 0x80;
inline constexpr std::uint8_t kWhoAmIValue   = 0x33;
inline constexpr std::uint8_t kFifoDepth     = 32;
inline constexpr std::uint8_t kSampleBytes   = 6;

// Бітове поле: маска, зсув і безпечні операції над ними.
template <std::uint8_t MaskValue, std::uint8_t ShiftValue>
struct Field {
    static constexpr std::uint8_t mask = MaskValue;
    static constexpr std::uint8_t shift = ShiftValue;

    [[nodiscard]] static constexpr bool fits(std::uint8_t value) noexcept
    {
        const auto placed = static_cast<unsigned>(value) << shift;
        return (placed & ~static_cast<unsigned>(mask)) == 0U;
    }

    [[nodiscard]] static constexpr std::uint8_t insert(std::uint8_t reg, std::uint8_t value) noexcept
    {
        const auto placed = static_cast<std::uint8_t>((static_cast<unsigned>(value) << shift) & mask);
        return static_cast<std::uint8_t>((reg & static_cast<std::uint8_t>(~mask)) | placed);
    }

    [[nodiscard]] static constexpr std::uint8_t extract(std::uint8_t reg) noexcept
    {
        return static_cast<std::uint8_t>((reg & mask) >> shift);
    }
};

// CTRL_REG1
using OdrField = Field<0xF0, 4>;
inline constexpr std::uint8_t kCtrl1LowPower = 1U << 3;
inline constexpr std::uint8_t kCtrl1AxesXyz  = 0x07;

// CTRL_REG3 — що саме виводиться на INT1
inline constexpr std::uint8_t kInt1DataReady = 1U << 4;
inline constexpr std::uint8_t kInt1Overrun   = 1U << 1;
inline constexpr std::uint8_t kInt1Watermark = 1U << 2;

// CTRL_REG4
inline constexpr std::uint8_t kCtrl4Bdu           = 1U << 7;
inline constexpr std::uint8_t kCtrl4HighResolution = 1U << 3;
using FullScaleField = Field<0x30, 4>;

// CTRL_REG5
inline constexpr std::uint8_t kCtrl5FifoEnable = 1U << 6;

// STATUS
inline constexpr std::uint8_t kStatusZyxDataReady = 1U << 3;
inline constexpr std::uint8_t kStatusZyxOverrun   = 1U << 7;

// FIFO_CTRL / FIFO_SRC
using FifoModeField = Field<0xC0, 6>;
using WatermarkField = Field<0x1F, 0>;
inline constexpr std::uint8_t kFifoSrcWatermark = 1U << 7;
inline constexpr std::uint8_t kFifoSrcOverrun   = 1U << 6;
inline constexpr std::uint8_t kFifoSrcEmpty     = 1U << 5;
inline constexpr std::uint8_t kFifoSrcLevelMask = 0x1F;

// Чи має регістр тіньову копію в ОЗП. Читати з чипа заради Read-Modify-Write
// не можна: STATUS і FIFO_SRC скидають прапорці самим фактом читання.
[[nodiscard]] constexpr bool isShadowed(Reg reg) noexcept
{
    switch (reg) {
    case Reg::Ctrl1:
    case Reg::Ctrl3:
    case Reg::Ctrl4:
    case Reg::Ctrl5:
    case Reg::FifoCtrl:
        return true;
    default:
        return false;
    }
}

} // namespace accel::regs
