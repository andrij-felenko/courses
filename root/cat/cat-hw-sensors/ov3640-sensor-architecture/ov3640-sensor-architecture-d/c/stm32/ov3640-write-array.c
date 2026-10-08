#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Структура елемента конфігураційної таблиці OV3640
typedef struct {
    uint8_t bank;  // Номер сторінки (0x00 - 0x03)
    uint8_t reg;   // Адреса регістра (0x00 - 0xFE)
    uint8_t val;   // Байт даних
} ov3640_reg_entry_t;

// Спеціальний маркер затримки в таблиці
#define OV3640_TOK_DELAY 0xFF

extern bool sccb_write_bytes(uint8_t reg_addr, uint8_t data);
extern void delay_ms(uint32_t ms);

// Таблиця первинної ініціалізації OV3640 для режиму JPEG VGA (640x480)
static const ov3640_reg_entry_t ov3640_vga_jpeg_init_table[] = {
    // 1. М'яке скидання
    {0x00, 0x12, 0x80},
    {0x00, OV3640_TOK_DELAY, 10}, // Затримка 10 мс
    
    // 2. Налаштування PLL та тактування PCLK (Bank 0)
    {0x00, 0x0D, 0x04}, // PLL multiplier = 4
    {0x00, 0x0E, 0x01}, // PLL pre-divider
    {0x00, 0x10, 0x02}, // PCLK divider = 2
    {0x00, 0x11, 0x04}, // PCLK rising edge, VSYNC active high, HREF active high
    
    // 3. Формат виходу та ISP (Bank 1)
    {0x01, 0x12, 0x10}, // Увімкнення JPEG виходу
    {0x01, 0x36, 0x00}, // Активація автоматичного балансу білого (AWB)
    
    // 4. Геометрія скалера (Bank 2) - VGA (640x480)
    {0x02, 0x90, 0x02}, // Width High byte (640 = 0x0280)
    {0x02, 0x91, 0x80}, // Width Low byte
    {0x02, 0x92, 0x01}, // Height High byte (480 = 0x01E0)
    {0x02, 0x93, 0xE0}, // Height Low byte
};

// Запис таблиці конфігурації з оптимізацією перемикання банок
bool ov3640_write_array(const ov3640_reg_entry_t *table, size_t count) {
    uint8_t current_bank = 0xFF; // Невідомий початковий стан
    
    for (size_t i = 0; i < count; i++) {
        if (table[i].reg == OV3640_TOK_DELAY) {
            delay_ms(table[i].val);
            continue;
        }
        
        // Запис регістру 0xFF виконується лише при зміні банку
        if (table[i].bank != current_bank) {
            if (!sccb_write_bytes(0xFF, table[i].bank)) {
                return false; // Помилка шини SCCB
            }
            current_bank = table[i].bank;
        }
        
        if (!sccb_write_bytes(table[i].reg, table[i].val)) {
            return false;
        }
    }
    return true;
}
