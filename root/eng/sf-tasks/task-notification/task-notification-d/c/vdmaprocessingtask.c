#include "FreeRTOS.h"
#include "task.h"

static TaskHandle_t xDmaTaskHandle = NULL;

// Обробник переривання завершення передачі DMA
void DMA1_Channel1_IRQHandler(void)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    // Перевіряємо апаратний прапорець завершення транзакції
    if (DMA1->ISR & DMA_ISR_TCIF1)
    {
        // Скидаємо апаратний прапорець переривання
        DMA1->IFCR = DMA_IFCR_CTCIF1;

        if (xDmaTaskHandle != NULL)
        {
            // Надсилаємо сповіщення задачі-обробнику з переривання
            vTaskNotifyGiveFromISR(xDmaTaskHandle, &xHigherPriorityTaskWoken);
        }
    }

    // Якщо розблокована задача має вищий пріоритет — виконуємо примусову зміну контексту
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// Задача обробки буфера DMA у фоновому режимі
void vDmaProcessingTask(void *pvParameters)
{
    xDmaTaskHandle = xTaskGetCurrentTaskHandle();

    for (;;)
    {
        // Запускаємо апаратну передачу DMA (ініціалізація периферичних регістрів)
        // ...

        // Чекаємо на сповіщення від ISR без обмеження за часом.
        // Передаємо pdTRUE для скидання лічильника в нуль (поведінка бінарного семафора).
        uint32_t ulEvents = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        if (ulEvents > 0)
        {
            // Обробка заповненого буфера даних у фоновому контексті
        }
    }
}
