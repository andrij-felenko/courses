#include <stdint.h>
#include <stdbool.h>

#define OV3640_SCCB_ADDR      0x78
#define OV3640_REG_BANK_SEL   0x3000
#define OV3640_BANK_DSP       0x00
#define OV3640_BANK_SENSOR    0x01

static uint8_t g_current_bank = 0xFF;

// Прототипи фізичного рівня SCCB
extern int sccb_write_bytes(uint8_t dev_addr, uint16_t reg_addr, uint8_t val);
extern int sccb_read_bytes(uint8_t dev_addr, uint16_t reg_addr, uint8_t *val);

int ov3640_set_bank(uint8_t bank) {
    if (g_current_bank == bank) {
        return 0; // Банк уже вибрано
    }
    int ret = sccb_write_bytes(OV3640_SCCB_ADDR, OV3640_REG_BANK_SEL, bank);
    if (ret == 0) {
        g_current_bank = bank;
    }
    return ret;
}

int ov3640_write_reg(uint8_t bank, uint16_t reg, uint8_t val) {
    int ret = ov3640_set_bank(bank);
    if (ret != 0) {
        return ret;
    }
    return sccb_write_bytes(OV3640_SCCB_ADDR, reg, val);
}

int ov3640_read_reg(uint8_t bank, uint16_t reg, uint8_t *val) {
    int ret = ov3640_set_bank(bank);
    if (ret != 0) {
        return ret;
    }
    return sccb_read_bytes(OV3640_SCCB_ADDR, reg, val);
}
