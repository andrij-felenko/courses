// Шаблонний клас драйвера bit-bang із нульовими накладними витратами
template <uintptr_t PortBsrrAddr, uintptr_t PortIdrAddr, uint8_t SclkPin, uint8_t DataPin>
class BitBangDriver {
public:
    static constexpr uint32_t SCLK_SET = (1UL << SclkPin);
    static constexpr uint32_t SCLK_CLR = (1UL << (SclkPin + 16));
    static constexpr uint32_t DATA_SET = (1UL << DataPin);
    static constexpr uint32_t DATA_CLR = (1UL << (DataPin + 16));

    static bitbang_status_t init() {
        bsrr() = SCLK_CLR; // SCLK у низькому стані спокою
        bsrr() = DATA_SET; // Лінія даних підтягнута у високий стан
        return BITBANG_OK;
    }

    template <uint32_t SetupCycles, uint32_t HalfClkCycles, uint32_t HoldCycles>
    static bitbang_status_t transfer_byte(uint8_t tx_byte, uint8_t &rx_byte) {
        uint8_t received = 0;
        for (int i = 7; i >= 0; --i) {
            // Встановлення біта даних на шині
            if (tx_byte & (1 << i)) {
                bsrr() = DATA_SET;
            } else {
                bsrr() = DATA_CLR;
            }
            wait_cycles<SetupCycles>();

            // Активний перепад такту
            bsrr() = SCLK_SET;
            wait_cycles<HalfClkCycles / 2>();

            // Зчитування стану вхідної лінії з регістра IDR
            received = static_cast<uint8_t>((received << 1) | ((idr() & DATA_SET) ? 1 : 0));
            wait_cycles<HalfClkCycles / 2>();

            // Повернення тактової лінії у стан спокою
            bsrr() = SCLK_CLR;
            wait_cycles<HoldCycles>();
        }
        rx_byte = received;
        return BITBANG_OK;
    }

private:
    static volatile uint32_t& bsrr() {
        return *reinterpret_cast<volatile uint32_t*>(PortBsrrAddr);
    }
    static volatile uint32_t& idr() {
        return *reinterpret_cast<volatile uint32_t*>(PortIdrAddr);
    }

    template <uint32_t N>
    static inline void wait_cycles() {
        if constexpr (N > 0) {
            __asm__ volatile ("nop");
            wait_cycles<N - 1>();
        }
    }
};
