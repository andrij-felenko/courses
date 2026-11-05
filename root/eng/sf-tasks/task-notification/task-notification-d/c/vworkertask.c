#include "FreeRTOS.h"
#include "task.h"

// Бітові маски подій периферії
#define EVENT_UART_RX_READY  (1UL << 0)
#define EVENT_SPI_TX_COMPLETE (1UL << 1)
#define EVENT_TIMER_TIMEOUT   (1UL << 2)

static TaskHandle_t xWorkerTaskHandle = NULL;

// Задача-обробник системних подій
void vWorkerTask(void *pvParameters)
{
    uint32_t ulNotifiedValue;
    
    for (;;)
    {
        // Чекаємо на будь-яке сповіщення. Очищаємо всі біти при виході.
        if (xTaskNotifyWait(0x00, 0xFFFFFFFF, &ulNotifiedValue, portMAX_DELAY) == pdTRUE)
        {
            if (ulNotifiedValue & EVENT_UART_RX_READY)
            {
                // Обробка надходження даних по UART
            }
            if (ulNotifiedValue & EVENT_SPI_TX_COMPLETE)
            {
                // Обробка завершення транзакції SPI
            }
            if (ulNotifiedValue & EVENT_TIMER_TIMEOUT)
            {
                // Обробка події системного таймера
            }
        }
    }
}

// Функція надсилання події з іншої фонової задачі
void vSendEventFromTask(uint32_t ulEventMask)
{
    if (xWorkerTaskHandle != NULL)
    {
        // Встановлюємо відповідні біти подій у TCB робочої задачі
        xTaskNotify(xWorkerTaskHandle, ulEventMask, eSetBits);
    }
}
