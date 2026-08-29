#include "i2c.h"
#include "pins.h"
#include "regs.h"

#define SCL_PORT GPIOB
#define SCL_PIN  6u
#define SDA_PORT GPIOB
#define SDA_PIN  7u
#define I2C1_AF  4u

/* ≈100 кГц при I2CCLK = MSI 4 МГц: PRESC=0, SCLDEL=4, SDADEL=2, SCLH=15, SCLL=19. */
#define I2C_TIMING_100K_AT_4MHZ 0x00420F13UL

/* Спини обмежені: раб, що завис, не має права підвісити всю прошивку. */
#define SPIN_LIMIT 20000u

static i2c_err_t wait_isr(uint32_t mask)
{
    for (uint32_t spin = 0; spin < SPIN_LIMIT; ++spin) {
        const uint32_t isr = I2C1_ISR;
        if (isr & (I2C_ISR_BERR | I2C_ISR_ARLO)) {
            I2C1_ICR = I2C_ICR_CLEAR_ALL;
            return I2C_ERR_BUS;
        }
        if (isr & I2C_ISR_NACKF) {
            I2C1_ICR = I2C_ICR_CLEAR_ALL;
            return I2C_ERR_NACK;
        }
        if (isr & mask) {
            return I2C_OK;
        }
    }
    return I2C_ERR_TIMEOUT;
}

static void pins_to_i2c(void)
{
    SCL_PORT->OTYPER |= (1u << SCL_PIN) | (1u << SDA_PIN); /* відкритий стік */
    pin_af(SCL_PORT, SCL_PIN, I2C1_AF);
    pin_af(SDA_PORT, SDA_PIN, I2C1_AF);
    pin_pull(SCL_PORT, SCL_PIN, PULL_NONE); /* підтяжки зовнішні, з 3V3_SW */
    pin_pull(SDA_PORT, SDA_PIN, PULL_NONE);
    pin_mode(SCL_PORT, SCL_PIN, MODE_AF);
    pin_mode(SDA_PORT, SDA_PIN, MODE_AF);
}

bool i2c1_bus_stuck(void)
{
    /* Дивимося на лінії як на входи: у спокої обидві мусять бути вгорі
     * (їх тягнуть зовнішні резистори). SDA внизу = раб тримає шину. */
    pin_mode(SCL_PORT, SCL_PIN, MODE_INPUT);
    pin_mode(SDA_PORT, SDA_PIN, MODE_INPUT);
    board_delay_ms(1);
    const bool sda_low = !pin_read(SDA_PORT, SDA_PIN);
    const bool scl_low = !pin_read(SCL_PORT, SCL_PIN);
    return sda_low || scl_low;
}

i2c_err_t i2c1_bus_recover(void)
{
    /* Класичне вивільнення: до дев'яти тактів SCL, поки раб не доотримає
     * недописаний байт і не відпустить SDA, потім умова STOP. */
    I2C1_CR1 &= ~I2C_CR1_PE;

    SCL_PORT->OTYPER |= (1u << SCL_PIN) | (1u << SDA_PIN);
    pin_write(SCL_PORT, SCL_PIN, true);
    pin_write(SDA_PORT, SDA_PIN, true);
    pin_mode(SCL_PORT, SCL_PIN, MODE_OUTPUT);
    pin_mode(SDA_PORT, SDA_PIN, MODE_INPUT);

    for (unsigned i = 0; i < 9u && !pin_read(SDA_PORT, SDA_PIN); ++i) {
        pin_write(SCL_PORT, SCL_PIN, false);
        board_delay_ms(1);
        pin_write(SCL_PORT, SCL_PIN, true);
        board_delay_ms(1);
    }

    /* STOP: SDA піднімається при високому SCL. */
    pin_mode(SDA_PORT, SDA_PIN, MODE_OUTPUT);
    pin_write(SDA_PORT, SDA_PIN, false);
    board_delay_ms(1);
    pin_write(SCL_PORT, SCL_PIN, true);
    board_delay_ms(1);
    pin_write(SDA_PORT, SDA_PIN, true);
    board_delay_ms(1);
    pin_mode(SDA_PORT, SDA_PIN, MODE_INPUT);

    const bool freed = pin_read(SDA_PORT, SDA_PIN);
    pins_to_i2c();
    I2C1_CR1 |= I2C_CR1_PE;
    return freed ? I2C_OK : I2C_ERR_STUCK;
}

i2c_err_t i2c1_init(void)
{
    RCC_APB1ENR1 |= RCC_APB1ENR1_I2C1EN;
    (void)RCC_APB1ENR1;

    I2C1_CR1 &= ~I2C_CR1_PE;
    I2C1_TIMINGR = I2C_TIMING_100K_AT_4MHZ;

    if (i2c1_bus_stuck()) {
        const i2c_err_t err = i2c1_bus_recover();
        if (err != I2C_OK) {
            return err;
        }
    }

    pins_to_i2c();
    I2C1_ICR = I2C_ICR_CLEAR_ALL;
    I2C1_CR1 |= I2C_CR1_PE;
    return I2C_OK;
}

void i2c1_deinit(void)
{
    I2C1_CR1 &= ~I2C_CR1_PE;
    RCC_APB1ENR1 &= ~RCC_APB1ENR1_I2C1EN;
    /* Виводи паркує board_park_switched_domain(): вони йдуть у знеструмлений
     * домен, і тримати їх у режимі AF означало б живити датчик через діод. */
}

static i2c_err_t transfer_start(uint8_t addr7, uint8_t nbytes, bool read, bool autoend)
{
    if (I2C1_ISR & I2C_ISR_BUSY) {
        return I2C_ERR_BUS;
    }
    uint32_t cr2 = ((uint32_t)addr7 << 1u)
                 | ((uint32_t)nbytes << I2C_CR2_NBYTES_SHIFT)
                 | I2C_CR2_START;
    if (read) {
        cr2 |= I2C_CR2_RD_WRN;
    }
    if (autoend) {
        cr2 |= I2C_CR2_AUTOEND;
    }
    I2C1_CR2 = cr2;
    return I2C_OK;
}

i2c_err_t i2c1_read_reg(uint8_t addr7, uint8_t reg, uint8_t *buf, uint8_t len)
{
    if (buf == 0 || len == 0u) {
        return I2C_ERR_BUS;
    }

    /* Фаза 1: записуємо покажчик регістра, без STOP. */
    i2c_err_t err = transfer_start(addr7, 1u, false, false);
    if (err != I2C_OK) {
        return err;
    }
    err = wait_isr(I2C_ISR_TXIS);
    if (err != I2C_OK) {
        I2C1_CR2 |= I2C_CR2_STOP;
        return err;
    }
    I2C1_TXDR = reg;

    err = wait_isr(I2C_ISR_TC);
    if (err != I2C_OK) {
        I2C1_CR2 |= I2C_CR2_STOP;
        return err;
    }

    /* Фаза 2: повторний старт на читання, автоматичний STOP наприкінці. */
    err = transfer_start(addr7, len, true, true);
    if (err != I2C_OK) {
        return err;
    }
    for (uint8_t i = 0; i < len; ++i) {
        err = wait_isr(I2C_ISR_RXNE);
        if (err != I2C_OK) {
            I2C1_CR2 |= I2C_CR2_STOP;
            return err;
        }
        buf[i] = (uint8_t)I2C1_RXDR;
    }

    err = wait_isr(I2C_ISR_STOPF);
    I2C1_ICR = I2C_ICR_CLEAR_ALL;
    return err;
}
