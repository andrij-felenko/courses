#include <stdint.h>
#include <stdbool.h>

#define OV2640_SCCB_ADDR   0x30
#define OV2640_BANK_REG    0xFF

typedef enum {
    OV2640_BANK_DSP    = 0x00,
    OV2640_BANK_SENSOR = 0x01
} ov2640_bank_t;

static ov2640_bank_t current_bank = (ov2640_bank_t)0xFF;

// Низькорівневий запис одного байта через шину SCCB
int sccb_write_byte(uint8_t slv_addr, uint8_t reg_addr, uint8_t data);

// Встановлення активного банку регістрів
int ov2640_set_bank(ov2640_bank_t bank) {
    if (current_bank == bank) {
        return 0; // Банк вже активний, уникаємо зайвої транзакції
    }
    int ret = sccb_write_byte(OV2640_SCCB_ADDR, OV2640_BANK_REG, (uint8_t)bank);
    if (ret == 0) {
        current_bank = bank;
    }
    return ret;
}

// Запис значення в регістр з гарантованим вибором банку
int ov2640_write_reg(ov2640_bank_t bank, uint8_t reg, uint8_t val) {
    int ret = ov2640_set_bank(bank);
    if (ret != 0) {
        return ret;
    }
    return sccb_write_byte(OV2640_SCCB_ADDR, reg, val);
}
