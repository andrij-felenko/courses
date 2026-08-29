#include "stm32l4xx.h"
#include "node.h"
#include "i2c.h"

#define I2C_TIMEOUT_MS 5u     /* найдовша транзакція вузла — 8 байтів на 100 кГц */
#define SCL_PIN 6u            /* PB6 */
#define SDA_PIN 7u            /* PB7 */

static uint32_t recovery_count;

/* ── Перемикання PB6/PB7 між периферією I2C1 і ручним GPIO ───────────────── */

static void pins_to_i2c(void)
{
    /* Відкритий стік, підтяжка вгору, альтернативна функція AF4 = I2C1. */
    GPIOB->OTYPER |= (1u << SCL_PIN) | (1u << SDA_PIN);
    GPIOB->PUPDR  = (GPIOB->PUPDR & ~((3u << (SCL_PIN * 2)) | (3u << (SDA_PIN * 2))))
                  | (1u << (SCL_PIN * 2)) | (1u << (SDA_PIN * 2));
    GPIOB->AFR[0] = (GPIOB->AFR[0] & ~((0xFu << (SCL_PIN * 4)) | (0xFu << (SDA_PIN * 4))))
                  | (4u << (SCL_PIN * 4)) | (4u << (SDA_PIN * 4));
    GPIOB->MODER  = (GPIOB->MODER & ~((3u << (SCL_PIN * 2)) | (3u << (SDA_PIN * 2))))
                  | (2u << (SCL_PIN * 2)) | (2u << (SDA_PIN * 2));   /* AF */
}

static void pins_to_gpio(void)
{
    /* Ті самі виводи, але вихід загального призначення: такти жене прошивка. */
    GPIOB->BSRR  = (1u << SCL_PIN) | (1u << SDA_PIN);   /* обидві лінії відпустити */
    GPIOB->MODER = (GPIOB->MODER & ~((3u << (SCL_PIN * 2)) | (3u << (SDA_PIN * 2))))
                 | (1u << (SCL_PIN * 2)) | (1u << (SDA_PIN * 2));    /* вихід */
}

static bool sda_is_high(void)
{
    return (GPIOB->IDR & (1u << SDA_PIN)) != 0u;
}

static void scl_set(bool high)
{
    GPIOB->BSRR = high ? (1u << SCL_PIN) : (1u << (SCL_PIN + 16u));
}

static void sda_set(bool high)
{
    GPIOB->BSRR = high ? (1u << SDA_PIN) : (1u << (SDA_PIN + 16u));
}

/* ── Ініціалізація периферії ─────────────────────────────────────────────── */

static void i2c_peripheral_setup(void)
{
    I2C1->CR1 = 0;                       /* PE=0 скидає внутрішній автомат */
    /* 100 кГц від ядра HSI16: PRESC=0, SCLDEL=3, SDADEL=0, SCLH=0x3D, SCLL=0x5B */
    I2C1->TIMINGR = 0x00303D5Bu;
    I2C1->CR1 = I2C_CR1_PE;
}

void i2c_init(void)
{
    RCC->AHB2ENR  |= RCC_AHB2ENR_GPIOBEN;
    RCC->APB1ENR1 |= RCC_APB1ENR1_I2C1EN;
    /* Ядро I2C тактуємо від HSI16: тайминги не залежать від того, чи ми
     * щойно вийшли зі Stop 2 і на чому зараз крутиться SYSCLK. */
    RCC->CCIPR = (RCC->CCIPR & ~RCC_CCIPR_I2C1SEL) | (2u << RCC_CCIPR_I2C1SEL_Pos);
    RCC->CR |= RCC_CR_HSION;
    while ((RCC->CR & RCC_CR_HSIRDY) == 0u) { }

    pins_to_i2c();
    i2c_peripheral_setup();

    /* Ведені могли лишитися завислими після попереднього скидання ядра —
     * розблоковуємо шину ще до першої транзакції. */
    if ((I2C1->ISR & I2C_ISR_BUSY) != 0u) {
        i2c_bus_recover();
    }
}

/* ── Розблокування шини ──────────────────────────────────────────────────── */

bool i2c_bus_recover(void)
{
    recovery_count++;

    I2C1->CR1 &= ~I2C_CR1_PE;      /* periph off, інакше вона тримає лінії */
    pins_to_gpio();

    bool released = sda_is_high();

    /* До дев'яти тактів: рівно стільки треба, щоб ведений домовив байт,
     * якого від нього ніхто вже не чекає, і відпустив SDA. */
    for (uint8_t i = 0; i < 9u && !released; i++) {
        scl_set(false);
        delay_us(5);
        scl_set(true);
        delay_us(5);
        released = sda_is_high();
    }

    /* Коректний STOP: SDA іде з нуля в одиницю при високому SCL. */
    sda_set(false);
    delay_us(5);
    scl_set(true);
    delay_us(5);
    sda_set(true);
    delay_us(5);

    pins_to_i2c();
    i2c_peripheral_setup();

    return released && ((I2C1->ISR & I2C_ISR_BUSY) == 0u);
}

/* ── Транзакції ──────────────────────────────────────────────────────────── */

/* Чекаємо будь-який із прапорців mask; NACK і тайм-аут — окремі відповіді. */
static i2c_status_t wait_isr(uint32_t mask)
{
    uint32_t deadline = millis() + I2C_TIMEOUT_MS + 1u;

    for (;;) {
        uint32_t isr = I2C1->ISR;

        if ((isr & mask) != 0u) {
            return I2C_OK;
        }
        if ((isr & I2C_ISR_NACKF) != 0u) {
            I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;
            return I2C_ERR_NACK;
        }
        if ((int32_t)(millis() - deadline) >= 0) {
            return I2C_ERR_TIMEOUT;
        }
    }
}

static i2c_status_t wait_not_busy(void)
{
    uint32_t deadline = millis() + I2C_TIMEOUT_MS + 1u;

    while ((I2C1->ISR & I2C_ISR_BUSY) != 0u) {
        if ((int32_t)(millis() - deadline) >= 0) {
            /* Класичний випадок: ведений тримає SDA і шина «зайнята» назавжди. */
            return i2c_bus_recover() ? I2C_OK : I2C_ERR_BUSY;
        }
    }
    return I2C_OK;
}

/* Аварійне завершення: гасимо периферію, щоб наступна транзакція почалася
 * з чистого автомата, а не доїдала недороблену. */
static i2c_status_t abort_transfer(i2c_status_t why)
{
    I2C1->CR1 &= ~I2C_CR1_PE;
    for (volatile int i = 0; i < 8; i++) { }
    I2C1->CR1 |= I2C_CR1_PE;

    if (why == I2C_ERR_TIMEOUT) {
        i2c_bus_recover();
    }
    return why;
}

i2c_status_t i2c_write(uint8_t addr7, const uint8_t *data, uint8_t len)
{
    i2c_status_t st = wait_not_busy();
    if (st != I2C_OK) {
        return st;
    }

    I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;
    I2C1->CR2 = ((uint32_t)addr7 << 1) |
                ((uint32_t)len << I2C_CR2_NBYTES_Pos) |
                I2C_CR2_AUTOEND | I2C_CR2_START;

    for (uint8_t i = 0; i < len; i++) {
        st = wait_isr(I2C_ISR_TXIS);
        if (st != I2C_OK) {
            return abort_transfer(st);
        }
        I2C1->TXDR = data[i];
    }

    st = wait_isr(I2C_ISR_STOPF);
    if (st != I2C_OK) {
        return abort_transfer(st);
    }
    I2C1->ICR = I2C_ICR_STOPCF;
    return I2C_OK;
}

i2c_status_t i2c_write_reg(uint8_t addr7, uint8_t reg, uint8_t value)
{
    uint8_t buf[2] = { reg, value };
    return i2c_write(addr7, buf, 2u);
}

i2c_status_t i2c_read_regs(uint8_t addr7, uint8_t reg, uint8_t *dst, uint8_t len)
{
    i2c_status_t st = wait_not_busy();
    if (st != I2C_OK) {
        return st;
    }

    I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;

    /* Перша фаза — адреса регістра, без AUTOEND: після неї потрібен
     * повторний старт, а не STOP, інакше DS3231 скине внутрішній вказівник. */
    I2C1->CR2 = ((uint32_t)addr7 << 1) | (1u << I2C_CR2_NBYTES_Pos) | I2C_CR2_START;

    st = wait_isr(I2C_ISR_TXIS);
    if (st != I2C_OK) {
        return abort_transfer(st);
    }
    I2C1->TXDR = reg;

    st = wait_isr(I2C_ISR_TC);
    if (st != I2C_OK) {
        return abort_transfer(st);
    }

    /* Друга фаза — повторний старт і читання з автоматичним STOP. */
    I2C1->CR2 = ((uint32_t)addr7 << 1) |
                ((uint32_t)len << I2C_CR2_NBYTES_Pos) |
                I2C_CR2_RD_WRN | I2C_CR2_AUTOEND | I2C_CR2_START;

    for (uint8_t i = 0; i < len; i++) {
        st = wait_isr(I2C_ISR_RXNE);
        if (st != I2C_OK) {
            return abort_transfer(st);
        }
        dst[i] = (uint8_t)I2C1->RXDR;
    }

    st = wait_isr(I2C_ISR_STOPF);
    if (st != I2C_OK) {
        return abort_transfer(st);
    }
    I2C1->ICR = I2C_ICR_STOPCF;
    return I2C_OK;
}

uint32_t i2c_recovery_count(void)
{
    return recovery_count;
}
