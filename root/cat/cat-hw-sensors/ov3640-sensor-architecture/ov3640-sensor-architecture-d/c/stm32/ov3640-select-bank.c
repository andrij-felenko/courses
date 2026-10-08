#include <stdint.h>
#include <stdbool.h>

// Адреса регістра вибору банку в OV3640
#define OV3640_REG_BANK_SEL  0xFF

// Структура регістрової конфігурації
typedef struct {
    uint8_t bank;
    uint8_t reg;
    uint8_t val;
} ov3640_reg_cfg_t;

// Низькорівневий запис через SCCB (прототип)
extern bool sccb_write_reg(uint8_t reg, uint8_t val);

// Перемикання активної банки регістрів
bool ov3640_select_bank(uint8_t bank_number) {
    return sccb_write_reg(OV3640_REG_BANK_SEL, bank_number);
}

// Запис регістру із вказівкою банки
bool ov3640_write_bank_reg(uint8_t bank, uint8_t reg, uint8_t val) {
    if (!ov3640_select_bank(bank)) {
        return false;
    }
    return sccb_write_reg(reg, val);
}

// Ініціалізація вихідного режиму JPEG з заданим масштабуванням
bool ov3640_set_jpeg_mode(uint16_t width, uint16_t height) {
    // 1. Вибір банку ISP (Bank 1) для налаштування розмірів кадру
    if (!ov3640_write_bank_reg(0x01, 0x12, 0x10)) { // Увімкнення кодера JPEG
        return false;
    }
    
    // 2. Вибір банку скалера (Bank 2) та запис коефіцієнтів масштабування
    ov3640_write_bank_reg(0x02, 0x90, (uint8_t)(width >> 8));
    ov3640_write_bank_reg(0x02, 0x91, (uint8_t)(width & 0xFF));
    ov3640_write_bank_reg(0x02, 0x92, (uint8_t)(height >> 8));
    ov3640_write_bank_reg(0x02, 0x93, (uint8_t)(height & 0xFF));
    
    return true;
}
