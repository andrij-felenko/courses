#include "dma_stream.hpp"

namespace mcu {

void DmaStream::start(volatile std::uint32_t& peripheralRegister, Direction dir,
                      const void* memory, std::size_t count, bool increment,
                      bool completeIrq) noexcept
{
    stop();
    clearFlags();

    regs().par = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(&peripheralRegister));
    regs().m0ar = static_cast<std::uint32_t>(reinterpret_cast<std::uintptr_t>(memory));
    regs().ndtr = static_cast<std::uint32_t>(count);

    std::uint32_t cr = (channel_ << dma_cr::channelPos) | dma_cr::priorityHigh
                     | dma_cr::transferErrorIrq;
    if (dir == Direction::MemToPeriph) {
        cr |= dma_cr::memToPeriph;
    }
    if (increment) {
        cr |= dma_cr::memIncrement;
    }
    if (completeIrq) {
        cr |= dma_cr::transferCompleteIrq;
    }

    regs().cr = cr;
    regs().cr |= dma_cr::enable;
}

void DmaStream::stop() noexcept
{
    regs().cr = 0u;
    // Потік гасне не миттєво: апаратура сама зніме EN, коли доб'є поточне слово
    while (regs().cr & dma_cr::enable) {
    }
}

void DmaStream::clearFlags() noexcept
{
    const std::uint32_t mask = 0x3Fu << flagBase();
    if (highGroup()) {
        dma().hifcr = mask;
    } else {
        dma().lifcr = mask;
    }
}

bool DmaStream::transferComplete() const noexcept
{
    const std::uint32_t isr = highGroup() ? dma().hisr : dma().lisr;
    return (isr & (1u << (flagBase() + 5u))) != 0u;
}

bool DmaStream::transferError() const noexcept
{
    const std::uint32_t isr = highGroup() ? dma().hisr : dma().lisr;
    return (isr & (1u << (flagBase() + 3u))) != 0u;
}

}  // namespace mcu
