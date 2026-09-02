#include "platform.h"
#include "sensor.h"

#define SW_RESET_QUIET_MS   5U  /* мінімальна тиша після команди скидання */
#define SW_RESET_TIMEOUT_MS 50U /* стеля очікування готовності */
#define POLL_STEP_MS        2U  /* інтервал між опитуваннями */

/*
 * Програмне скидання з опитуванням готовності. Ключове місце — реакція на NACK:
 * поки чип усередині скидання, він відключає інтерфейсний блок і НЕ підтверджує
 * адресу. Це нормальна відповідь, а не фатальна помилка шини; фатальним є лише
 * вичерпаний таймаут або притиснута SDA.
 */
init_result_t sensor_software_reset(uint8_t dev_addr)
{
    if (i2c_write_reg(dev_addr, REG_RESET_CTRL, BIT_SW_RESET) != BUS_OK) {
        return INIT_ERR_BUS;
    }

    delay_ms(SW_RESET_QUIET_MS);

    uint32_t start = platform_get_millis();
    for (;;) {
        uint8_t ctrl = 0;
        uint8_t status = 0;
        int rc_ctrl = i2c_read_reg(dev_addr, REG_RESET_CTRL, &ctrl);
        int rc_status = i2c_read_reg(dev_addr, REG_STATUS, &status);

        if (rc_ctrl == BUS_OK && rc_status == BUS_OK) {
            bool reset_done = (ctrl & BIT_SW_RESET) == 0;   /* біт самоочисний */
            bool device_ready = (status & BIT_STATUS_READY) != 0;
            if (reset_done && device_ready) {
                return INIT_OK;
            }
        } else if (rc_ctrl == BUS_ERR_STUCK || rc_status == BUS_ERR_STUCK) {
            return INIT_ERR_BUS; /* опитування залиплу лінію не розчистить */
        }

        if ((platform_get_millis() - start) >= SW_RESET_TIMEOUT_MS) {
            return INIT_ERR_TIMEOUT; /* захист від вічного while (busy) */
        }
        delay_ms(POLL_STEP_MS);
    }
}

/*
 * Верифікація ідентифікатора ловить три різні біди одним читанням: обірвану лінію
 * (0x00 або 0xFF), чужий пристрій на тій самій адресі й несумісну ревізію кремнію.
 */
init_result_t sensor_check_id(uint8_t dev_addr)
{
    uint8_t id = 0;
    if (i2c_read_reg(dev_addr, REG_WHO_AM_I, &id) != BUS_OK) {
        return INIT_ERR_BUS;
    }
    if (id != SENSOR_WHO_AM_I_VALUE) {
        return INIT_ERR_WRONG_ID;
    }
    return INIT_OK;
}

init_result_t sensor_data_ready(uint8_t dev_addr, bool *out_ready)
{
    uint8_t status = 0;
    if (i2c_read_reg(dev_addr, REG_STATUS, &status) != BUS_OK) {
        return INIT_ERR_BUS;
    }
    *out_ready = (status & BIT_STATUS_DRDY) != 0;
    return INIT_OK;
}
