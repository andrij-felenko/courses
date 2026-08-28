#include <concepts>
#include <cstdint>
#include <span>

namespace embedded::hw {

/* Конфігураційні константи для шини I2C STM32F103 */
struct I2cBusConfig {
    static constexpr uint32_t Apb1ClockHz = 36'000'000U;
    static constexpr uint32_t BusSpeedHz  = 100'000U;
    static constexpr uint32_t DelayCount  = 200U;
};

enum class RecoveryResult : uint8_t {
    Success,
    BusLineStuckLow,
    HardwareFault
};

class I2c1BusRecovery {
public:
    explicit I2c1BusRecovery() = default;

    /* Заборона копіювання апаратного драйвера */
    I2c1BusRecovery(const I2c1BusRecovery&) = delete;
    I2c1BusRecovery& operator=(const I2c1BusRecovery&) = delete;

    [[nodiscard]] static RecoveryResult recover_and_initialize() noexcept {
        reset_peripheral_rcc();
        enable_clocks();
        configure_pins_as_gpio();

        release_lines_high();
        delay(I2cBusConfig::DelayCount);

        /* Вибивання дев'яти тактів для звільнення SDA веденим чипом */
        for (uint8_t cycle = 0; cycle < 9; ++cycle) {
            if (is_sda_high()) {
                break;
            }
            toggle_scl_pulse();
        }

        generate_stop_condition();

        /* Перевірка стану ліній: якщо хоча б одна в нулі — шина фізично пошкоджена */
        if (!is_scl_high() || !is_sda_high()) {
            return RecoveryResult::BusLineStuckLow;
        }

        configure_pins_as_alternate_function();
        initialize_i2c_registers();

        return RecoveryResult::Success;
    }

private:
    static void delay(volatile uint32_t count) noexcept {
        while (count--) {
            asm volatile("nop");
        }
    }

    static void reset_peripheral_rcc() noexcept {
        RCC->APB1RSTR |= RCC_APB1RSTR_I2C1RST;
        delay(100);
        RCC->APB1RSTR &= ~RCC_APB1RSTR_I2C1RST;
    }

    static void enable_clocks() noexcept {
        RCC->APB2ENR |= RCC_APB2ENR_IOPBEN;
        RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    }

    static void configure_pins_as_gpio() noexcept {
        GPIOB->CRL &= ~(0xFF000000U);
        GPIOB->CRL |= (0x77000000U); /* Open-Drain Output 10 MHz */
    }

    static void configure_pins_as_alternate_function() noexcept {
        GPIOB->CRL &= ~(0xFF000000U);
        GPIOB->CRL |= (0xBB000000U); /* Alternate Function Open-Drain */
    }

    static void release_lines_high() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BS6 | GPIO_BSRR_BS7;
    }

    static bool is_sda_high() noexcept {
        return (GPIOB->IDR & GPIO_IDR_IDR7) != 0;
    }

    static bool is_scl_high() noexcept {
        return (GPIOB->IDR & GPIO_IDR_IDR6) != 0;
    }

    static void toggle_scl_pulse() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BR6; /* SCL -> 0 */
        delay(I2cBusConfig::DelayCount);
        GPIOB->BSRR = GPIO_BSRR_BS6; /* SCL -> 1 */
        delay(I2cBusConfig::DelayCount);
    }

    static void generate_stop_condition() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BR7; /* SDA -> 0 */
        delay(I2cBusConfig::DelayCount);
        GPIOB->BSRR = GPIO_BSRR_BS6; /* SCL -> 1 */
        delay(I2cBusConfig::DelayCount);
        GPIOB->BSRR = GPIO_BSRR_BS7; /* SDA -> 1 (STOP) */
        delay(I2cBusConfig::DelayCount);
    }

    static void initialize_i2c_registers() noexcept {
        I2C1->CR1 = I2C_CR1_SWRST;
        delay(50);
        I2C1->CR1 = 0;

        constexpr uint32_t freq_mhz = I2cBusConfig::Apb1ClockHz / 1'000'000U;
        constexpr uint32_t ccr_val  = I2cBusConfig::Apb1ClockHz / (2U * I2cBusConfig::BusSpeedHz);

        I2C1->CR2 = freq_mhz;
        I2C1->CCR = ccr_val;
        I2C1->TRISE = freq_mhz + 1U;
        I2C1->CR1 |= I2C_CR1_PE;
    }
};

} // namespace embedded::hw
