/* chip_driver.c — реалізація драйвера, що його перевіряють тести.
 *
 * Тут живуть три речі, заради яких і потрібен мок: бітові маски конфігурації,
 * політика повторних спроб і математика переходу до SI. Жодна з них не
 * потребує кремнію, тому всі три перевіряються на ПК за мікросекунди.
 */
#include "chip_driver.h"

#include <string.h>

#include "chip_regs.h"

#define CHIP_DEFAULT_RETRIES   3u
#define CHIP_DEFAULT_RETRY_MS  1u

const char *chip_status_str(chip_status_t status)
{
    switch (status) {
    case CHIP_OK:                return "OK";
    case CHIP_ERR_INVALID_PARAM: return "INVALID_PARAM";
    case CHIP_ERR_COMM:          return "COMM";
    case CHIP_ERR_NOT_FOUND:     return "DEVICE_NOT_FOUND";
    case CHIP_ERR_NOT_INIT:      return "NOT_INITIALIZED";
    case CHIP_ERR_NO_DATA:       return "NO_DATA";
    default:                     return "UNKNOWN";
    }
}

/* Одна транзакція з політикою повторів: збій шини сам по собі ще не аварія,
 * бо на реальній платі це буває від наведення чи від зайнятого чипа. Пауза
 * подвоюється, щоб не забивати шину рівномірним частоколом спроб. */
static chip_status_t bus_read_retry(chip_dev_t *dev, uint8_t reg,
                                    uint8_t *buf, uint16_t len)
{
    if (len > 1u) {
        reg |= CHIP_REG_AUTO_INC;
    }

    uint32_t delay = dev->retry_delay_ms;
    for (uint8_t attempt = 0; attempt <= dev->max_retries; ++attempt) {
        int32_t rc = dev->bus_ops->read(dev->user_ctx, dev->dev_addr, reg, buf, len);
        if (rc == 0) {
            return CHIP_OK;
        }
        if (attempt == dev->max_retries) {
            break;
        }
        if (dev->bus_ops->delay_ms != NULL) {
            dev->bus_ops->delay_ms(delay);
        }
        delay *= 2u;
    }
    return CHIP_ERR_COMM;
}

static chip_status_t bus_write_retry(chip_dev_t *dev, uint8_t reg, uint8_t value)
{
    uint32_t delay = dev->retry_delay_ms;
    for (uint8_t attempt = 0; attempt <= dev->max_retries; ++attempt) {
        int32_t rc = dev->bus_ops->write(dev->user_ctx, dev->dev_addr, reg, &value, 1u);
        if (rc == 0) {
            return CHIP_OK;
        }
        if (attempt == dev->max_retries) {
            break;
        }
        if (dev->bus_ops->delay_ms != NULL) {
            dev->bus_ops->delay_ms(delay);
        }
        delay *= 2u;
    }
    return CHIP_ERR_COMM;
}

chip_status_t chip_init(chip_dev_t *dev, const chip_bus_ops_t *bus_ops,
                        void *user_ctx, uint8_t dev_addr)
{
    if (dev == NULL || bus_ops == NULL ||
        bus_ops->read == NULL || bus_ops->write == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    memset(dev, 0, sizeof(*dev));
    dev->bus_ops        = bus_ops;
    dev->user_ctx       = user_ctx;
    dev->dev_addr       = dev_addr;
    dev->max_retries    = CHIP_DEFAULT_RETRIES;
    dev->retry_delay_ms = CHIP_DEFAULT_RETRY_MS;

    /* Крок 1. Упевнитися, що на цій адресі справді наш чип. Поки цього не
     * доведено, жодного запису в конфігурацію не робимо: писати маски в
     * невідомий кремній — найшвидший спосіб перевести чужий пристрій у
     * режим, з якого його доведеться діставати перезапуском живлення. */
    uint8_t who = 0u;
    chip_status_t st = bus_read_retry(dev, CHIP_REG_WHO_AM_I, &who, 1u);
    if (st != CHIP_OK) {
        return st;
    }
    if (who != CHIP_WHO_AM_I_VALUE) {
        return CHIP_ERR_NOT_FOUND;
    }

    /* Крок 2. Частота вибірки й дозвіл трьох осей. */
    uint8_t ctrl1 = (uint8_t)((CHIP_ODR_100_HZ << CTRL1_ODR_SHIFT) | CTRL1_XYZ_EN);
    st = bus_write_retry(dev, CHIP_REG_CTRL1, ctrl1);
    if (st != CHIP_OK) {
        return st;
    }

    /* Крок 3. BDU не дає чипу підмінити старший байт, поки ми читаємо
     * молодший, а HR вмикає повні 16 біт. Діапазон за замовчуванням ±2 g. */
    uint8_t ctrl4 = (uint8_t)(CTRL4_BDU | CTRL4_HR |
                              (chip_range_to_fs(2u) << CTRL4_FS_SHIFT));
    st = bus_write_retry(dev, CHIP_REG_CTRL4, ctrl4);
    if (st != CHIP_OK) {
        return st;
    }

    dev->shadow_ctrl1   = ctrl1;
    dev->shadow_ctrl4   = ctrl4;
    dev->active_range   = 2u;
    dev->scale_factor   = chip_scale_si(2u);
    dev->is_initialized = true;
    return CHIP_OK;
}

chip_status_t chip_set_range(chip_dev_t *dev, uint8_t range_g)
{
    if (dev == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }

    uint8_t fs = chip_range_to_fs(range_g);
    if (fs == 0xFFu) {
        return CHIP_ERR_INVALID_PARAM;
    }

    /* Читання-модифікація-запис іде з тіні в ОЗП, а не з кремнію: інакше
     * кожна зміна діапазону коштувала б зайвої транзакції, а збій на її
     * читанні затер би сусідні біти регістра випадковим сміттям. */
    uint8_t ctrl4 = (uint8_t)((dev->shadow_ctrl4 & (uint8_t)~CTRL4_FS_MASK) |
                              (uint8_t)(fs << CTRL4_FS_SHIFT));

    chip_status_t st = bus_write_retry(dev, CHIP_REG_CTRL4, ctrl4);
    if (st != CHIP_OK) {
        return st; /* тінь не чіпаємо: у кремнії лишився старий діапазон */
    }

    dev->shadow_ctrl4 = ctrl4;
    dev->active_range = range_g;
    dev->scale_factor = chip_scale_si(range_g);
    return CHIP_OK;
}

chip_status_t chip_read_sample_si(chip_dev_t *dev, chip_axes_data_si_t *data_si)
{
    if (dev == NULL || data_si == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }

    uint8_t status = 0u;
    chip_status_t st = bus_read_retry(dev, CHIP_REG_STATUS, &status, 1u);
    if (st != CHIP_OK) {
        return st;
    }
    if ((status & STATUS_ZYXDA) == 0u) {
        return CHIP_ERR_NO_DATA; /* відлік ще не готовий — не старий віддавати */
    }

    uint8_t buf[6] = {0};
    st = bus_read_retry(dev, CHIP_REG_OUT_X_L, buf, sizeof(buf));
    if (st != CHIP_OK) {
        return st; /* вихідну структуру не чіпаємо: у ній лишається старе */
    }

    /* Порядок байтів на шині — молодший першим; знак розширюється сам,
     * щойно пара байтів складена в int16_t. */
    int16_t raw[3];
    for (int axis = 0; axis < 3; ++axis) {
        uint16_t word = (uint16_t)((uint16_t)buf[axis * 2 + 1] << 8) |
                        (uint16_t)buf[axis * 2];
        raw[axis] = (int16_t)word;
    }

    data_si->x = (float)raw[0] * dev->scale_factor;
    data_si->y = (float)raw[1] * dev->scale_factor;
    data_si->z = (float)raw[2] * dev->scale_factor;
    return CHIP_OK;
}

chip_status_t chip_soft_reset(chip_dev_t *dev)
{
    if (dev == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (!dev->is_initialized) {
        return CHIP_ERR_NOT_INIT;
    }

    /* Спершу зупиняємо перетворення, потім повертаємо конфігурацію з тіні:
     * після відновлення шини кремній мусить прокинутись у тому самому
     * режимі, у якому його бачить решта прошивки. */
    chip_status_t st = bus_write_retry(dev, CHIP_REG_CTRL1,
                                       (uint8_t)(CHIP_ODR_POWER_DOWN << CTRL1_ODR_SHIFT));
    if (st != CHIP_OK) {
        return st;
    }
    if (dev->bus_ops->delay_ms != NULL) {
        dev->bus_ops->delay_ms(5u);
    }

    st = bus_write_retry(dev, CHIP_REG_CTRL4, dev->shadow_ctrl4);
    if (st != CHIP_OK) {
        return st;
    }
    return bus_write_retry(dev, CHIP_REG_CTRL1, dev->shadow_ctrl1);
}
