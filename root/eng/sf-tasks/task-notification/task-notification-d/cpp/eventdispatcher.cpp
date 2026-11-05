#include "FreeRTOS.h"
#include "task.h"
#include <cstdint>

class EventDispatcher
{
public:
    enum EventMask : uint32_t
    {
        UartRxReady  = (1UL << 0),
        SpiTxComplete = (1UL << 1),
        TimerTimeout   = (1UL << 2)
    };

    static void setWorkerHandle(TaskHandle_t handle)
    {
        m_workerHandle = handle;
    }

    static void sendEvent(EventMask mask)
    {
        if (m_workerHandle != nullptr)
        {
            // Атомарне побітове встановлення прапорців події у TCB задачі
            xTaskNotify(m_workerHandle, static_cast<uint32_t>(mask), eSetBits);
        }
    }

    static void workerLoop()
    {
        uint32_t notifiedValue = 0;
        for (;;)
        {
            if (xTaskNotifyWait(0x00, 0xFFFFFFFF, &notifiedValue, portMAX_DELAY) == pdTRUE)
            {
                if (notifiedValue & UartRxReady)
                {
                    // Обробка прийому UART
                }
                if (notifiedValue & SpiTxComplete)
                {
                    // Обробка обміну SPI
                }
                if (notifiedValue & TimerTimeout)
                {
                    // Обробка події таймера
                }
            }
        }
    }

private:
    inline static TaskHandle_t m_workerHandle = nullptr;
};
