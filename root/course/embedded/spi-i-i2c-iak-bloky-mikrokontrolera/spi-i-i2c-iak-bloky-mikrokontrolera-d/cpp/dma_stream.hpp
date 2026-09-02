#pragma once

#include <cstdint>
#include <span>

#include "peripherals.hpp"

namespace mcu {

// Один потік DMA як окремий об'єкт: у C ці ж дії розписано двома функціями
// поруч із драйвером SPI, тут вони належать самому апаратному ресурсу.
class DmaStream {
public:
    enum class Direction { PeriphToMem, MemToPeriph };

    constexpr DmaStream(std::uintptr_t dmaBase, unsigned index, unsigned channel) noexcept
        : dmaBase_{dmaBase}, index_{index}, channel_{channel} {}

    // Джерело чи приймач у пам'яті; порожній span означає "адресу не нарощувати"
    void start(volatile std::uint32_t& peripheralRegister, Direction dir,
               const void* memory, std::size_t count, bool increment,
               bool completeIrq) noexcept;

    void stop() noexcept;
    void clearFlags() noexcept;
    [[nodiscard]] bool transferComplete() const noexcept;
    [[nodiscard]] bool transferError() const noexcept;

private:
    [[nodiscard]] DmaRegs& dma() const noexcept
    {
        return *reinterpret_cast<DmaRegs*>(dmaBase_);
    }
    [[nodiscard]] DmaStreamRegs& regs() const noexcept { return dma().stream[index_]; }
    [[nodiscard]] bool highGroup() const noexcept { return index_ >= 4u; }

    // Прапорці потоків стоять групами по шість бітів зі зсувами 0/6/16/22
    [[nodiscard]] unsigned flagBase() const noexcept
    {
        constexpr unsigned offsets[4] = {0u, 6u, 16u, 22u};
        return offsets[index_ & 3u];
    }

    std::uintptr_t dmaBase_;
    unsigned index_;
    unsigned channel_;
};

}  // namespace mcu
