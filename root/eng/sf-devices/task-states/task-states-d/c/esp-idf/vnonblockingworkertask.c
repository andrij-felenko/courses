#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"
#include "esp_task_wdt.h"
#include "esp_log.h"

typedef struct {
    uint32_t commandId;
    uint32_t dataValue;
} DataCommand_t;

static QueueHandle_t xCmdQueue;
static SemaphoreHandle_t xBusMutex;

void vNonBlockingWorkerTask(void *pvParameters) {
    DataCommand_t cmd;
    // Обов'язкова підписка задачі на системний сторожовий таймер
    esp_task_wdt_add(NULL);

    while (1) {
        // Крок 1: Перехід у стан Blocked в очікуванні команди (таймаут 1 сек).
        // Процесор повністю звільняється для інших задач.
        if (xQueueReceive(xCmdQueue, &cmd, pdMS_TO_TICKS(1000)) == pdTRUE) {
            // Крок 2: Захоплення м'ютексу шини з успадкуванням пріоритету
            if (xSemaphoreTake(xBusMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
                // Безпечна обробка даних на спільній шині
                ESP_LOGI("WORKER", "Обробка команди %lu зі значенням %lu", 
                         cmd.commandId, cmd.dataValue);
                xSemaphoreGive(xBusMutex);
            } else {
                ESP_LOGE("WORKER", "Не вдалося захопити м'ютекс шини (таймаут)");
            }
        }

        // Крок 3: Регулярне підтвердження нормальної роботи (скидання WDT)
        esp_task_wdt_reset();
    }
}
