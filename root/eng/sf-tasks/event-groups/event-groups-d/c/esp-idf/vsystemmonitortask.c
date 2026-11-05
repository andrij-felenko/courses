#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_log.h"

#define BIT_POWER_OK     (1 << 0)
#define BIT_STORAGE_OK   (1 << 1)
#define BIT_SENSORS_OK   (1 << 2)
#define BIT_NETWORK_OK   (1 << 3)

#define SYSTEM_READY_MASK (BIT_POWER_OK | BIT_STORAGE_OK | BIT_SENSORS_OK | BIT_NETWORK_OK)

static StaticEventGroup_t s_system_group_buffer;
static EventGroupHandle_t s_system_event_group;
static const char *TAG = "SYS_MONITOR";

void vSystemMonitorTask(void *pvParameters)
{
    ESP_LOGI(TAG, "Очікування готовності всіх підсистем...");

    // Атомарне очікування всіх 4 бітів готовності (Логічне AND)
    EventBits_t uxBits = xEventGroupWaitBits(
        s_system_event_group,
        SYSTEM_READY_MASK,
        pdFALSE,            // Не очищати атомарно для широкомовного доступу
        pdTRUE,             // Очікувати ВСІ біти (AND)
        portMAX_DELAY
    );

    if ((uxBits & SYSTEM_READY_MASK) == SYSTEM_READY_MASK) {
        ESP_LOGI(TAG, "Усі підсистеми готові! Запуск основного циклу");
    }
}

void vSubsystemInit(void)
{
    // Створення групи подій без використання динамічної купи
    s_system_event_group = xEventGroupCreateStatic(&s_system_group_buffer);

    // Імітація поступового запуску підсистем
    xEventGroupSetBits(s_system_event_group, BIT_POWER_OK);
    xEventGroupSetBits(s_system_event_group, BIT_STORAGE_OK);
    xEventGroupSetBits(s_system_event_group, BIT_SENSORS_OK);
    xEventGroupSetBits(s_system_event_group, BIT_NETWORK_OK);
}
