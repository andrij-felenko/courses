#include "FreeRTOS.h"
#include "task.h"
#include "event_filter.h"

static TaskHandle_t xControlTaskHandle = NULL;
static event_filter_fast32_t limit_switch_filter;

void vTimerCallback_1kHz(void) {
    bool raw_level = (GPIO_PORT->IDR & PIN_MASK) != 0;
    bool prev_state = event_filter_fast32_get_state(&limit_switch_filter);
    bool new_state  = event_filter_fast32_update(&limit_switch_filter, raw_level);

    /* Надсилаємо подію задачі ЛИШЕ при реальній зміні відфільтрованого стану */
    if (new_state != prev_state && xControlTaskHandle != NULL) {
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xTaskNotifyFromISR(xControlTaskHandle, 
                           new_state ? EVENT_ACTIVE_BIT : EVENT_INACTIVE_BIT, 
                           eSetBits, 
                           &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

void vControlTask(void *pvParameters) {
    (void)pvParameters;
    uint32_t ulNotifiedValue;
    for (;;) {
        /* Задача спить і не споживає процесорний час, поки немає подій */
        if (xTaskNotifyWait(0x00, 0xFFFFFFFF, &ulNotifiedValue, portMAX_DELAY) == pdTRUE) {
            if (ulNotifiedValue & EVENT_ACTIVE_BIT) {
                // Дія на надійне спрацювання датчика
            }
        }
    }
}
