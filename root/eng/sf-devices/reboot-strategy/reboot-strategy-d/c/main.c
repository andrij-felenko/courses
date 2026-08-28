#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_log.h"
static const char *TAG = "fault_handler";

// RTC_NOINIT_ATTR: змінна у RTC slow memory. Переживає програмний reset,
// але НЕ переживає повного знеструмлення; через deep-sleep на ESP32 за
// замовчуванням теж не зберігається (треба окремо тримати RTC-домен живим).
RTC_NOINIT_ATTR static uint32_t s_boot_fail_cnt;
RTC_NOINIT_ATTR static uint32_t s_last_fault_code;

// Викликати на старті: відрізнити «свіже» увімкнення від рестарту по збою.
void fault_counter_init(void) {
    esp_reset_reason_t reason = esp_reset_reason();
    if (reason == ESP_RST_POWERON || reason == ESP_RST_BROWNOUT) {
        // Справжнє увімкнення живлення або просідання напруги:
        // RTC-пам'ять могла бути неініціалізованою — починаємо лічбу з нуля.
        s_boot_fail_cnt   = 0;
        s_last_fault_code = 0;
    }
    // Якщо причина — watchdog чи panic, лічильник НЕ чіпаємо:
    // він уже інкрементований перед попереднім reset і має зберегтися.
}

// Викликати при будь-якій критичній помилці.
void fault_handler(uint32_t fault_code) {
    // Крок 1: безпечний стан — ПЕРЕДУСІМ (між збоєм і reset мотор не крутиться).
    enter_safe_state();

    // Крок 2: зберегти причину й збільшити лічильник — ДО reset, поки RAM жива.
    s_last_fault_code = fault_code;
    s_boot_fail_cnt++;

    // Крок 3: лишити слід у журналі.
    ESP_LOGE(TAG, "FAULT 0x%08lx — reboot #%lu", fault_code, s_boot_fail_cnt);

    // Крок 4: дозаписати NVS — закрити незавершені транзакції, не лишити їх «рваними».
    nvs_flash_deinit();

    // Невелика пауза — дати UART витиснути лог до кінця.
    vTaskDelay(pdMS_TO_TICKS(200));

    // Крок 5: чисте перезавантаження.
    esp_restart();
}
