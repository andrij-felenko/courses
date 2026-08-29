/* ports/stm32f4/stm32_hal_i2c.c — реалізація шини I2C для STM32F401.
 * Це ЄДИНЕ місце у всьому проєкті, де згадано регістри контролера I2C.
 * Драйвери BME280 і ADXL345 про цей файл не знають нічого — вони бачать
 * лише таблицю операцій, яку він заповнює наприкінці. */
#include "hal/hal_i2c_ops.h"
#include "hal/hal_time.h"
#include "ports/stm32f4/stm32_port.h"

#include "stm32f4xx.h"

#define I2C_TIMEOUT_MS        10u
#define I2C_APB1_CLOCK_MHZ    42u
#define I2C_CCR_100KHZ        210u  /* 42 МГц / (2 × 100 кГц) */
#define I2C_TRISE_100KHZ      43u   /* 1000 нс × 42 МГц + 1 */

typedef struct {
    I2C_TypeDef *regs;
} stm32_i2c_ctx_t;

static stm32_i2c_ctx_t g_i2c1_ctx = { I2C1 };

/* Очікування прапорця в SR1 з обмеженням у часі. Нескінченне while(!flag)
 * у польових умовах перетворює пристрій на цеглину: досить одного
 * електростатичного розряду, щоб лінія SDA залипла в нулі. */
static hal_i2c_status_t wait_sr1(I2C_TypeDef *regs, uint32_t mask)
{
    const uint32_t started = hal_time_now_ms();
    while ((regs->SR1 & mask) == 0u) {
        if (regs->SR1 & I2C_SR1_AF) {
            regs->SR1 &= ~I2C_SR1_AF;
            regs->CR1 |= I2C_CR1_STOP;
            return HAL_I2C_ERR_NACK;
        }
        if (regs->SR1 & (I2C_SR1_BERR | I2C_SR1_ARLO | I2C_SR1_OVR)) {
            regs->SR1 &= ~(I2C_SR1_BERR | I2C_SR1_ARLO | I2C_SR1_OVR);
            regs->CR1 |= I2C_CR1_STOP;
            return HAL_I2C_ERR_BUS;
        }
        if (hal_time_elapsed_ms(started) > I2C_TIMEOUT_MS) {
            regs->CR1 |= I2C_CR1_STOP;
            return HAL_I2C_ERR_TIMEOUT;
        }
    }
    return HAL_I2C_OK;
}

static hal_i2c_status_t wait_not_busy(I2C_TypeDef *regs)
{
    const uint32_t started = hal_time_now_ms();
    while (regs->SR2 & I2C_SR2_BUSY) {
        if (hal_time_elapsed_ms(started) > I2C_TIMEOUT_MS) {
            return HAL_I2C_ERR_BUS;
        }
    }
    return HAL_I2C_OK;
}

static void clear_addr(I2C_TypeDef *regs)
{
    /* Прапорець ADDR скидається читанням SR1, а потім SR2 — саме в такому
     * порядку. Пропущене читання лишає контролер у розтягнутому такті. */
    volatile uint32_t tmp = regs->SR1;
    tmp = regs->SR2;
    (void)tmp;
}

static hal_i2c_status_t start_and_address(I2C_TypeDef *regs, uint8_t dev_addr, bool read)
{
    regs->CR1 |= I2C_CR1_START;

    hal_i2c_status_t st = wait_sr1(regs, I2C_SR1_SB);
    if (st != HAL_I2C_OK) {
        return st;
    }

    regs->DR = (uint8_t)((dev_addr << 1) | (read ? 1u : 0u));
    return wait_sr1(regs, I2C_SR1_ADDR);
}

static hal_i2c_status_t stm32_i2c_write(void *ctx, uint8_t dev_addr,
                                        const uint8_t *data, size_t len)
{
    stm32_i2c_ctx_t *self = (stm32_i2c_ctx_t *)ctx;
    I2C_TypeDef *regs = self->regs;

    hal_i2c_status_t st = wait_not_busy(regs);
    if (st != HAL_I2C_OK) {
        return st;
    }

    st = start_and_address(regs, dev_addr, false);
    if (st != HAL_I2C_OK) {
        return st;
    }
    clear_addr(regs);

    /* len == 0 — це опитування присутності мікросхеми: адресу вона вже
     * підтвердила, тож просто відпускаємо шину. */
    for (size_t i = 0u; i < len; i++) {
        st = wait_sr1(regs, I2C_SR1_TXE);
        if (st != HAL_I2C_OK) {
            return st;
        }
        regs->DR = data[i];
    }

    if (len != 0u) {
        st = wait_sr1(regs, I2C_SR1_BTF);
        if (st != HAL_I2C_OK) {
            return st;
        }
    }

    regs->CR1 |= I2C_CR1_STOP;
    return HAL_I2C_OK;
}

/* Тіло прийому без очікування вільної шини: під час повторного START
 * шина навмисно лишається зайнятою, і перевірка BUSY тут завалила б
 * кожне читання регістра. Очікування робить лише публічна обгортка. */
static hal_i2c_status_t i2c_receive(I2C_TypeDef *regs, uint8_t dev_addr,
                                    uint8_t *data, size_t len)
{
    hal_i2c_status_t st;

    regs->CR1 |= I2C_CR1_ACK;

    st = start_and_address(regs, dev_addr, true);
    if (st != HAL_I2C_OK) {
        return st;
    }

    /* Три різні послідовності завершення прийому — не примха автора, а
     * припис довідника RM0090: контролер має дізнатися про кінець посилки
     * на байт раніше, ніж той доїде. */
    if (len == 1u) {
        regs->CR1 &= ~I2C_CR1_ACK;
        clear_addr(regs);
        regs->CR1 |= I2C_CR1_STOP;

        st = wait_sr1(regs, I2C_SR1_RXNE);
        if (st != HAL_I2C_OK) {
            return st;
        }
        data[0] = (uint8_t)regs->DR;
        return HAL_I2C_OK;
    }

    if (len == 2u) {
        regs->CR1 &= ~I2C_CR1_ACK;
        regs->CR1 |= I2C_CR1_POS;   /* NACK поїде на другий байт */
        clear_addr(regs);

        st = wait_sr1(regs, I2C_SR1_BTF);
        if (st != HAL_I2C_OK) {
            regs->CR1 &= ~I2C_CR1_POS;
            return st;
        }
        regs->CR1 |= I2C_CR1_STOP;
        data[0] = (uint8_t)regs->DR;
        data[1] = (uint8_t)regs->DR;
        regs->CR1 &= ~I2C_CR1_POS;
        return HAL_I2C_OK;
    }

    clear_addr(regs);

    size_t index = 0u;
    while ((len - index) > 3u) {
        st = wait_sr1(regs, I2C_SR1_RXNE);
        if (st != HAL_I2C_OK) {
            return st;
        }
        data[index++] = (uint8_t)regs->DR;
    }

    /* Лишилося три байти: чекаємо BTF, знімаємо ACK і забираємо N-3. */
    st = wait_sr1(regs, I2C_SR1_BTF);
    if (st != HAL_I2C_OK) {
        return st;
    }
    regs->CR1 &= ~I2C_CR1_ACK;
    data[index++] = (uint8_t)regs->DR;

    st = wait_sr1(regs, I2C_SR1_BTF);
    if (st != HAL_I2C_OK) {
        return st;
    }
    regs->CR1 |= I2C_CR1_STOP;
    data[index++] = (uint8_t)regs->DR;
    data[index]   = (uint8_t)regs->DR;

    return HAL_I2C_OK;
}

static hal_i2c_status_t stm32_i2c_read(void *ctx, uint8_t dev_addr,
                                       uint8_t *data, size_t len)
{
    stm32_i2c_ctx_t *self = (stm32_i2c_ctx_t *)ctx;

    if (data == 0 || len == 0u) {
        return HAL_I2C_ERR_ARG;
    }

    const hal_i2c_status_t st = wait_not_busy(self->regs);
    if (st != HAL_I2C_OK) {
        return st;
    }
    return i2c_receive(self->regs, dev_addr, data, len);
}

static hal_i2c_status_t stm32_i2c_write_read(void *ctx, uint8_t dev_addr,
                                             const uint8_t *wdata, size_t wlen,
                                             uint8_t *rdata, size_t rlen)
{
    stm32_i2c_ctx_t *self = (stm32_i2c_ctx_t *)ctx;
    I2C_TypeDef *regs = self->regs;

    if (wdata == 0 || wlen == 0u || rdata == 0 || rlen == 0u) {
        return HAL_I2C_ERR_ARG;
    }

    hal_i2c_status_t st = wait_not_busy(regs);
    if (st != HAL_I2C_OK) {
        return st;
    }

    st = start_and_address(regs, dev_addr, false);
    if (st != HAL_I2C_OK) {
        return st;
    }
    clear_addr(regs);

    for (size_t i = 0u; i < wlen; i++) {
        st = wait_sr1(regs, I2C_SR1_TXE);
        if (st != HAL_I2C_OK) {
            return st;
        }
        regs->DR = wdata[i];
    }

    st = wait_sr1(regs, I2C_SR1_BTF);
    if (st != HAL_I2C_OK) {
        return st;
    }

    /* Повторний START без STOP: шина не відпускається, тож інший майстер
     * не встромиться між адресою регістра й читанням даних. */
    return i2c_receive(regs, dev_addr, rdata, rlen);
}

static const hal_i2c_ops_t g_stm32_i2c_ops = {
    .write      = stm32_i2c_write,
    .read       = stm32_i2c_read,
    .write_read = stm32_i2c_write_read,
};

static const hal_i2c_bus_t g_i2c1_bus = {
    .ops = &g_stm32_i2c_ops,
    .ctx = &g_i2c1_ctx,
};

const hal_i2c_bus_t *stm32_i2c1_init(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;

    /* PB6 = SCL, PB7 = SDA: альтернативна функція 4, відкритий стік,
     * підтяжки на платі зовнішні (4.7 кОм). */
    GPIOB->MODER   &= ~((3u << (6u * 2u)) | (3u << (7u * 2u)));
    GPIOB->MODER   |=  ((2u << (6u * 2u)) | (2u << (7u * 2u)));
    GPIOB->OTYPER  |=  ((1u << 6u) | (1u << 7u));
    GPIOB->OSPEEDR |=  ((3u << (6u * 2u)) | (3u << (7u * 2u)));
    GPIOB->PUPDR   &= ~((3u << (6u * 2u)) | (3u << (7u * 2u)));
    GPIOB->AFR[0]  &= ~((0xFu << (6u * 4u)) | (0xFu << (7u * 4u)));
    GPIOB->AFR[0]  |=  ((4u << (6u * 4u)) | (4u << (7u * 4u)));

    I2C1->CR1 = I2C_CR1_SWRST;   /* контролер після скидання шини буває
                                  * у стані «зайнято»; скидаємо явно */
    I2C1->CR1 = 0u;
    I2C1->CR2   = I2C_APB1_CLOCK_MHZ;
    I2C1->CCR   = I2C_CCR_100KHZ;
    I2C1->TRISE = I2C_TRISE_100KHZ;
    I2C1->CR1  |= I2C_CR1_PE;

    return &g_i2c1_bus;
}
