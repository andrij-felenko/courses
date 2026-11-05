#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_log.h"

#define TASK_A_BIT (1 << 0)
#define TASK_B_BIT (1 << 1)
#define TASK_C_BIT (1 << 2)
#define ALL_SYNC_BITS (TASK_A_BIT | TASK_B_BIT | TASK_C_BIT)

static EventGroupHandle_t s_rendezvous_group;
static const char *TAG = "RENDEZVOUS";

void vWorkerTaskA(void *pvParameters)
{
    while (1) {
        ESP_LOGI(TAG, "Задача A: Виконання Фази 1 (збір даних)");
        vTaskDelay(pdMS_TO_TICKS(100));

        // Досягнення бар'єра рандеву
        EventBits_t uxReturn = xEventGroupSync(
            s_rendezvous_group,
            TASK_A_BIT,
            ALL_SYNC_BITS,
            portMAX_DELAY
        );

        if ((uxReturn & ALL_SYNC_BITS) == ALL_SYNC_BITS) {
            ESP_LOGI(TAG, "Задача A: Бар'єр подолано! Перехід до Фази 2");
        }
    }
}

void vWorkerTaskB(void *pvParameters)
{
    while (1) {
        ESP_LOGI(TAG, "Задача B: Виконання Фази 1 (калібрування)");
        vTaskDelay(pdMS_TO_TICKS(200));

        EventBits_t uxReturn = xEventGroupSync(
            s_rendezvous_group,
            TASK_B_BIT,
            ALL_SYNC_BITS,
            portMAX_DELAY
        );

        if ((uxReturn & ALL_SYNC_BITS) == ALL_SYNC_BITS) {
            ESP_LOGI(TAG, "Задача B: Бар'єр подолано! Перехід до Фази 2");
        }
    }
}

void vWorkerTaskC(void *pvParameters)
{
    while (1) {
        ESP_LOGI(TAG, "Задача C: Виконання Фази 1 (розрахунок фільтра)");
        vTaskDelay(pdMS_TO_TICKS(150));

        EventBits_t uxReturn = xEventGroupSync(
            s_rendezvous_group,
            TASK_C_BIT,
            ALL_SYNC_BITS,
            portMAX_DELAY
        );

        if ((uxReturn & ALL_SYNC_BITS) == ALL_SYNC_BITS) {
            ESP_LOGI(TAG, "Задача C: Бар'єр подолано! Перехід до Фази 2");
        }
    }
}
