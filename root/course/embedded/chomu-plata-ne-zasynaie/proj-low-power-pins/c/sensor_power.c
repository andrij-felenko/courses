#include "sensor_power.h"

/* Плата: барометр BME280 і акселерометр LIS2DH12 на спільній шині 3V3_SENS,
 * яку вмикає P-MOSFET. Підтяжки I2C сидять на ТІЙ САМІЙ шині — тому вони
 * зникають разом із живленням, і мікроконтролер не має чим фантомити датчики. */
#define BME280_ADDR      0x76U
#define BME280_REG_ID    0xD0U
#define BME280_ID_VALUE  0x60U
#define BME280_REG_CTRL  0xF4U
#define BME280_SLEEP     0x00U /* режим 00 — сон */
#define BME280_FORCED    0x25U /* передискретизація ×1 по обох каналах, один вимір */
#define BME280_REG_TEMP  0xFAU

#define LIS2DH_ADDR      0x19U
#define LIS2DH_REG_CTRL1 0x20U
#define LIS2DH_POWERDOWN 0x00U
#define LIS2DH_ODR_100HZ 0x57U

/* Час на обмін одним байтом із запасом на розтягування такту веденим. */
#define I2C_STEP_TIMEOUT_US 2000U
/* Скільки чекати завершення передачі перед знеструмленням. */
#define BUS_QUIESCE_TIMEOUT_US 5000U

/* Розряд шини датчиків після розмикання ключа.
 * Стікач 10 кОм і 4.7 мкФ блокувальної ємності дають tau ≈ 47 мс;
 * п'яти постійних часу досить, щоб напруга впала нижче порога діодів. */
#define RAIL_DISCHARGE_MS 235U
/* Наростання шини плюс час старту BME280 після подання живлення. */
#define RAIL_STARTUP_MS 5U

const char *rail_status_str(rail_status_t st)
{
    switch (st) {
    case RAIL_OK:            return "ok";
    case RAIL_ERR_I2C_NACK:  return "датчик не відповів (NACK)";
    case RAIL_ERR_I2C_TIMEOUT: return "i2c: таймаут кроку";
    case RAIL_ERR_BUS:       return "шина не зупинилася чисто";
    case RAIL_ERR_ID:        return "на шині не той датчик";
    default:                 return "?";
    }
}

/* Чекає один із прапорців ISR; NACK повертає окремим кодом, бо це не таймаут,
 * а відповідь заліза: за такою адресою нікого немає. */
static rail_status_t i2c_wait(uint32_t flag)
{
    uint32_t left = I2C_STEP_TIMEOUT_US;
    for (;;) {
        uint32_t isr = I2C1->ISR;
        if ((isr & I2C_ISR_NACKF) != 0U) {
            I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;
            return RAIL_ERR_I2C_NACK;
        }
        if ((isr & flag) != 0U) {
            return RAIL_OK;
        }
        if (left == 0U) {
            return RAIL_ERR_I2C_TIMEOUT;
        }
        mcu_delay_us(1U);
        left--;
    }
}

static rail_status_t i2c_finish(void)
{
    rail_status_t st = i2c_wait(I2C_ISR_STOPF);
    I2C1->ICR = I2C_ICR_STOPCF;
    I2C1->CR2 = 0U;
    return st;
}

rail_status_t i2c_write_reg(uint8_t addr7, uint8_t reg, uint8_t value)
{
    if ((I2C1->CR1 & I2C_CR1_PE) == 0U) {
        I2C1->CR1 |= I2C_CR1_PE; /* після сну модуль лишається вимкненим */
    }

    I2C1->CR2 = I2C_CR2_SADD(addr7) | I2C_CR2_NBYTES(2U) |
                I2C_CR2_AUTOEND | I2C_CR2_START;

    rail_status_t st = i2c_wait(I2C_ISR_TXIS);
    if (st != RAIL_OK) {
        return st;
    }
    I2C1->TXDR = reg;

    st = i2c_wait(I2C_ISR_TXIS);
    if (st != RAIL_OK) {
        return st;
    }
    I2C1->TXDR = value;

    return i2c_finish();
}

rail_status_t i2c_read_regs(uint8_t addr7, uint8_t reg, uint8_t *dst, uint8_t len)
{
    if ((I2C1->CR1 & I2C_CR1_PE) == 0U) {
        I2C1->CR1 |= I2C_CR1_PE;
    }

    /* Фаза 1: пишемо номер регістра БЕЗ AUTOEND, щоб утримати шину до
     * повторного старту. */
    I2C1->CR2 = I2C_CR2_SADD(addr7) | I2C_CR2_NBYTES(1U) | I2C_CR2_START;

    rail_status_t st = i2c_wait(I2C_ISR_TXIS);
    if (st != RAIL_OK) {
        return st;
    }
    I2C1->TXDR = reg;

    st = i2c_wait(I2C_ISR_TC);
    if (st != RAIL_OK) {
        return st;
    }

    /* Фаза 2: повторний старт на читання, автоматичний STOP наприкінці. */
    I2C1->CR2 = I2C_CR2_SADD(addr7) | I2C_CR2_NBYTES(len) |
                I2C_CR2_RD_WRN | I2C_CR2_AUTOEND | I2C_CR2_START;

    for (uint8_t n = 0U; n < len; n++) {
        st = i2c_wait(I2C_ISR_RXNE);
        if (st != RAIL_OK) {
            return st;
        }
        dst[n] = (uint8_t)I2C1->RXDR;
    }

    return i2c_finish();
}

/* --------------------------- вимикальний хід --------------------------- */

rail_status_t sensor_rail_shutdown(void)
{
    rail_status_t st;

    /* 1. Просимо датчики заснути самих. Це не ввічливість: акселерометр із
     * увімкненим перетворювачем тягне сотні мікроампер навіть тоді, коли шину
     * вже ніхто не читає, а барометр посеред виміру не відпустить шину. */
    st = i2c_write_reg(BME280_ADDR, BME280_REG_CTRL, BME280_SLEEP);
    if (st != RAIL_OK) {
        return st;
    }
    st = i2c_write_reg(LIS2DH_ADDR, LIS2DH_REG_CTRL1, LIS2DH_POWERDOWN);
    if (st != RAIL_OK) {
        return st;
    }

    /* 2. Зупиняємо шини й відпускаємо лінії в Hi-Z. */
    if (bus_quiesce_all(BUS_QUIESCE_TIMEOUT_US) != BUS_OK) {
        return RAIL_ERR_BUS;
    }

    /* 3. Розмикаємо силовий ключ: одиниця на затворі P-MOSFET закриває його. */
    gpio_write(RAIL_SWITCH_PORT, RAIL_SWITCH_PIN, true);

    /* 4. Витримка на розряд. Поки на блокувальних ємностях датчика лишається
     * напруга, будь-який вивід мікроконтролера, зведений у нуль, стає для неї
     * стоком через нижній захисний діод. */
    mcu_delay_ms(RAIL_DISCHARGE_MS);

    return RAIL_OK;
}

rail_status_t sensor_rail_power_up(void)
{
    /* 1. Ключ. Нуль на затворі P-MOSFET відкриває його. */
    gpio_write(RAIL_SWITCH_PORT, RAIL_SWITCH_PIN, false);
    mcu_delay_ms(RAIL_STARTUP_MS);

    /* 2. Модуль I2C і його виводи повертаються до роботи. */
    gpio_af(GPIOB, 8U, 4U);
    gpio_af(GPIOB, 9U, 4U);
    I2C1->CR1 |= I2C_CR1_PE;

    /* 3. Перевірка ідентифікатора: якщо шина не піднялася або підтяжки зникли
     * разом із живленням датчиків, читання дасть 0x00 або 0xFF, і краще
     * дізнатися про це тут, ніж прийняти сміття за вимір. */
    uint8_t id = 0U;
    rail_status_t st = i2c_read_regs(BME280_ADDR, BME280_REG_ID, &id, 1U);
    if (st != RAIL_OK) {
        return st;
    }
    if (id != BME280_ID_VALUE) {
        return RAIL_ERR_ID;
    }

    /* 4. Датчики знову в робочому режимі. */
    st = i2c_write_reg(LIS2DH_ADDR, LIS2DH_REG_CTRL1, LIS2DH_ODR_100HZ);
    if (st != RAIL_OK) {
        return st;
    }
    return i2c_write_reg(BME280_ADDR, BME280_REG_CTRL, BME280_FORCED);
}

rail_status_t sensor_read_temperature_raw(int32_t *raw)
{
    /* Один вимір на вимогу; ×1 передискретизації — близько 7 мс. */
    rail_status_t st = i2c_write_reg(BME280_ADDR, BME280_REG_CTRL, BME280_FORCED);
    if (st != RAIL_OK) {
        return st;
    }
    mcu_delay_ms(10U);

    uint8_t buf[3] = {0U, 0U, 0U};
    st = i2c_read_regs(BME280_ADDR, BME280_REG_TEMP, buf, 3U);
    if (st != RAIL_OK) {
        return st;
    }

    /* Двадцять значущих бітів: старший, середній і чотири біти молодшого. */
    *raw = (int32_t)(((uint32_t)buf[0] << 12) |
                     ((uint32_t)buf[1] << 4) |
                     ((uint32_t)buf[2] >> 4));
    return RAIL_OK;
}
