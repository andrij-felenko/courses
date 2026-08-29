// Регістрова карта LIS2DH12 (ST, DocID027112; самотест — AN5005).
// Деталь реалізації: прикладний код включає лише sensor.hpp.
#pragma once

#include <cstdint>

namespace chip::reg {

enum class Reg : std::uint8_t {
    WhoAmI   = 0x0F,
    Ctrl1    = 0x20,
    Ctrl2    = 0x21,
    Ctrl3    = 0x22,
    Ctrl4    = 0x23,
    Ctrl5    = 0x24,
    Ctrl6    = 0x25,
    Status   = 0x27,
    OutXL    = 0x28,
    FifoCtrl = 0x2E,
    FifoSrc  = 0x2F,
};

inline constexpr std::uint8_t kWhoAmIValue = 0x33;

/// I2C сам автоінкремента не робить: без старшого біта пакетне читання
/// шість разів поверне той самий OUT_X_L.
[[nodiscard]] constexpr std::uint8_t autoIncrement(Reg r) noexcept
{
    return static_cast<std::uint8_t>(static_cast<std::uint8_t>(r) | 0x80U);
}

[[nodiscard]] constexpr std::uint8_t raw(Reg r) noexcept
{
    return static_cast<std::uint8_t>(r);
}

// CTRL_REG1: ODR[7:4] | LPen[3] | Zen[2] | Yen[1] | Xen[0]
inline constexpr std::uint8_t kCtrl1XyzEnable = 0x07;
inline constexpr std::uint8_t kCtrl1OdrMask   = 0xF0;
inline constexpr unsigned     kCtrl1OdrShift  = 4;
inline constexpr std::uint8_t kCtrl1ResetValue = 0x07;

// CTRL_REG4: BDU[7] | BLE[6] | FS[5:4] | HR[3] | ST[2:1] | SIM[0]
inline constexpr std::uint8_t kCtrl4Bdu     = 0x80;
inline constexpr std::uint8_t kCtrl4FsMask  = 0x30;
inline constexpr unsigned     kCtrl4FsShift = 4;
inline constexpr std::uint8_t kCtrl4HighRes = 0x08;
inline constexpr std::uint8_t kCtrl4SelfTest0 = 0x02;

// CTRL_REG5: BOOT[7] | FIFO_EN[6]
inline constexpr std::uint8_t kCtrl5Boot   = 0x80;
inline constexpr std::uint8_t kCtrl5FifoEn = 0x40;

// STATUS_REG
inline constexpr std::uint8_t kStatusZyxDataReady = 0x08;

// FIFO_CTRL_REG: FM[7:6]
inline constexpr std::uint8_t kFifoModeBypass = 0x00;
inline constexpr std::uint8_t kFifoModeStream = 0x80;

// FIFO_SRC_REG: WTM[7] | OVRN[6] | EMPTY[5] | FSS[4:0]
inline constexpr std::uint8_t kFifoSrcWatermark = 0x80;
inline constexpr std::uint8_t kFifoSrcOverrun   = 0x40;
inline constexpr std::uint8_t kFifoSrcCountMask = 0x1F;

} // namespace chip::reg
