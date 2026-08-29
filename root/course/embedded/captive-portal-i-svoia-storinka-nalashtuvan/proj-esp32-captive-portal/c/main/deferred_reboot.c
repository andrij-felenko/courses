#include "deferred_reboot.h"

#include "esp_log.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"

static const char *TAG = "reboot";

static TimerHandle_t s_timer = NULL;

static void reboot_timer_cb(TimerHandle_t timer)
{
    (void)timer;
    ESP_LOGI(TAG, "Плановий перезапуск системи");
    esp_restart();
}

esp_err_t deferred_reboot_schedule(uint32_t delay_ms)
{
    const TickType_t ticks = pdMS_TO_TICKS(delay_ms);
    if (ticks == 0) {
        return ESP_ERR_INVALID_ARG;
    }

    if (s_timer == NULL) {
        s_timer = xTimerCreate("reboot", ticks, pdFALSE, NULL, reboot_timer_cb);
        if (s_timer == NULL) {
            ESP_LOGE(TAG, "Не вистачило купи на таймер перезапуску");
            return ESP_ERR_NO_MEM;
        }
    } else if (xTimerChangePeriod(s_timer, ticks, 0) != pdPASS) {
        return ESP_FAIL;
    }

    /* Команда йде в чергу служби таймерів; чекати на неї в обробнику HTTP не можна. */
    if (xTimerStart(s_timer, 0) != pdPASS) {
        ESP_LOGE(TAG, "Черга служби таймерів переповнена");
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "Перезапуск заплановано через %u мс", (unsigned)delay_ms);
    return ESP_OK;
}
