#pragma once

// Напівдуплексний канал RS-485 і ведений Modbus RTU в одному класі: кадр
// відділяється апаратною паузою t3.5, лінія DE знімається строго по TC.

#include <array>
#include <cstdint>

#include "mcu.hpp"
#include "telemetry.hpp"

namespace node {

class ModbusSlave {
public:
    using Events = EventQueue<16>;

    static constexpr std::uint8_t  kNodeId = 0x01;
    static constexpr std::uint32_t kBaud   = 19'200;

    explicit ModbusSlave(Events& events) noexcept : events_{events} {}

    void begin(std::uint32_t kernelClkHz) noexcept;

    // Викликається з USART1_IRQHandler.
    void handleIrq() noexcept;

    // Розбирає зібраний кадр і, якщо він наш, відправляє відповідь.
    void service(const Record& last) noexcept;

    [[nodiscard]] bool txBusy() const noexcept { return txBusy_; }
    [[nodiscard]] bool frameWaiting() const noexcept { return frameReady_; }
    [[nodiscard]] bool masterActive() const noexcept {
        return masterSeen_ && !mcu::time::elapsed(lastPollMs_, kMasterWindowMs);
    }

private:
    static constexpr std::size_t kRxSize = 64;
    static constexpr std::size_t kTxSize = 40;
    static constexpr std::uint8_t kFuncReadHolding = 0x03;
    static constexpr std::uint8_t kExcIllegalFunction = 0x01;

    void send(std::span<const std::byte> frame) noexcept;

    Events& events_;
    mcu::Pin de_{GPIOA, 8};

    std::array<std::byte, kRxSize> rx_{};
    std::array<std::byte, kRxSize> frame_{};
    std::array<std::byte, kTxSize> tx_{};

    volatile std::size_t rxLen_{0};
    volatile std::size_t frameLen_{0};
    volatile std::size_t txLen_{0};
    volatile std::size_t txPos_{0};
    volatile bool frameReady_{false};
    volatile bool txBusy_{false};

    std::uint32_t overruns_{0};
    std::uint32_t lastPollMs_{0};
    bool masterSeen_{false};
};

}  // namespace node
