// SpiFlashDriver.hpp — зовнішня SPI-Flash як клієнт диспетчера живлення.
#pragma once

#include <chrono>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "PowerManager.hpp"

namespace emb::drv {

enum class FlashError : std::uint8_t {
    Busy,          // попередній запис ще триває
    EmptyBuffer,
    TooLarge,      // більше за сторінку
    PageCrossing,  // адреса загорнулася б по колу всередині сторінки
    BusTimeout     // шина не відповіла
};

class SpiFlashDriver final : public pm::IPowerClient {
public:
    static constexpr std::size_t PageSize = 256;

    [[nodiscard]] static SpiFlashDriver& instance() noexcept
    {
        static SpiFlashDriver s_instance;
        return s_instance;
    }

    void init() noexcept;

    // Запис сторінки через DMA: повертається одразу, дані течуть самі.
    [[nodiscard]] std::expected<void, FlashError> writePageAsync(
        std::uint32_t address, std::span<const std::byte> data) noexcept;

    // З головного циклу: знімає блокування, коли мікросхема допекла сторінку.
    void poll() noexcept;

    [[nodiscard]] bool busy() const noexcept { return m_state != State::Idle; }
    [[nodiscard]] std::uint32_t errors() const noexcept { return m_errors; }

    // --- IPowerClient ---
    [[nodiscard]] std::string_view name() const noexcept override { return "SPI-Flash"; }
    [[nodiscard]] bool preSleep(pm::Mode targetMode) noexcept override;
    void postWakeup(pm::Mode fromMode) noexcept override;

    void onDmaIrq() noexcept;

private:
    SpiFlashDriver() noexcept = default;

    enum class State : std::uint8_t {
        Idle = 0,  // мікросхема вільна, сон дозволено
        Dma,       // дані течуть у SPI через DMA
        Program    // байти віддані, мікросхема пече сторінку сама
    };

    [[nodiscard]] bool xfer(std::byte out, std::byte* in = nullptr) noexcept;
    void drainRx() noexcept;
    void configurePins() noexcept;
    void abort() noexcept;
    [[nodiscard]] std::expected<std::byte, FlashError> readStatus() noexcept;

    volatile State m_state{State::Idle};
    std::uint32_t  m_errors{0};
    std::uint32_t  m_savedModer{0};
    bool           m_deepPowerDown{false};
    // Блокування живе довше за виклик: його бере writePageAsync, а віддає
    // poll(), коли мікросхема справді закінчила запис.
    pm::ScopedPowerLock* m_lock{nullptr};
};

} // namespace emb::drv
