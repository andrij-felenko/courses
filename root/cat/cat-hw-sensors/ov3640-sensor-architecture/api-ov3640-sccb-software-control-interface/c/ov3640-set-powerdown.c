#include <stdint.h>
#include <errno.h>

#define OV3640_ERR_OK        0
#define OV3640_ERR_NACK     -EIO
#define OV3640_ERR_TIMEOUT  -ETIMEDOUT

#define OV3640_REG_PWR_CTRL  0x3008

int ov3640_set_powerdown(bool enable) {
    uint8_t pwr_val = enable ? 0x80 : 0x00;
    int ret = ov3640_write_reg(OV3640_BANK_SENSOR, OV3640_REG_PWR_CTRL, pwr_val);
    if (ret != 0) {
        return OV3640_ERR_NACK;
    }
    if (!enable) {
        delay_ms(5); // Пауза для відновлення PLL після виходу з Powerdown
    }
    return OV3640_ERR_OK;
}

int ov3640_safe_write(uint8_t bank, uint16_t reg, uint8_t val) {
    int attempts = 3;
    while (attempts--) {
        int ret = ov3640_write_reg(bank, reg, val);
        if (ret == 0) {
            return OV3640_ERR_OK;
        }
        if (ret == -ETIMEDOUT) {
            return OV3640_ERR_TIMEOUT;
        }
    }
    return OV3640_ERR_NACK; // Усі спроби завершилися помилкою NACK
}
