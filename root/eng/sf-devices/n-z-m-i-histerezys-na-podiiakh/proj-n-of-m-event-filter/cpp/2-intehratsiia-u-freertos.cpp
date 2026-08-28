#include "FreeRTOS.h"
#include "task.h"
#include "event_filter_modern.hpp"

using namespace embedded::filter;

static TaskHandle_t controlTaskHandle = nullptr;
static ModernEventFilter<8, 6, 2> limitSwitchFilter{false};

void TimerCallback1kHz() noexcept {
    const bool raw_level = (GPIO_PORT->IDR & PIN_MASK) != 0;
    const bool prev_state = limitSwitchFilter.GetState();
    const bool new_state  = limitSwitchFilter.Update(raw_level);

    if (new_state != prev_state && controlTaskHandle != nullptr) {
        BaseType_t higherPriorityTaskWoken = pdFALSE;
        xTaskNotifyFromISR(controlTaskHandle,
                           new_state ? EVENT_ACTIVE_BIT : EVENT_INACTIVE_BIT,
                           eSetBits,
                           &higherPriorityTaskWoken);
        portYIELD_FROM_ISR(higherPriorityTaskWoken);
    }
}
