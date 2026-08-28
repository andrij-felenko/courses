#include <concepts>
#include <cstdint>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

namespace hal {

/* Фіктивна структура регістрів АЦП */
struct AdcRegisters {
    volatile uint32_t sr;
    volatile uint32_t cr;
    volatile uint32_t dr;
};

inline constexpr uint32_t ADC_SR_EOC = 1U << 1;
extern AdcRegisters* ADC1_REGS;

class AdcInterruptHandler {
public:
    explicit AdcInterruptHandler(SemaphoreHandle_t sem) noexcept : ready_semaphore_(sem) {}

    /* Top-Half обробка в ISR */
    void handle_irq() noexcept {
        BaseType_t higher_priority_task_woken = pdFALSE;

        if (ADC1_REGS->sr & ADC_SR_EOC) {
            ADC1_REGS->sr &= ~ADC_SR_EOC;

            if (ready_semaphore_ != nullptr) {
                xSemaphoreGiveFromISR(ready_semaphore_, &higher_priority_task_woken);
            }
        }

        portYIELD_FROM_ISR(higher_priority_task_woken);
    }

private:
    SemaphoreHandle_t ready_semaphore_;
};

} // namespace hal

static hal::AdcInterruptHandler g_adc_handler(nullptr);

extern "C" void ADC1_2_IRQHandler() {
    g_adc_handler.handle_irq();
}

extern "C" void adc_processing_task(void* pvParameters) {
    auto sem = static_cast<SemaphoreHandle_t>(pvParameters);
    for (;;) {
        if (xSemaphoreTake(sem, portMAX_DELAY) == pdTRUE) {
            const uint32_t raw_value = hal::ADC1_REGS->dr;
            // process_adc_sample(raw_value);
        }
    }
}
