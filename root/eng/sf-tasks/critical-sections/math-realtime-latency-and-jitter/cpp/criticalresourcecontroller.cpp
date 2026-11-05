#include <cstdint>
#include "stm32f4xx.h"
#include "FreeRTOS.h"
#include "semphr.h"

class CriticalResourceController {
private:
    SemaphoreHandle_t mutex_;
    volatile uint32_t internal_buffer_{0};

public:
    CriticalResourceController() {
        mutex_ = xSemaphoreCreateMutex();
    }

    ~CriticalResourceController() {
        if (mutex_ != nullptr) {
            vSemaphoreDelete(mutex_);
        }
    }

    uint32_t update_resource(uint32_t value) {
        if (mutex_ == nullptr) return 0;

        if (xSemaphoreTake(mutex_, portMAX_DELAY) == pdTRUE) {
            uint32_t start_cycles = DWT->CYCCNT;

            taskENTER_CRITICAL();
            internal_buffer_ += value;
            TIM2->CNT = internal_buffer_;
            __DSB();
            taskEXIT_CRITICAL();

            uint32_t elapsed = DWT->CYCCNT - start_cycles;
            xSemaphoreGive(mutex_);
            return elapsed;
        }
        return 0;
    }
};
