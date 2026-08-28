#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void lcd_init(void) {
    // 0. Налаштувати ніжки на вихід — одним gpio_config на всі шість
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << LCD_RS) | (1ULL << LCD_E) |
                        (1ULL << LCD_D4) | (1ULL << LCD_D5) |
                        (1ULL << LCD_D6) | (1ULL << LCD_D7),
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));
    gpio_set_level(LCD_E, 0);

    vTaskDelay(pdMS_TO_TICKS(50));   // 1. чекаємо ≥ 40 мс після подачі живлення

    // 2. Тричі напівбайт 0011 — надійно завести у 8-бітний режим із будь-якого стану.
    //    Це ще НЕ повні байти: шлемо самі напівбайти, стробом кожен.
    gpio_set_level(LCD_RS, 0);
    put_nibble(0x03); pulse_e(); esp_rom_delay_us(5000);  // перший раз: > 4.1 мс
    put_nibble(0x03); pulse_e(); esp_rom_delay_us(150);   // другий: > 100 мкс
    put_nibble(0x03); pulse_e(); esp_rom_delay_us(150);   // третій

    // 3. Тепер напівбайт 0010 — перемкнути у 4-бітний режим.
    put_nibble(0x02); pulse_e(); esp_rom_delay_us(150);

    // 4. Звідси — вже ПОВНІ байти (send_byte ріже їх на два напівбайти).
    lcd_command(0x28);       // Function Set: 4 біти, 2 рядки, шрифт 5×8
    lcd_command(0x08);       // Display OFF
    lcd_command(0x01); esp_rom_delay_us(2000);  // Clear Display (довга, ~1.52 мс)
    lcd_command(0x06);       // Entry Mode: курсор вправо, без зсуву екрана
    lcd_command(0x0C);       // Display ON, курсор і блимання вимкнені
}
