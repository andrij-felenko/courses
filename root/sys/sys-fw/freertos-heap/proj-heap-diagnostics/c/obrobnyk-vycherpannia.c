#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_system.h"

void vApplicationMallocFailedHook(void)
{
    TaskHandle_t failed_task = xTaskGetCurrentTaskHandle();
    const char *task_name = pcTaskGetName(failed_task);

    ESP_LOGE("CRITICAL", "КРИТИЧНА ПОМИЛКА: pvPortMalloc() повернув NULL у задачі '%s'!",
             task_name ? task_name : "UNKNOWN");
    ESP_LOGE("CRITICAL", "Вільна пам'ять на момент збою: %u Б",
             (unsigned int)xPortGetFreeHeapSize());

    /* У бойовій системі: фіксація в NVS/RTC та контрольоване перезавантаження */
    esp_restart();
}
