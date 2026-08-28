#include "esp_sleep.h"
#include "esp_log.h"
#include "driver/gpio.h"
#include "driver/rtc_io.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "keypad";

// keypad_init() / keypad_scan() і масиви ніжок — з вкладки ESP-IDF кроку 1:
// рядки на RTC-здатних 32, 33, 25, 26; стовпці — 27, 14, 4, 13 (без стрепінгових).
extern const gpio_num_t row_pins[4], col_pins[4];
void keypad_init(void);
char keypad_scan(void);

// маска рядкових ніг для ext1 (біт номера GPIO):
#define ROW_MASK ((1ULL << 32) | (1ULL << 33) | (1ULL << 25) | (1ULL << 26))

RTC_DATA_ATTR static uint32_t wake_count = 0;   // переживає сон у RTC-пам'яті

void app_main(void) {
    wake_count++;

    // Після глибокого сну стовпці лишаються ЗАФІКСОВАНІ (hold) з минулого разу,
    // а рядки — під RTC. Спершу все відпустити, інакше сканувати нічим:
    gpio_deep_sleep_hold_dis();
    for (int c = 0; c < 4; c++) gpio_hold_dis(col_pins[c]);
    for (int r = 0; r < 4; r++) rtc_gpio_deinit(row_pins[r]);

    if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT1) {
        ESP_LOGI(TAG, "прокинувся від натиску #%u", (unsigned)wake_count);
        keypad_init();
        char k = 0;
        for (int t = 0; t < 40 && !k; t++) {    // клавіша ще може деренчати
            k = keypad_scan();
            vTaskDelay(pdMS_TO_TICKS(2));
        }
        if (k) ESP_LOGI(TAG, "клавіша: %c", k);
        // тут: обробити подію
    } else {
        ESP_LOGI(TAG, "холодний старт");
    }

    // --- ДЗЕРКАЛЬНИЙ арм-стан (під те, що вміє класичний ESP32) ---
    for (int c = 0; c < 4; c++) {
        gpio_set_direction(col_pins[c], GPIO_MODE_OUTPUT);
        gpio_set_level(col_pins[c], 1);               // усі стовпці у «1»
        gpio_hold_en(col_pins[c]);                    // ЗАФІКСУВАТИ: у сні драйвер гасне
    }
    for (int r = 0; r < 4; r++) {
        rtc_gpio_init(row_pins[r]);
        rtc_gpio_set_direction(row_pins[r], RTC_GPIO_MODE_INPUT_ONLY);
        rtc_gpio_pulldown_en(row_pins[r]);            // підтяжка ВНИЗ мусить жити й у сні
        rtc_gpio_pullup_dis(row_pins[r]);
    }
    gpio_deep_sleep_hold_en();                        // тримати фіксацію й у глибокому сні

    // будити, коли БУДЬ-ЯКА стежена нога стане ВИСОКОЮ (натиск підіймає рядок у «1»):
    esp_sleep_enable_ext1_wakeup(ROW_MASK, ESP_EXT1_WAKEUP_ANY_HIGH);

    ESP_LOGI(TAG, "засинаю; розбудить натиск");
    esp_deep_sleep_start();     // усе нижче не виконається — після сну app_main почнеться заново
}
