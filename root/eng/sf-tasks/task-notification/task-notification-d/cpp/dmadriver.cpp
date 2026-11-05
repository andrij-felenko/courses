#include "FreeRTOS.h"
#include "task.h"
#include <cstdint>

class DmaDriver
{
public:
    static void initTask()
    {
        m_taskHandle = xTaskGetCurrentTaskHandle();
    }

    // Викликається з вектора апаратного переривання DMA
    static void handleInterruptFromISR()
    {
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;

        // Перевірка та скидання прапорця периферії
        if (DMA1->ISR & DMA_ISR_TCIF1)
        {
            DMA1->IFCR = DMA_IFCR_CTCIF1;

            if (m_taskHandle != nullptr)
            {
                // Розблоковуємо задачу через пряме сповіщення TCB
                vTaskNotifyGiveFromISR(m_taskHandle, &xHigherPriorityTaskWoken);
            }
        }

        // Запит на перемикання контексту наприкінці ISR
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }

    static void taskLoop()
    {
        initTask();
        for (;;)
        {
            // Очікування сповіщення від переривання
            if (ulTaskNotifyTake(pdTRUE, portMAX_DELAY) > 0)
            {
                // Безпечна обробка даних у контексті задачі
            }
        }
    }

private:
    inline static TaskHandle_t m_taskHandle = nullptr;
};

// Зовнішня ISR функція вектора
extern "C" void DMA1_Channel1_IRQHandler(void)
{
    DmaDriver::handleInterruptFromISR();
}
