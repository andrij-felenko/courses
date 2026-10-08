#include <stdint.h>
#include <stdbool.h>

#define OV2640_SCCB_ADDR   0x30
#define REG_BANK_SEL       0xFF
#define BANK_SENSOR        0x01
#define REG_COM7           0x12
#define REG_CLKRC          0x11
#define COM7_SW_RESET      0x80

// Зовнішня функція запису регістра по шині SCCB
extern bool sccb_write_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t val);

bool ov2640_clock_init(void) {
    // 1. Переключення на банк сенсорного ядра
    if (!sccb_write_reg(OV2640_SCCB_ADDR, REG_BANK_SEL, BANK_SENSOR)) {
        return false;
    }

    // 2. Виконання програмного скидання
    if (!sccb_write_reg(OV2640_SCCB_ADDR, REG_COM7, COM7_SW_RESET)) {
        return false;
    }

    // Затримка на перезапуск внутрішніх вузлів
    // delay_ms(5);

    // 3. Повторний вибір банку сенсора після скидання
    sccb_write_reg(OV2640_SCCB_ADDR, REG_BANK_SEL, BANK_SENSOR);

    // 4. Налаштування дільника CLKRC (XCLK = 24 МГц, PCLK = 24 МГц, PLL увімкнено)
    // Біт 7 = 0 (PLL увімкнено), біти 5:0 = 0x01 (дільник = 2)
    if (!sccb_write_reg(OV2640_SCCB_ADDR, REG_CLKRC, 0x01)) {
        return false;
    }

    return true;
}
