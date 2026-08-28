// Точна затримка DWT у C++ з використанням constexpr
class DwtTimer {
public:
    static void init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    static void delay_us(uint32_t us) noexcept {
        const uint32_t start = DWT->CYCCNT;
        const uint32_t count = us * (SystemCoreClock / 1000000);
        while ((DWT->CYCCNT - start) < count) {
            // Апаратне очікування
        }
    }
};
