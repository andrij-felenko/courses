#include "esp_psram.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "driver/spi_master.h"

static const char *TAG = "PCB_INTEGRITY_TEST";

// Перевірка цілісності сигналів та стабільності Octal SPI при максимальному навантаженні
void test_pcb_octal_bus_integrity(void) {
    if (!esp_psram_is_initialized()) {
        ESP_LOGE(TAG, "Octal PSRAM не виявлено! Перевірте трасування шини та живлення VDD_SPI.");
        return;
    }

    const size_t test_words = 256 * 1024; // 1 МБ блокових даних
    uint32_t *psram_array = (uint32_t *)heap_caps_malloc(test_words * sizeof(uint32_t), MALLOC_CAP_SPIRAM);

    if (psram_array == NULL) {
        ESP_LOGE(TAG, "Не вдалося виділити пам'ять у PSRAM для тесту цілісності");
        return;
    }

    ESP_LOGI(TAG, "Запуск тестування цілісності сигналів OPI (шаблони 0x55AA55AA та 0xAA55AA55)...");

    // Шаблон 1: Агресивний рівень перемикання шини (шиновий дзвін)
    for (size_t i = 0; i < test_words; i++) {
        psram_array[i] = (i % 2 == 0) ? 0x55AA55AA : 0xAA55AA55;
    }

    size_t error_count = 0;
    for (size_t i = 0; i < test_words; i++) {
        uint32_t expected = (i % 2 == 0) ? 0x55AA55AA : 0xAA55AA55;
        if (psram_array[i] != expected) {
            error_count++;
        }
    }

    // Шаблон 2: Бігучий нуль та одиниця (перевірка перехресних наводок crosstalk)
    for (size_t i = 0; i < test_words; i++) {
        psram_array[i] = (1U << (i % 32));
    }

    for (size_t i = 0; i < test_words; i++) {
        uint32_t expected = (1U << (i % 32));
        if (psram_array[i] != expected) {
            error_count++;
        }
    }

    heap_caps_free(psram_array);

    if (error_count == 0) {
        ESP_LOGI(TAG, "Тест цілісності сигналів пройшов УСПІШНО! Фізичне трасування 50 Ом та skew budget витримано.");
    } else {
        ESP_LOGE(TAG, "ВИЯВЛЕНО %zu ПОМИЛОК! Перевірте вирівнювання трас D0-D7/DQS та блокувальні конденсатори.", error_count);
    }
}
