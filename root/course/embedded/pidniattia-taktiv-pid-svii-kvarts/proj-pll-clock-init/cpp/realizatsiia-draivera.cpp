#include <cstdint>
#include <concepts>

namespace bsp::clock {

/* Типобезпечні структури адрес та бітових полів */
inline constexpr std::uintptr_t rcc_base     = 0x40023800UL;
inline constexpr std::uintptr_t flash_r_base = 0x40023C00UL;

struct RccRegisters {
    volatile std::uint32_t cr;
    volatile std::uint32_t pllcfgr;
    volatile std::uint32_t cfgr;
    volatile std::uint32_t cir;
};

struct FlashRegisters {
    volatile std::uint32_t acr;
};

inline auto& rcc   = *reinterpret_cast<RccRegisters*>(rcc_base);
inline auto& flash = *reinterpret_cast<FlashRegisters*>(flash_r_base);

enum class Status : std::uint8_t {
    Ok = 0,
    HseTimeout,
    PllTimeout,
    SwitchTimeout
};

struct PllConfig {
    std::uint32_t m;
    std::uint32_t n;
    std::uint32_t p;
    std::uint32_t q;
};

class ClockController {
public:
    static constexpr std::uint32_t default_timeout = 0x5000UL;

    /* Розрахунок та встановлення тактування */
    static Status init_8mhz_to_168mhz() noexcept {
        // 1. Встановлюємо 5 тактів очікування Flash + кеш інструкцій та даних
        flash.acr = (5UL << 0) | (1UL << 8) | (1UL << 9) | (1UL << 10);

        // 2. Вмикаємо зовнішній кварц HSE
        rcc.cr |= (1UL << 16);
        if (!wait_for_bit(rcc.cr, (1UL << 17))) {
            return Status::HseTimeout;
        }

        // 3. Дільники шин: AHB /1, APB1 /4, APB2 /2
        rcc.cfgr = (0UL << 4) | (5UL << 10) | (4UL << 13);

        // 4. Запис дільників PLL (M=4, N=168, P=2, Q=7, Джерело=HSE)
        constexpr PllConfig cfg{ .m = 4, .n = 168, .p = 0 /* /2 */, .q = 7 };
        rcc.pllcfgr = (cfg.m << 0) | (cfg.n << 6) | (cfg.p << 16) | (1UL << 22) | (cfg.q << 24);

        // 5. Запуск PLL
        rcc.cr |= (1UL << 24);
        if (!wait_for_bit(rcc.cr, (1UL << 25))) {
            return Status::PllTimeout;
        }

        // 6. Перемикання на вихід PLL
        rcc.cfgr = (rcc.cfgr & ~0x03UL) | 0x02UL;
        if (!wait_for_mask(rcc.cfgr, 0x0CUL, 0x08UL)) {
            return Status::SwitchTimeout;
        }

        // 7. Вмикаємо апаратну безпеку тактування CSS
        rcc.cr |= (1UL << 19);

        return Status::Ok;
    }

private:
    static bool wait_for_bit(const volatile std::uint32_t& reg, std::uint32_t mask) noexcept {
        std::uint32_t t = default_timeout;
        while (!(reg & mask)) {
            if (--t == 0) return false;
        }
        return true;
    }

    static bool wait_for_mask(const volatile std::uint32_t& reg, std::uint32_t mask, std::uint32_t expected) noexcept {
        std::uint32_t t = default_timeout;
        while ((reg & mask) != expected) {
            if (--t == 0) return false;
        }
        return true;
    }
};

} // namespace bsp::clock

extern "C" void NMI_Handler() {
    using namespace bsp::clock;
    if (rcc.cir & (1UL << 7)) { // CSSF прапорець
        // Аварійний перехід у безпечний режим
        rcc.cir |= (1UL << 23); // Скидання CSSC
        while (true) {
            // Очікування перезапуску Watchdog
        }
    }
}
