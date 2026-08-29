#include <stddef.h>

#include "chip_io.h"

/* Пауза перед повторною спробою: 1, 2, 4, 8 мс — щоб короткий сплеск завади
 * (комутація реле, пуск інвертора) устиг закінчитися, а система не стояла. */
static void backoff_delay(const chip_dev_t *dev, uint8_t attempt)
{
    uint32_t base = dev->retry_delay_ms ? dev->retry_delay_ms : 1u;
    uint32_t factor = 1u;
    for (uint8_t i = 0; i < attempt && i < 4u; ++i) {
        factor *= 2u;
    }
    dev->bus_ops->delay_ms(base * factor);
}

static bool ops_are_valid(const chip_dev_t *dev)
{
    return dev != NULL && dev->bus_ops != NULL &&
           dev->bus_ops->read != NULL &&
           dev->bus_ops->write != NULL &&
           dev->bus_ops->delay_ms != NULL;
}

chip_status_t chip_io_read(chip_dev_t *dev, uint8_t reg, uint8_t *data, uint16_t len)
{
    if (!ops_are_valid(dev) || data == NULL || len == 0u) {
        return CHIP_ERR_INVALID_PARAM;
    }

    for (uint8_t attempt = 0; attempt <= dev->max_retries; ++attempt) {
        if (attempt > 0u) {
            backoff_delay(dev, (uint8_t)(attempt - 1u));
        }
        int32_t res = dev->bus_ops->read(dev->user_ctx, dev->dev_addr, reg, data, len);
        if (res == 0) {
            return CHIP_OK;
        }
    }
    return CHIP_ERR_COMM;
}

chip_status_t chip_io_write(chip_dev_t *dev, uint8_t reg, const uint8_t *data, uint16_t len)
{
    if (!ops_are_valid(dev) || data == NULL || len == 0u) {
        return CHIP_ERR_INVALID_PARAM;
    }

    for (uint8_t attempt = 0; attempt <= dev->max_retries; ++attempt) {
        if (attempt > 0u) {
            backoff_delay(dev, (uint8_t)(attempt - 1u));
        }
        int32_t res = dev->bus_ops->write(dev->user_ctx, dev->dev_addr, reg, data, len);
        if (res == 0) {
            return CHIP_OK;
        }
    }
    return CHIP_ERR_COMM;
}

chip_status_t chip_io_read_byte(chip_dev_t *dev, uint8_t reg, uint8_t *value)
{
    if (value == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    return chip_io_read(dev, reg, value, 1u);
}

chip_status_t chip_io_write_byte(chip_dev_t *dev, uint8_t reg, uint8_t value)
{
    return chip_io_write(dev, reg, &value, 1u);
}

chip_status_t chip_io_wait_flag(chip_dev_t *dev, uint8_t reg, uint8_t mask,
                                uint32_t timeout_ms, uint32_t poll_interval_ms)
{
    if (!ops_are_valid(dev) || mask == 0u) {
        return CHIP_ERR_INVALID_PARAM;
    }
    if (poll_interval_ms == 0u) {
        poll_interval_ms = 1u;
    }

    uint32_t elapsed = 0u;
    for (;;) {
        uint8_t value = 0u;
        chip_status_t st = chip_io_read_byte(dev, reg, &value);
        if (st != CHIP_OK) {
            return st; /* шина мовчить — це не тайм-аут очікування даних */
        }
        if ((value & mask) != 0u) {
            return CHIP_OK;
        }
        if (elapsed >= timeout_ms) {
            return CHIP_ERR_TIMEOUT;
        }
        dev->bus_ops->delay_ms(poll_interval_ms);
        elapsed += poll_interval_ms;
    }
}
