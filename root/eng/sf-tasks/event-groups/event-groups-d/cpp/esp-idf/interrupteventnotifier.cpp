#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "driver/gpio.h"

class InterruptEventNotifier {
public:
    InterruptEventNotifier() {
        group_handle_ = xEventGroupCreate();
    }

    EventGroupHandle_t get_handle() const { return group_handle_; }

    // Метод для виклику виключно з ISR
    BaseType_t notify_from_isr(EventBits_t bits, BaseType_t *hp_task_woken) {
        return xEventGroupSetBitsFromISR(group_handle_, bits, hp_task_woken);
    }

private:
    EventGroupHandle_t group_handle_;
};

static InterruptEventNotifier s_notifier;

static void IRAM_ATTR gpio_cpp_isr_handler(void *arg) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    s_notifier.notify_from_isr(1 << 0, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
