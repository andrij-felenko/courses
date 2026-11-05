#include "FreeRTOS.h"
#include "event_groups.h"

// Визначення масок бітів подій (використовуємо молодші 24 біти)
#define BIT_POWER_STABLE    (1UL << 0)
#define BIT_SENSOR_READY    (1UL << 1)
#define BIT_NETWORK_UP      (1UL << 2)

// Маска комбінованої очікуваної події (Logical AND)
#define BIT_SYSTEM_READY_MASK (BIT_POWER_STABLE | BIT_SENSOR_READY | BIT_NETWORK_UP)

static EventGroupHandle_t xSystemEventGroup = NULL;

void vInitTask(void *pvParameters)
{
    (void)pvParameters;

    // Створення об'єкта групи подій
    xSystemEventGroup = xEventGroupCreate();
    if (xSystemEventGroup == NULL) {
        // Обробка помилки браку пам'яті в купі
        vTaskDelete(NULL);
    }

    // Імітація успішного запуску підсистем
    xEventGroupSetBits(xSystemEventGroup, BIT_POWER_STABLE);
    xEventGroupSetBits(xSystemEventGroup, BIT_SENSOR_READY);
    xEventGroupSetBits(xSystemEventGroup, BIT_NETWORK_UP);

    vTaskDelete(NULL);
}

void vApplicationWorkerTask(void *pvParameters)
{
    (void)pvParameters;
    EventBits_t uxReturnedBits;

    // Очікуємо одночасно на всі три біти з автоочищенням після виходу
    uxReturnedBits = xEventGroupWaitBits(
        xSystemEventGroup,
        BIT_SYSTEM_READY_MASK,
        pdTRUE,         // xClearOnExit = pdTRUE (скинути біти після розблокування)
        pdTRUE,         // xWaitForAllBits = pdTRUE (логіка AND)
        portMAX_DELAY   // Блокування без обмеження за часом
    );

    // Перевіряємо, чи справді було отримано повну маску
    if ((uxReturnedBits & BIT_SYSTEM_READY_MASK) == BIT_SYSTEM_READY_MASK) {
        // Усі компоненти підтвердили готовність — запуск основного циклу
    }

    vTaskDelete(NULL);
}
