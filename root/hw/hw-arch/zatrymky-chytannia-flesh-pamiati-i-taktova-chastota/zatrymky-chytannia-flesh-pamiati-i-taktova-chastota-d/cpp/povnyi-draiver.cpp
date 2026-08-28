#include <cstdint>

namespace mcu::system {

class ClockManager {
private:
    static constexpr uintptr_t FlashAcrAddr = 0x40023C00U;
    static constexpr uintptr_t RccCrAddr    = 0x40023800U;
    static constexpr uintptr_t RccCfgrAddr  = 0x40023808U;

    static constexpr uint32_t Latency5Ws = 5U;
    static constexpr uint32_t Prften     = 1U << 8;
    static constexpr uint32_t Icen       = 1U << 9;
    static constexpr uint32_t Dcen       = 1U << 10;

    static constexpr uint32_t PllOn      = 1U << 24;
    static constexpr uint32_t PllRdy     = 1U << 25;
    static constexpr uint32_t SwPll      = 2U;
    static constexpr uint32_t SwsMask    = 0x0CU;
    static constexpr uint32_t SwsPll     = 0x08U;

    static auto& flash_acr() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(FlashAcrAddr);
    }
    static auto& rcc_cr() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(RccCrAddr);
    }
    static auto& rcc_cfgr() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(RccCfgrAddr);
    }

public:
    [[nodiscard]] static bool scale_up_to_168mhz() noexcept {
        /* 1. Спершу збільшуємо затримку Flash */
        flash_acr() = Latency5Ws | Prften | Icen | Dcen;

        uint32_t timeout = 5000U;
        while ((flash_acr() & 0x0FU) != Latency5Ws) {
            if (--timeout == 0U) return false;
        }

        /* 2. Запуск PLL */
        rcc_cr() |= PllOn;
        timeout = 10000U;
        while (!(rcc_cr() & PllRdy)) {
            if (--timeout == 0U) return false;
        }

        /* 3. Перемикання системного такту */
        auto cfgr = rcc_cfgr();
        cfgr &= ~0x03U;
        cfgr |= SwPll;
        rcc_cfgr() = cfgr;

        timeout = 5000U;
        while ((rcc_cfgr() & SwsMask) != SwsPll) {
            if (--timeout == 0U) return false;
        }

        return true;
    }
};

} // namespace mcu::system
