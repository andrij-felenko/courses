#include <cstdint>
#include <expected>
#include <concepts>

namespace stm32::rcc {

/* Базові адреси апаратних блоків */
inline constexpr std::uintptr_t rcc_base   = 0x40023800U;
inline constexpr std::uintptr_t flash_base = 0x40023C00U;
inline constexpr std::uintptr_t pwr_base   = 0x40007000U;

/* Реєстрові структури */
struct RccRegs {
    volatile std::uint32_t CR;
    volatile std::uint32_t PLLCFGR;
    volatile std::uint32_t CFGR;
    volatile std::uint32_t CIR;
    volatile std::uint32_t AHB1RSTR;
    volatile std::uint32_t AHB2RSTR;
    volatile std::uint32_t AHB3RSTR;
    std::uint32_t          RESERVED0;
    volatile std::uint32_t APB1RSTR;
    volatile std::uint32_t APB2RSTR;
    std::uint32_t          RESERVED1[2];
    volatile std::uint32_t AHB1ENR;
    volatile std::uint32_t AHB2ENR;
    volatile std::uint32_t AHB3ENR;
    std::uint32_t          RESERVED2;
    volatile std::uint32_t APB1ENR;
    volatile std::uint32_t APB2ENR;
};

struct FlashRegs {
    volatile std::uint32_t ACR;
    volatile std::uint32_t KEYR;
    volatile std::uint32_t OPTKEYR;
    volatile std::uint32_t SR;
    volatile std::uint32_t CR;
    volatile std::uint32_t OPTCR;
};

struct PwrRegs {
    volatile std::uint32_t CR;
    volatile std::uint32_t CSR;
};

/* Строго типізовані коди помилок тактування */
enum class ClockError : std::uint8_t {
    HseTimeout,
    PllTimeout,
    SwitchTimeout,
    InvalidConfiguration
};

/* Константи перевірки меж PLL під час компіляції */
struct PllConfig {
    std::uint32_t hse_hz;
    std::uint32_t m;
    std::uint32_t n;
    std::uint32_t p;
    std::uint32_t q;

    [[nodiscard]] constexpr bool isValid() const noexcept {
        if (m < 2 || m > 63) return false;
        if (n < 50 || n > 432) return false;
        if (p != 2 && p != 4 && p != 6 && p != 8) return false;
        if (q < 2 || q > 15) return false;

        const std::uint32_t vco_in = hse_hz / m;
        if (vco_in < 1000000U || vco_in > 2000000U) return false;

        const std::uint32_t vco_out = vco_in * n;
        if (vco_out < 100000000U || vco_out > 432000000U) return false;

        return true;
    }

    [[nodiscard]] constexpr std::uint32_t sysclk() const noexcept {
        return ((hse_hz / m) * n) / p;
    }

    [[nodiscard]] constexpr std::uint32_t usbClock() const noexcept {
        return ((hse_hz / m) * n) / q;
    }
};

/* Шаблонний клас ініціалізації дерева тактування */
template <PllConfig Config>
class ClockController {
    static_assert(Config.isValid(), "Некоректні параметри PLL: порушено фізичні межі VCO!");
    static_assert(Config.sysclk() <= 168000000U, "Перевищено максимальну частоту ядра 168 МГц!");
    static_assert(Config.usbClock() == 48000000U, "Частота USB повинна дорівнювати строго 48 МГц!");

public:
    [[nodiscard]] static auto initialize() noexcept -> std::expected<void, ClockError> {
        auto* const rcc   = reinterpret_cast<RccRegs*>(rcc_base);
        auto* const flash = reinterpret_cast<FlashRegs*>(flash_base);
        auto* const pwr   = reinterpret_cast<PwrRegs*>(pwr_base);

        /* 1. Запуск кварцу HSE */
        rcc->CR |= (1U << 16); // HSEON

        std::uint32_t timeout = 200000U;
        while ((rcc->CR & (1U << 17)) == 0U) { // HSERDY
            if (--timeout == 0U) {
                return std::unexpected(ClockError::HseTimeout);
            }
        }

        /* 2. Живлення регулятора ядра в режимі Scale 1 */
        rcc->APB1ENR |= (1U << 28); // PWREN
        pwr->CR |= (1U << 14);      // VOS Scale 1

        /* 3. Встановлення Flash Latency: 5 WS для 168 МГц + буферизація */
        constexpr std::uint32_t flash_acr_val = (1U << 9) |  // ICEN (Instruction Cache)
                                                (1U << 10) | // DCEN (Data Cache)
                                                (1U << 8) |  // PRFTEN (Prefetch)
                                                (5U << 0);   // 5 Wait States
        flash->ACR = flash_acr_val;

        /* 4. Конфігурація дільників шин: AHB = /1, APB1 = /4, APB2 = /2 */
        constexpr std::uint32_t hpre_div1  = (0U << 4);
        constexpr std::uint32_t ppre1_div4 = (5U << 10);
        constexpr std::uint32_t ppre2_div2 = (4U << 13);

        rcc->CFGR &= ~((0x0FU << 4) | (7U << 10) | (7U << 13));
        rcc->CFGR |= (hpre_div1 | ppre1_div4 | ppre2_div2);

        /* 5. Запис перевірених під час компіляції коефіцієнтів PLL */
        constexpr std::uint32_t p_code = (Config.p / 2U) - 1U; // 2->00b, 4->01b, 6->10b, 8->11b
        rcc->PLLCFGR = (Config.m << 0) |
                       (Config.n << 6) |
                       (p_code << 16) |
                       (1U << 22) | // PLLSRC_HSE
                       (Config.q << 24);

        /* 6. Запуск PLL */
        rcc->CR |= (1U << 24); // PLLON

        timeout = 200000U;
        while ((rcc->CR & (1U << 25)) == 0U) { // PLLRDY
            if (--timeout == 0U) {
                return std::unexpected(ClockError::PllTimeout);
            }
        }

        /* 7. Перемикання джерела SYSCLK на PLL */
        rcc->CFGR &= ~3U;
        rcc->CFGR |= 2U; // SW = PLL

        /* 8. Очікування підтвердження комутації апаратурою */
        timeout = 200000U;
        while ((rcc->CFGR & (3U << 2)) != (2U << 2)) { // SWS == PLL
            if (--timeout == 0U) {
                return std::unexpected(ClockError::SwitchTimeout);
            }
        }

        /* 9. Активація захисту CSS від зриву кварцу */
        rcc->CR |= (1U << 19); // CSSON

        return {};
    }
};

} // namespace stm32::rcc

/* Приклад використання в коді застосунку */
extern "C" void SystemInit_Custom(void) {
    constexpr stm32::rcc::PllConfig config_168mhz{
        .hse_hz = 8000000U,
        .m = 8U,
        .n = 336U,
        .p = 2U,
        .q = 7U
    };

    const auto result = stm32::rcc::ClockController<config_168mhz>::initialize();
    if (!result.has_value()) {
        /* Обробка аварійної ситуації: залишаємося на HSI 16 МГц */
        while (true) {
            // Безпечний аварійний цикл
        }
    }
}
