/* BME280 на I2C1 (PB6/PB7) у forced-режимі.
   Самі транзакції короткі: 2-4 байти на 100 кГц — це 200-400 мкс, і робити
   з них автомат немає сенсу, вони блокуючі зі сторожовим лічильником.
   Неблокуючим зроблено те, що справді довге: 5 мс самого вимірювання. */
#include "sensor.h"

#include "stm32g0xx.h"

#define BME280_ADDR   0x76u
#define REG_CALIB_T   0x88u
#define REG_ID        0xD0u
#define REG_STATUS    0xF3u
#define REG_CTRL_MEAS 0xF4u
#define REG_CONFIG    0xF5u
#define REG_TEMP_MSB  0xFAu
#define CHIP_ID       0x60u

/* osrs_t = x1, osrs_p = skip, mode = forced. */
#define CTRL_MEAS_FORCED 0x21u
/* Час перетворення при x1: 1.25 + 2.3 ≈ 4 мс (datasheet 9.1) — беремо 5. */
#define MEAS_TIME_MS 5u
#define MEAS_TIMEOUT_MS 50u
#define FAULT_PAUSE_MS 1000u

/* Тайминг 100 кГц для PCLK = 16 МГц (HSI16 після скидання).
   Під іншу частоту число рахує CubeMX — воно тактозалежне. */
#define I2C_TIMINGR_100K 0x00303D5Bu

/* Сторож на прапорці: 100 тис. обертів на 16 МГц — це кілька мілісекунд,
   тобто довше за будь-який байт на 100 кГц і коротше за вікно watchdog. */
#define BUS_GUARD 100000u

static void i2c_hw_init(void)
{
    RCC->IOPENR  |= RCC_IOPENR_GPIOBEN;
    RCC->APBENR1 |= RCC_APBENR1_I2C1EN;

    /* PB6 = SCL, PB7 = SDA: альтернативна функція 6, відкритий стік, підтяжка. */
    GPIOB->MODER = (GPIOB->MODER & ~(GPIO_MODER_MODE6 | GPIO_MODER_MODE7))
                 | (2u << GPIO_MODER_MODE6_Pos) | (2u << GPIO_MODER_MODE7_Pos);
    GPIOB->OTYPER |= GPIO_OTYPER_OT6 | GPIO_OTYPER_OT7;
    GPIOB->PUPDR = (GPIOB->PUPDR & ~(GPIO_PUPDR_PUPD6 | GPIO_PUPDR_PUPD7))
                 | (1u << GPIO_PUPDR_PUPD6_Pos) | (1u << GPIO_PUPDR_PUPD7_Pos);
    GPIOB->AFR[0] = (GPIOB->AFR[0] & ~(GPIO_AFRL_AFSEL6 | GPIO_AFRL_AFSEL7))
                  | (6u << GPIO_AFRL_AFSEL6_Pos) | (6u << GPIO_AFRL_AFSEL7_Pos);

    I2C1->CR1     = 0u;              /* налаштування — лише при PE = 0 */
    I2C1->TIMINGR = I2C_TIMINGR_100K;
    I2C1->CR1     = I2C_CR1_PE;
}

static void i2c_reset(void)
{
    /* Після NACK чи зависання шини периферію треба перезапустити:
       інакше наступна транзакція піде по зайнятому BUSY. */
    I2C1->CR1 &= ~I2C_CR1_PE;
    for (volatile int i = 0; i < 16; i++) { /* три такти APB на скидання */ }
    I2C1->CR1 |= I2C_CR1_PE;
}

static bool i2c_wait(uint32_t flag)
{
    uint32_t guard = BUS_GUARD;
    while ((I2C1->ISR & flag) == 0u) {
        if ((I2C1->ISR & I2C_ISR_NACKF) != 0u) {
            I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;
            return false;
        }
        if (guard-- == 0u) {
            return false;
        }
    }
    return true;
}

static void i2c_finish(void)
{
    uint32_t guard = BUS_GUARD;
    while (((I2C1->ISR & I2C_ISR_STOPF) == 0u) && (guard-- != 0u)) { }
    I2C1->ICR = I2C_ICR_STOPCF | I2C_ICR_NACKCF;
}

static bool i2c_write_reg(uint8_t reg, uint8_t value)
{
    I2C1->CR2 = ((uint32_t)BME280_ADDR << 1) | (2u << I2C_CR2_NBYTES_Pos)
              | I2C_CR2_AUTOEND | I2C_CR2_START;
    if (!i2c_wait(I2C_ISR_TXIS)) { i2c_reset(); return false; }
    I2C1->TXDR = reg;
    if (!i2c_wait(I2C_ISR_TXIS)) { i2c_reset(); return false; }
    I2C1->TXDR = value;
    i2c_finish();
    return true;
}

static bool i2c_read_regs(uint8_t reg, uint8_t *buf, uint8_t len)
{
    /* Фаза адреси регістра — без AUTOEND, далі повторний старт на читання. */
    I2C1->CR2 = ((uint32_t)BME280_ADDR << 1) | (1u << I2C_CR2_NBYTES_Pos) | I2C_CR2_START;
    if (!i2c_wait(I2C_ISR_TXIS)) { i2c_reset(); return false; }
    I2C1->TXDR = reg;
    if (!i2c_wait(I2C_ISR_TC)) { i2c_reset(); return false; }

    I2C1->CR2 = ((uint32_t)BME280_ADDR << 1) | ((uint32_t)len << I2C_CR2_NBYTES_Pos)
              | I2C_CR2_RD_WRN | I2C_CR2_AUTOEND | I2C_CR2_START;
    for (uint8_t i = 0; i < len; i++) {
        if (!i2c_wait(I2C_ISR_RXNE)) { i2c_reset(); return false; }
        buf[i] = (uint8_t)I2C1->RXDR;
    }
    i2c_finish();
    return true;
}

/* Цілочисельна компенсація температури — формула з datasheet, розділ 4.2.3. */
static int32_t compensate(const sensor_t *s, int32_t adc_t)
{
    int32_t var1 = ((((adc_t >> 3) - ((int32_t)s->dig_t1 << 1))) * (int32_t)s->dig_t2) >> 11;
    int32_t d    = (adc_t >> 4) - (int32_t)s->dig_t1;
    int32_t var2 = (((d * d) >> 12) * (int32_t)s->dig_t3) >> 14;
    int32_t t_fine = var1 + var2;
    return (t_fine * 5 + 128) >> 8; /* сотые градуса */
}

static void go_fault(sensor_t *s, uint32_t now_ms)
{
    s->errors++;
    s->state = SENSOR_FAULT;
    s->started_ms = now_ms;
    if (s->retries < 255u) {
        s->retries++;
    }
}

bool sensor_init(sensor_t *s)
{
    uint8_t id = 0u;
    uint8_t cal[6];

    i2c_hw_init();

    if (!i2c_read_regs(REG_ID, &id, 1u) || (id != CHIP_ID)) {
        return false;
    }
    if (!i2c_read_regs(REG_CALIB_T, cal, sizeof cal)) {
        return false;
    }
    s->dig_t1 = (uint16_t)((uint16_t)cal[1] << 8 | cal[0]);
    s->dig_t2 = (int16_t)((uint16_t)cal[3] << 8 | cal[2]);
    s->dig_t3 = (int16_t)((uint16_t)cal[5] << 8 | cal[4]);

    /* Фільтр вимкнено: у forced-режимі він лише розмазує одиночні виміри. */
    if (!i2c_write_reg(REG_CONFIG, 0x00u)) {
        return false;
    }
    s->state = SENSOR_IDLE;
    s->retries = 0u;
    return true;
}

void sensor_start(sensor_t *s, uint32_t now_ms)
{
    if (s->state != SENSOR_IDLE) {
        return; /* попередній вимір ще не забрали — новий не нав'язуємо */
    }
    if (!i2c_write_reg(REG_CTRL_MEAS, CTRL_MEAS_FORCED)) {
        go_fault(s, now_ms);
        return;
    }
    s->started_ms = now_ms;
    s->state = SENSOR_WAIT;
}

bool sensor_poll(sensor_t *s, uint32_t now_ms)
{
    switch (s->state) {
    case SENSOR_IDLE:
        return false;

    case SENSOR_WAIT: {
        uint8_t status = 0u;
        if ((now_ms - s->started_ms) < MEAS_TIME_MS) {
            return false; /* ще рано — виходимо, цикл робить інші справи */
        }
        if (!i2c_read_regs(REG_STATUS, &status, 1u)) {
            go_fault(s, now_ms);
            return false;
        }
        if ((status & 0x08u) != 0u) { /* біт measuring */
            if ((now_ms - s->started_ms) > MEAS_TIMEOUT_MS) {
                go_fault(s, now_ms); /* датчик завис у вимірюванні */
            }
            return false;
        }
        s->state = SENSOR_READ;
        return false;
    }

    case SENSOR_READ: {
        uint8_t raw[3];
        int32_t adc;
        if (!i2c_read_regs(REG_TEMP_MSB, raw, sizeof raw)) {
            go_fault(s, now_ms);
            return false;
        }
        adc = ((int32_t)raw[0] << 12) | ((int32_t)raw[1] << 4) | ((int32_t)raw[2] >> 4);
        if (adc == 0x80000) {
            go_fault(s, now_ms); /* 0x80000 — датчик не мав дійсного виміру */
            return false;
        }
        s->temp_c100 = compensate(s, adc);
        s->retries = 0u;
        s->state = SENSOR_IDLE;
        return true;
    }

    case SENSOR_FAULT:
    default:
        if ((now_ms - s->started_ms) < FAULT_PAUSE_MS) {
            return false; /* пауза перед повторним підняттям шини */
        }
        if (sensor_init(s)) {
            s->state = SENSOR_IDLE;
        } else {
            s->started_ms = now_ms;
        }
        return false;
    }
}
