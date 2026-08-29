#include <stddef.h>

#include "chip_io.h"
#include "chip_regops.h"

uint8_t *chip_reg_shadow(chip_dev_t *dev, uint8_t reg)
{
    if (dev == NULL) {
        return NULL;
    }
    switch (reg) {
    case CHIP_REG_CTRL_REG1: return &dev->shadow_ctrl1;
    case CHIP_REG_CTRL_REG3: return &dev->shadow_ctrl3;
    case CHIP_REG_CTRL_REG4: return &dev->shadow_ctrl4;
    case CHIP_REG_CTRL_REG5: return &dev->shadow_ctrl5;
    case CHIP_REG_FIFO_CTRL: return &dev->shadow_fifo_ctrl;
    default:                 return NULL;
    }
}

chip_status_t chip_reg_write(chip_dev_t *dev, uint8_t reg, uint8_t value)
{
    chip_status_t st = chip_io_write_byte(dev, reg, value);
    if (st != CHIP_OK) {
        return st; /* тінь лишається старою: у кремнії нічого не змінилося */
    }

    uint8_t *shadow = chip_reg_shadow(dev, reg);
    if (shadow != NULL) {
        *shadow = value;
    }
    return CHIP_OK;
}

chip_status_t chip_reg_update_field(chip_dev_t *dev, uint8_t reg,
                                    uint8_t mask, uint8_t shift, uint8_t value)
{
    if (dev == NULL || mask == 0u) {
        return CHIP_ERR_INVALID_PARAM;
    }

    uint8_t *shadow = chip_reg_shadow(dev, reg);
    if (shadow == NULL) {
        /* Поле в нетіньовому регістрі оновлювати не можна: прочитати його
         * заради RMW означає ризикнути прапорцями clear-on-read. */
        return CHIP_ERR_INVALID_PARAM;
    }

    uint8_t shifted = (uint8_t)((uint8_t)(value << shift) & mask);
    if ((uint8_t)(shifted >> shift) != value) {
        return CHIP_ERR_INVALID_PARAM; /* значення не влазить у поле */
    }

    uint8_t new_val = (uint8_t)((*shadow & (uint8_t)~mask) | shifted);
    return chip_reg_write(dev, reg, new_val);
}

chip_status_t chip_reg_set_bits(chip_dev_t *dev, uint8_t reg, uint8_t bits)
{
    uint8_t *shadow = chip_reg_shadow(dev, reg);
    if (shadow == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    return chip_reg_write(dev, reg, (uint8_t)(*shadow | bits));
}

chip_status_t chip_reg_clear_bits(chip_dev_t *dev, uint8_t reg, uint8_t bits)
{
    uint8_t *shadow = chip_reg_shadow(dev, reg);
    if (shadow == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }
    return chip_reg_write(dev, reg, (uint8_t)(*shadow & (uint8_t)~bits));
}

chip_status_t chip_reg_read_burst(chip_dev_t *dev, uint8_t start_reg,
                                  uint8_t *buf, uint16_t len)
{
    if (buf == NULL || len == 0u) {
        return CHIP_ERR_INVALID_PARAM;
    }

    uint8_t addr = start_reg;
    if (len > 1u) {
        addr = (uint8_t)(start_reg | CHIP_ADDR_AUTOINC);
    }
    return chip_io_read(dev, addr, buf, len);
}

chip_status_t chip_reg_sync_shadow(chip_dev_t *dev)
{
    static const uint8_t readable_config[] = {
        CHIP_REG_CTRL_REG1, CHIP_REG_CTRL_REG3, CHIP_REG_CTRL_REG4,
        CHIP_REG_CTRL_REG5, CHIP_REG_FIFO_CTRL
    };

    for (size_t i = 0; i < sizeof(readable_config) / sizeof(readable_config[0]); ++i) {
        uint8_t reg = readable_config[i];
        uint8_t value = 0u;
        chip_status_t st = chip_io_read_byte(dev, reg, &value);
        if (st != CHIP_OK) {
            return st;
        }
        uint8_t *shadow = chip_reg_shadow(dev, reg);
        if (shadow != NULL) {
            *shadow = value;
        }
    }
    return CHIP_OK;
}
