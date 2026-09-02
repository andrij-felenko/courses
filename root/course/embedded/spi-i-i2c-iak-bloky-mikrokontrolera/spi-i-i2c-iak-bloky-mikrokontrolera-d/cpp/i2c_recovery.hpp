#pragma once

#include <cstdint>
#include <expected>

namespace drv {

enum class BusState : std::uint8_t {
    AlreadyFree,  // SDA була високою — лікувати нічого
    Released      // ведений відпустив лінію після досланих тактів
};

// Шина лишилася притиснутою до землі: коротке замикання або мертвий чіп
enum class RecoveryError : std::uint8_t { StuckLow };

// Викликати ДО ввімкнення блока I2C, при кожному старті системи
[[nodiscard]] std::expected<BusState, RecoveryError> recoverI2c1Bus() noexcept;

}  // namespace drv
