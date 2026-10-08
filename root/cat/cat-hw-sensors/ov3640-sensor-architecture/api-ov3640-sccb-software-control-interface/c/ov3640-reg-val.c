#include <stdint.h>
#include <stdbool.h>

#define OV3640_REG_CHIP_ID_HIGH  0x300A
#define OV3640_REG_CHIP_ID_LOW   0x300B
#define OV3640_CHIP_ID           0x3640
#define OV3640_REG_RESET         0x3012

struct ov3640_reg_val {
    uint8_t bank;
    uint16_t reg;
    uint8_t val;
};

// Базова таблиця конфігурації за замовчуванням
static const struct ov3640_reg_val default_init_regs[] = {
    {OV3640_BANK_SENSOR, 0x3010, 0x00},
    {OV3640_BANK_DSP,    0x3600, 0x04},
    {OV3640_BANK_DSP,    0x3601, 0x30},
    // Додаткові регістри кадрування та посилення
};

extern void delay_ms(uint32_t ms);

int ov3640_check_chip_id(void) {
    uint8_t id_h = 0, id_l = 0;
    int ret = ov3640_read_reg(OV3640_BANK_SENSOR, OV3640_REG_CHIP_ID_HIGH, &id_h);
    if (ret != 0) return ret;
    ret = ov3640_read_reg(OV3640_BANK_SENSOR, OV3640_REG_CHIP_ID_LOW, &id_l);
    if (ret != 0) return ret;

    uint16_t chip_id = ((uint16_t)id_h << 8) | id_l;
    if (chip_id != OV3640_CHIP_ID) {
        return -1; // Невідповідність CHIP ID
    }
    return 0;
}

int ov3640_write_array(const struct ov3640_reg_val *table, size_t count) {
    for (size_t i = 0; i < count; i++) {
        int ret = ov3640_write_reg(table[i].bank, table[i].reg, table[i].val);
        if (ret != 0) {
            return ret;
        }
    }
    return 0;
}

int ov3640_init(void) {
    // 1. Програмне скидання
    int ret = ov3640_write_reg(OV3640_BANK_SENSOR, OV3640_REG_RESET, 0x80);
    if (ret != 0) return ret;
    delay_ms(10);

    // 2. Перевірка ідентифікатора
    ret = ov3640_check_chip_id();
    if (ret != 0) return ret;

    // 3. Завантаження базової конфігурації
    size_t reg_count = sizeof(default_init_regs) / sizeof(default_init_regs[0]);
    return ov3640_write_array(default_init_regs, reg_count);
}
