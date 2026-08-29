#include "sht3x.h"
#include "crc8.h"

/* Команди чипа (старший байт передається першим). */
#define SHT3X_CMD_STATUS     0xF32Du
#define SHT3X_CMD_HEATER_ON  0x306Du
#define SHT3X_CMD_HEATER_OFF 0x3066u

#define SHT3X_POR_DELAY_MS   5u   /* t_POR = 0.5..1.0 мс, беремо запас */
#define SHT3X_RETRY_DELAY_MS 30u  /* пауза між повторами після збою */

struct meas_profile {
    uint16_t cmd;
    uint32_t duration_ms;
};

/* Режим без утримання тактової лінії: SCL лишається вільною, паузу
   відлічує мікроконтролер. До верхньої межі t_meas додано 1 мс запасу —
   інакше сенсор відповість NACK на передчасне читання. */
static const struct meas_profile k_profiles[3] = {
    { 0x2400u, 16u },   /* High   */
    { 0x240Bu,  7u },   /* Medium */
    { 0x2416u,  5u }    /* Low    */
};

static bool handle_is_valid(const sht3x_t *dev)
{
    return dev != NULL && dev->i2c_write != NULL &&
           dev->i2c_read != NULL && dev->delay_ms != NULL;
}

static uint16_t be16(const uint8_t *p)
{
    return (uint16_t)(((uint16_t)p[0] << 8) | (uint16_t)p[1]);
}

static sht3x_status_t send_command(sht3x_t *dev, uint16_t cmd)
{
    const uint8_t buf[2] = { (uint8_t)(cmd >> 8), (uint8_t)(cmd & 0xFFu) };

    if (!dev->i2c_write(dev->addr7, buf, sizeof buf, dev->ctx)) {
        dev->bus_errors++;
        return SHT3X_ERR_I2C_WRITE;
    }
    return SHT3X_OK;
}

sht3x_status_t sht3x_init(sht3x_t *dev)
{
    if (!handle_is_valid(dev)) {
        return SHT3X_ERR_PARAM;
    }
    if (dev->addr7 != SHT3X_ADDR_GND && dev->addr7 != SHT3X_ADDR_VDD) {
        return SHT3X_ERR_PARAM;
    }

    dev->bus_errors = 0u;
    dev->crc_errors = 0u;

    /* Поки не мине POR, чип не відповідає навіть на власну адресу. */
    dev->delay_ms(SHT3X_POR_DELAY_MS, dev->ctx);

    uint16_t status = 0u;
    sht3x_status_t st = sht3x_read_status(dev, &status);

    if (st == SHT3X_ERR_I2C_WRITE || st == SHT3X_ERR_I2C_READ) {
        /* Мовчання на шині — це не «збій обміну», а відсутній чип:
           переплутані SDA/SCL, немає підтяжок або не той вивід ADDR. */
        return SHT3X_ERR_NO_DEVICE;
    }
    return st;
}

sht3x_status_t sht3x_measure(sht3x_t *dev, sht3x_rep_t rep, sht3x_meas_t *out)
{
    if (!handle_is_valid(dev) || out == NULL) {
        return SHT3X_ERR_PARAM;
    }
    if ((unsigned)rep > (unsigned)SHT3X_REP_LOW) {
        return SHT3X_ERR_PARAM;
    }

    const struct meas_profile *p = &k_profiles[(unsigned)rep];

    sht3x_status_t st = send_command(dev, p->cmd);
    if (st != SHT3X_OK) {
        return st;
    }

    dev->delay_ms(p->duration_ms, dev->ctx);

    uint8_t rx[6] = { 0 };
    if (!dev->i2c_read(dev->addr7, rx, sizeof rx, dev->ctx)) {
        dev->bus_errors++;
        return SHT3X_ERR_I2C_READ;
    }

    /* Кадр захищено двома незалежними сумами; хибна — відкидаємо ОБИДВА
       значення, бо завада на шині псує будь-який біт кадру. */
    if (!sht3x_crc8_check(&rx[0], rx[2])) {
        dev->crc_errors++;
        return SHT3X_ERR_CRC_TEMP;
    }
    if (!sht3x_crc8_check(&rx[3], rx[5])) {
        dev->crc_errors++;
        return SHT3X_ERR_CRC_HUMI;
    }

    out->raw_t  = be16(&rx[0]);
    out->raw_rh = be16(&rx[3]);

    /* T[м°C] = -45000 + 175000 * S_T / 65535. Коефіцієнти скорочено на 5:
       175000/65535 = 35000/13107, і найбільший проміжний добуток
       35000 * 65535 = 2 293 725 000 уже вміщається в uint32_t. Тож ані
       64-бітної арифметики, ані емуляції float на Cortex-M0 не треба. */
    out->temperature_mc = -45000 + (int32_t)((35000UL * (uint32_t)out->raw_t) / 13107UL);

    /* RH[0.01 %] = 10000 * S_RH / 65535; 10000 * 65535 = 655 350 000. */
    out->humidity_cpm = (uint32_t)((10000UL * (uint32_t)out->raw_rh) / 65535UL);

    return SHT3X_OK;
}

sht3x_status_t sht3x_measure_retry(sht3x_t *dev, sht3x_rep_t rep,
                                   sht3x_meas_t *out, uint8_t attempts)
{
    if (!handle_is_valid(dev) || out == NULL || attempts == 0u) {
        return SHT3X_ERR_PARAM;
    }

    sht3x_status_t st = SHT3X_ERR_PARAM;

    for (uint8_t i = 0u; i < attempts; ++i) {
        if (i > 0u) {
            dev->delay_ms(SHT3X_RETRY_DELAY_MS, dev->ctx);
        }
        st = sht3x_measure(dev, rep, out);
        if (st == SHT3X_OK || st == SHT3X_ERR_PARAM) {
            return st;
        }
    }
    return st;
}

sht3x_status_t sht3x_heater(sht3x_t *dev, bool on)
{
    if (!handle_is_valid(dev)) {
        return SHT3X_ERR_PARAM;
    }
    return send_command(dev, on ? SHT3X_CMD_HEATER_ON : SHT3X_CMD_HEATER_OFF);
}

sht3x_status_t sht3x_read_status(sht3x_t *dev, uint16_t *status)
{
    if (!handle_is_valid(dev) || status == NULL) {
        return SHT3X_ERR_PARAM;
    }

    sht3x_status_t st = send_command(dev, SHT3X_CMD_STATUS);
    if (st != SHT3X_OK) {
        return st;
    }

    uint8_t rx[3] = { 0 };
    if (!dev->i2c_read(dev->addr7, rx, sizeof rx, dev->ctx)) {
        dev->bus_errors++;
        return SHT3X_ERR_I2C_READ;
    }
    if (!sht3x_crc8_check(&rx[0], rx[2])) {
        dev->crc_errors++;
        return SHT3X_ERR_CRC_STATUS;
    }

    *status = be16(&rx[0]);
    return SHT3X_OK;
}

const char *sht3x_strerror(sht3x_status_t st)
{
    switch (st) {
    case SHT3X_OK:             return "ok";
    case SHT3X_ERR_PARAM:      return "hybnyi arhument";
    case SHT3X_ERR_NO_DEVICE:  return "chyp ne vidpovidaie";
    case SHT3X_ERR_I2C_WRITE:  return "zbii zapysu I2C";
    case SHT3X_ERR_I2C_READ:   return "zbii chytannia I2C";
    case SHT3X_ERR_CRC_TEMP:   return "CRC temperatury";
    case SHT3X_ERR_CRC_HUMI:   return "CRC volohosti";
    case SHT3X_ERR_CRC_STATUS: return "CRC rehistra stanu";
    default:                   return "nevidoma pomylka";
    }
}
