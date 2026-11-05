#include "ff.h"
#include "esp_timer.h"
#include "esp_log.h"

static const char *TAG = "SD_LOG";

// Структура телеметрії для запису
typedef struct {
    uint32_t timestamp_ms;
    float accel_x;
    float accel_y;
    float accel_z;
} telemetry_pkt_t;

void naive_logging_task(void *pvParameters) {
    FIL log_file;
    FRESULT res;
    UINT bytes_written;
    telemetry_pkt_t pkt;
    
    res = f_open(&log_file, "1:/telemetry.bin", FA_WRITE | FA_OPEN_APPEND);
    if (res != FR_OK) {
        ESP_LOGE(TAG, "Помилка відкриття файлу: %d", res);
        vTaskDelete(NULL);
    }

    while (1) {
        // Заповнення пакету фіктивними даними датчиків
        pkt.timestamp_ms = (uint32_t)(esp_timer_get_time() / 1000);
        pkt.accel_x = 1.0f;
        pkt.accel_y = 0.0f;
        pkt.accel_z = 9.81f;

        uint64_t t_start = esp_timer_get_time();
        
        // Запис пакету в кінець файлу (динамічне розширення)
        res = f_write(&log_file, &pkt, sizeof(pkt), &bytes_written);
        
        uint64_t t_end = esp_timer_get_time();
        uint32_t duration_us = (uint32_t)(t_end - t_start);

        if (duration_us > 50000) { // Фіксація затримок понад 50 мс
            ESP_LOGW(TAG, "Сплеск tail latency: %uint32_t мкс!", duration_us);
        }

        vTaskDelay(pdMS_TO_TICKS(10)); // Інтервал виклику 10 мс
    }
}
