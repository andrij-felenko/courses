// Лікування завислої шини I2C.
//
// Мікроконтролер скинувся сторожовим таймером посеред байта — ведений чип
// лишився з притиснутою до землі лінією SDA й чекає тактів, яких уже ніхто не
// дає. Умову старту в такому стані апаратний блок сформувати не може й мовчить
// назавжди. Виходимо руками: забираємо піни в GPIO, докручуємо до дев'яти
// тактів SCL, доки чип не видавить залишок байта, малюємо СТОП і повертаємо
// піни периферії. Повернення пінів — робота деструктора: воно мусить статися
// на будь-якому шляху виходу.
#include "bus/dispatcher.hpp"

namespace bus {
namespace {

constexpr std::uint32_t kRecoveryPulses = 9;
constexpr std::uint32_t kHalfPeriodUs = 5;      // ~100 кГц: повільно, зате напевно
constexpr std::uint32_t kStretchLimitUs = 1000; // скільки терпимо розтягування такту

void enable_cycle_counter() noexcept
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
#if defined(DWT_LSR_Present_Msk)
    DWT->LAR = 0xC5ACCE55U;   // на Cortex-M7 регістри DWT замкнені до розблокування
#endif
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

// SysTick зайнятий HAL, а заводити таймер заради дев'яти імпульсів безглуздо.
void delay_us(std::uint32_t microseconds) noexcept
{
    const std::uint32_t start = DWT->CYCCNT;
    const std::uint32_t cycles = microseconds * (SystemCoreClock / 1000000U);
    while (DWT->CYCCNT - start < cycles) {
        __NOP();
    }
}

// Піни на час лікування належать нам; деструктор віддає їх назад блокові I2C.
class BorrowedPins {
public:
    explicit BorrowedPins(const I2cLines& lines) noexcept : lines_{lines}
    {
        GPIO_InitTypeDef io{};
        io.Mode = GPIO_MODE_OUTPUT_OD;   // тільки відкритий стік: активної одиниці на шині бути не може
        io.Pull = GPIO_PULLUP;
        io.Speed = GPIO_SPEED_FREQ_LOW;

        io.Pin = lines_.scl_pin;
        HAL_GPIO_Init(lines_.scl_port, &io);
        io.Pin = lines_.sda_pin;
        HAL_GPIO_Init(lines_.sda_port, &io);

        set_scl(true);
        set_sda(true);
        delay_us(kHalfPeriodUs);
    }

    BorrowedPins(const BorrowedPins&) = delete;
    BorrowedPins& operator=(const BorrowedPins&) = delete;

    ~BorrowedPins()
    {
        GPIO_InitTypeDef io{};
        io.Mode = GPIO_MODE_AF_OD;
        io.Pull = GPIO_NOPULL;           // підтяжка стоїть на платі, а не в МК
        io.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
        io.Alternate = lines_.alternate;

        io.Pin = lines_.scl_pin;
        HAL_GPIO_Init(lines_.scl_port, &io);
        io.Pin = lines_.sda_pin;
        HAL_GPIO_Init(lines_.sda_port, &io);
    }

    void set_scl(bool high) const noexcept
    {
        HAL_GPIO_WritePin(lines_.scl_port, lines_.scl_pin, high ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }

    void set_sda(bool high) const noexcept
    {
        HAL_GPIO_WritePin(lines_.sda_port, lines_.sda_pin, high ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }

    [[nodiscard]] bool sda_released() const noexcept
    {
        return HAL_GPIO_ReadPin(lines_.sda_port, lines_.sda_pin) == GPIO_PIN_SET;
    }

    // Такт із урахуванням clock stretching: ведений має право тримати SCL унизу.
    void pulse_scl() const noexcept
    {
        set_scl(false);
        delay_us(kHalfPeriodUs);
        set_scl(true);

        std::uint32_t waited = 0;
        while (HAL_GPIO_ReadPin(lines_.scl_port, lines_.scl_pin) == GPIO_PIN_RESET &&
               waited < kStretchLimitUs) {
            delay_us(1);
            ++waited;
        }
        delay_us(kHalfPeriodUs);
    }

    // Умова СТОП руками: перехід SDA з нуля в одиницю при високому SCL.
    void emit_stop() const noexcept
    {
        set_scl(false);
        set_sda(false);
        delay_us(kHalfPeriodUs);
        set_scl(true);
        delay_us(kHalfPeriodUs);
        set_sda(true);
        delay_us(kHalfPeriodUs);
    }

private:
    I2cLines lines_;
};

}  // namespace

RecoveryOutcome recover_i2c_bus(I2C_HandleTypeDef& i2c, const I2cLines& lines) noexcept
{
    enable_cycle_counter();
    static_cast<void>(HAL_I2C_DeInit(&i2c));   // поки блок живий, піни належать йому

    bool was_stuck = false;
    bool released = false;
    {
        const BorrowedPins pins{lines};

        released = pins.sda_released();
        was_stuck = !released;

        for (std::uint32_t i = 0; i < kRecoveryPulses && !released; ++i) {
            pins.pulse_scl();
            released = pins.sda_released();
        }
        pins.emit_stop();
    }   // тут піни повертаються периферії — і на успіху, і на невдачі

    if (HAL_I2C_Init(&i2c) != HAL_OK) {
        return RecoveryOutcome::ReinitFailed;
    }
    if (!released) {
        return RecoveryOutcome::StillStuck;
    }
    return was_stuck ? RecoveryOutcome::Released : RecoveryOutcome::NotStuck;
}

}  // namespace bus
