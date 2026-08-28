// ============================================================================
// ФАЙЛ: hal_event_types.hpp (C++20)
// ============================================================================
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>

namespace hal {

enum class PeripheralId : std::uint8_t {
    Uart1 = 0,
    Uart2 = 1,
    Spi1  = 2,
    Dma1  = 3,
    Gpio  = 4,
    Timer = 5
};

enum class EventKind : std::uint8_t {
    RxReady       = 0x01,
    TxComplete    = 0x02,
    TransferDone  = 0x03,
    PinEdge       = 0x04,
    PeriodElapsed = 0x05,
    ErrorOverrun  = 0x0E,
    ErrorHardware = 0x0F
};

struct Event {
    PeripheralId            periph;
    EventKind               kind;
    std::uint32_t           timestamp_us;
    std::span<const std::byte> payload;
    std::uint32_t           flags;
};

} // namespace hal
