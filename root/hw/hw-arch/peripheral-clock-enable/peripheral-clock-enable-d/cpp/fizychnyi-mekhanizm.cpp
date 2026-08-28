#include <cstdint>

struct simulated_rcc {
    volatile std::uint32_t apb1rstr{0};
    volatile std::uint32_t apb1enr{0};
};

class peripheral_reset_controller {
private:
    static inline simulated_rcc rcc_{};
    static constexpr std::uint32_t i2c1_bit{1U << 21};

public:
    static void reset_i2c1() noexcept {
        // 1. Гарантувати активність шинного такту
        rcc_.apb1enr |= i2c1_bit;
        [[maybe_unused]] volatile auto b1 = rcc_.apb1enr;

        // 2. Ініціювати скидання
        rcc_.apb1rstr |= i2c1_bit;
        [[maybe_unused]] volatile auto b2 = rcc_.apb1rstr;

        // 3. Затримка стабілізації
        for (volatile int i = 0; i < 10; ++i) {
            asm volatile("nop");
        }

        // 4. Завершити скидання
        rcc_.apb1rstr &= ~i2c1_bit;
        [[maybe_unused]] volatile auto b3 = rcc_.apb1rstr;
    }
};
