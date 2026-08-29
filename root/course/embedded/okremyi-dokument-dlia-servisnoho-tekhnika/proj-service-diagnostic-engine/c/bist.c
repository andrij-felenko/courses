/* bist.c — самотестування плати. I2C реалізовано програмно: так бюджет
   часу видно прямо в коді, а не ховається в регістрі периферії. */

#include "bist.h"

#include <string.h>

#include "hw_port.h"

#define I2C_HALF_BIT_US     5u  /* близько 100 кГц */
#define I2C_TIMEOUT_MS      5u  /* бюджет однієї спроби */
#define BUS_LOCK_TIMEOUT_MS 20u

#define I2C_ADDR_RTC    0x68u
#define I2C_ADDR_EEPROM 0x50u

#define ADC_VREF_MV    3300u
#define ADC_FULL_SCALE 4096u

static bool expired(uint32_t deadline)
{
    return (int32_t)(hw_get_tick_ms() - deadline) >= 0;
}

/* Відпустити SCL і дочекатися, поки ведений перестане тримати такт
   (clock stretching). Тримає надто довго — виходимо за тайм-аутом. */
static bool scl_high(uint32_t deadline)
{
    hw_i2c_scl_release();
    while (!hw_i2c_scl_read()) {
        if (expired(deadline)) {
            return false;
        }
    }
    hw_delay_us(I2C_HALF_BIT_US);
    return true;
}

static void scl_low(void)
{
    hw_i2c_scl_low();
    hw_delay_us(I2C_HALF_BIT_US);
}

static bool write_bit(bool bit, uint32_t deadline)
{
    if (bit) {
        hw_i2c_sda_release();
    } else {
        hw_i2c_sda_low();
    }
    hw_delay_us(1u);
    if (!scl_high(deadline)) {
        return false;
    }
    scl_low();
    return true;
}

static bool read_bit(bool *bit, uint32_t deadline)
{
    hw_i2c_sda_release();
    hw_delay_us(1u);
    if (!scl_high(deadline)) {
        return false;
    }
    *bit = hw_i2c_sda_read();
    scl_low();
    return true;
}

static bool i2c_start(uint32_t deadline)
{
    hw_i2c_sda_release();
    if (!scl_high(deadline)) {
        return false;
    }
    if (!hw_i2c_sda_read()) {
        return false; /* лінію тримає хтось інший */
    }
    hw_i2c_sda_low();
    hw_delay_us(I2C_HALF_BIT_US);
    scl_low();
    return true;
}

static void i2c_stop(void)
{
    hw_i2c_sda_low();
    hw_delay_us(I2C_HALF_BIT_US);
    hw_i2c_scl_release();
    hw_delay_us(I2C_HALF_BIT_US);
    hw_i2c_sda_release();
    hw_delay_us(I2C_HALF_BIT_US);
}

static bool write_byte(uint8_t b, bool *ack, uint32_t deadline)
{
    bool nack = true;

    for (int i = 7; i >= 0; i--) {
        if (!write_bit(((b >> i) & 1u) != 0u, deadline)) {
            return false;
        }
    }
    if (!read_bit(&nack, deadline)) {
        return false;
    }
    *ack = !nack; /* ведений притискає SDA до нуля — це і є ACK */
    return true;
}

/* Ведений завис із SDA у нулі: дев'ять тактів SCL дають йому додати
   недоотримані біти й відпустити лінію. Класичний прийом відновлення. */
static bool bus_recover(uint32_t deadline)
{
    if (hw_i2c_sda_read()) {
        return true;
    }
    for (int i = 0; i < 9 && !hw_i2c_sda_read(); i++) {
        if (!scl_high(deadline)) {
            return false;
        }
        scl_low();
    }
    if (!hw_i2c_sda_read()) {
        return false; /* шина прибита намертво — це вже FAULT плати */
    }
    i2c_stop();
    return true;
}

bool hw_i2c_probe_device(uint8_t addr_7bit)
{
    uint32_t deadline = hw_get_tick_ms() + I2C_TIMEOUT_MS;
    bool     ack      = false;

    hw_i2c_sda_release();
    hw_i2c_scl_release();

    if (bus_recover(deadline) && i2c_start(deadline)) {
        (void)write_byte((uint8_t)(addr_7bit << 1), &ack, deadline); /* біт 0 = запис */
    }
    /* Виходимо ЗАВЖДИ через stop і відпущені лінії — байдуже, на якому
       кроці нас спинив тайм-аут. Інакше шина лишиться захопленою. */
    i2c_stop();
    hw_i2c_sda_release();
    hw_i2c_scl_release();
    return ack;
}

bool bist_run(bist_report_t *rep)
{
    memset(rep, 0, sizeof *rep);

    if (!hw_bus_try_lock(BUS_LOCK_TIMEOUT_MS)) {
        return false; /* шину тримає робоча задача — не заважаємо */
    }
    rep->bus_free  = hw_i2c_sda_read() && hw_i2c_scl_read();
    rep->rtc_ok    = hw_i2c_probe_device(I2C_ADDR_RTC);
    rep->eeprom_ok = hw_i2c_probe_device(I2C_ADDR_EEPROM);
    hw_bus_unlock();

    rep->adc0_raw = hw_adc_read_raw(0);
    /* Цілочисельно: у сервісній задачі плаваюча кома не потрібна. */
    rep->adc0_mv  = (uint16_t)(((uint32_t)rep->adc0_raw * ADC_VREF_MV) / ADC_FULL_SCALE);
    return true;
}
