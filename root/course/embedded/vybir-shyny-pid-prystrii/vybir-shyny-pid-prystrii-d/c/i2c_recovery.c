/* Лікування завислої шини I2C.
 *
 * Якщо мікроконтролер скинувся сторожовим таймером посеред байта, ведений чип
 * лишається з притиснутою до землі лінією SDA й чекає на такти, яких уже ніхто
 * не дає. Умову старту в такому стані сформувати неможливо — апаратний блок
 * мовчить назавжди. Виходимо руками: забираємо піни в GPIO, докручуємо до
 * дев'яти тактів SCL, доки чип не видавить залишок байта й не відпустить SDA,
 * після чого малюємо умову СТОП і повертаємо піни периферії.
 */
#include "bus.h"

#define I2C_RECOVERY_PULSES     9u
#define I2C_HALF_PERIOD_US      5u    /* ~100 кГц: повільно, зате гарантовано */
#define I2C_STRETCH_LIMIT_US 1000u    /* скільки терпимо розтягування такту веденим */

/* Мікросекундна затримка на лічильнику циклів ядра: SysTick тут зайнятий HAL,
 * а таймер заводити заради дев'яти імпульсів безглуздо. */
static void cycle_counter_enable(void)
{
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
#if defined(DWT_LSR_Present_Msk)
    DWT->LAR = 0xC5ACCE55u;   /* на Cortex-M7 регістри DWT замкнені до розблокування */
#endif
    DWT->CYCCNT = 0u;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

static void delay_us(uint32_t us)
{
    uint32_t start  = DWT->CYCCNT;
    uint32_t cycles = us * (SystemCoreClock / 1000000u);
    while ((DWT->CYCCNT - start) < cycles) {
        __NOP();
    }
}

static void pins_to_gpio(const i2c_lines_t *lines)
{
    GPIO_InitTypeDef io = {0};

    io.Mode  = GPIO_MODE_OUTPUT_OD;   /* саме відкритий стік: активної одиниці на шині бути не може */
    io.Pull  = GPIO_PULLUP;
    io.Speed = GPIO_SPEED_FREQ_LOW;

    io.Pin = lines->scl_pin;
    HAL_GPIO_Init(lines->scl_port, &io);
    io.Pin = lines->sda_pin;
    HAL_GPIO_Init(lines->sda_port, &io);

    HAL_GPIO_WritePin(lines->scl_port, lines->scl_pin, GPIO_PIN_SET);
    HAL_GPIO_WritePin(lines->sda_port, lines->sda_pin, GPIO_PIN_SET);
}

static void pins_to_peripheral(const i2c_lines_t *lines)
{
    GPIO_InitTypeDef io = {0};

    io.Mode      = GPIO_MODE_AF_OD;
    io.Pull      = GPIO_NOPULL;       /* підтяжка на платі, а не всередині МК */
    io.Speed     = GPIO_SPEED_FREQ_VERY_HIGH;
    io.Alternate = lines->alternate;

    io.Pin = lines->scl_pin;
    HAL_GPIO_Init(lines->scl_port, &io);
    io.Pin = lines->sda_pin;
    HAL_GPIO_Init(lines->sda_port, &io);
}

static bool sda_released(const i2c_lines_t *lines)
{
    return HAL_GPIO_ReadPin(lines->sda_port, lines->sda_pin) == GPIO_PIN_SET;
}

/* Такт із урахуванням clock stretching: ведений має право тримати SCL унизу. */
static void scl_pulse(const i2c_lines_t *lines)
{
    HAL_GPIO_WritePin(lines->scl_port, lines->scl_pin, GPIO_PIN_RESET);
    delay_us(I2C_HALF_PERIOD_US);
    HAL_GPIO_WritePin(lines->scl_port, lines->scl_pin, GPIO_PIN_SET);

    uint32_t waited = 0u;
    while ((HAL_GPIO_ReadPin(lines->scl_port, lines->scl_pin) == GPIO_PIN_RESET) &&
           (waited < I2C_STRETCH_LIMIT_US)) {
        delay_us(1u);
        waited++;
    }
    delay_us(I2C_HALF_PERIOD_US);
}

/* Умова СТОП руками: перехід SDA з нуля в одиницю при високому SCL. */
static void emit_stop(const i2c_lines_t *lines)
{
    HAL_GPIO_WritePin(lines->scl_port, lines->scl_pin, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(lines->sda_port, lines->sda_pin, GPIO_PIN_RESET);
    delay_us(I2C_HALF_PERIOD_US);
    HAL_GPIO_WritePin(lines->scl_port, lines->scl_pin, GPIO_PIN_SET);
    delay_us(I2C_HALF_PERIOD_US);
    HAL_GPIO_WritePin(lines->sda_port, lines->sda_pin, GPIO_PIN_SET);
    delay_us(I2C_HALF_PERIOD_US);
}

bool i2c_bus_recover(I2C_HandleTypeDef *i2c, const i2c_lines_t *lines)
{
    cycle_counter_enable();

    (void)HAL_I2C_DeInit(i2c);   /* поки блок живий, піни йому й належать */
    pins_to_gpio(lines);
    delay_us(I2C_HALF_PERIOD_US);

    bool released = sda_released(lines);
    for (uint32_t i = 0u; (i < I2C_RECOVERY_PULSES) && !released; ++i) {
        scl_pulse(lines);
        released = sda_released(lines);
    }

    emit_stop(lines);
    pins_to_peripheral(lines);

    if (HAL_I2C_Init(i2c) != HAL_OK) {
        return false;
    }
    return released;
}
