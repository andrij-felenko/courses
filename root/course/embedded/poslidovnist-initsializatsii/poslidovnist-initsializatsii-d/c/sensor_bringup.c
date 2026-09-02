#include <stdio.h>

#include "platform.h"
#include "sensor.h"

#define MAX_ATTEMPTS    3U
#define BACKOFF_BASE_MS 50U

const char *init_result_str(init_result_t result)
{
    switch (result) {
    case INIT_OK:            return "успіх";
    case INIT_ERR_BUS:       return "збій шини (NACK або залипла SDA)";
    case INIT_ERR_TIMEOUT:   return "таймаут готовності";
    case INIT_ERR_WRONG_ID:  return "невідповідний CHIP_ID";
    case INIT_ERR_VERIFY:    return "Read-Back не підтвердив конфігурацію";
    default:                 return "невідома помилка";
    }
}

/* Одна повна спроба підйому: скидання -> ідентифікатор -> конфігурація */
static init_result_t bringup_attempt(sensor_t *dev)
{
    init_result_t rc = sensor_software_reset(dev->addr);
    if (rc != INIT_OK) {
        return rc;
    }

    rc = sensor_check_id(dev->addr);
    if (rc != INIT_OK) {
        return rc;
    }

    uint8_t failed_reg = 0;
    rc = sensor_apply_config(dev->addr, &failed_reg);
    if (rc != INIT_OK && failed_reg != 0) {
        printf("      регістр 0x%02X не прийняв конфігурацію\n", failed_reg);
    }
    return rc;
}

/*
 * Відкат стану: спершу глушимо переривання, інакше зависла лінія INT
 * довбатиме процесор нескінченними хибними спрацюваннями.
 */
void sensor_rollback(sensor_t *dev, init_result_t reason)
{
    (void)i2c_write_reg(dev->addr, REG_INT_EN, 0x00U);
    (void)i2c_write_reg(dev->addr, REG_PWR, PWR_MODE_STANDBY);
    dev->state = DEVICE_STATE_FAULT;
    dev->last_error = reason;
}

init_result_t sensor_bringup(sensor_t *dev)
{
    dev->state = DEVICE_STATE_UNINITIALIZED;
    dev->last_error = INIT_OK;
    dev->attempts_used = 0;

    for (uint8_t k = 1; k <= MAX_ATTEMPTS; ++k) {
        dev->attempts_used = k;

        /* Нульова фаза повтору: розчистити шину після невдалої спроби */
        if (k > 1) {
            i2c_bus_recover(dev->addr);
        }

        init_result_t rc = bringup_attempt(dev);
        if (rc == INIT_OK) {
            dev->state = DEVICE_STATE_READY;
            dev->last_error = INIT_OK;
            return INIT_OK;
        }

        dev->last_error = rc;
        printf("      спроба %u: %s\n", (unsigned)k, init_result_str(rc));

        /* Не той кремній на адресі — повтори тут безглузді */
        if (rc == INIT_ERR_WRONG_ID) {
            break;
        }

        if (k < MAX_ATTEMPTS) {
            uint32_t backoff = BACKOFF_BASE_MS << (k - 1U); /* 50 -> 100 -> 200 мс */
            delay_ms(backoff);
        }
    }

    sensor_rollback(dev, dev->last_error);
    return dev->last_error;
}
