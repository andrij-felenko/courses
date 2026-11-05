#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "driver/gpio.h"

#define BUTTON_GPIO_PIN GPIO_NUM_4
#define EVENT_BIT_BUTTON_PRESSED (1 << 0)

static EventGroupHandle_t s_system_event_group;

// Обробник переривання GPIO
static void IRAM_ATTR gpio_isr_handler(void *arg)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    // Безпечне асинхронне встановлення біта з ISR
    BaseType_t xResult = xEventGroupSetBitsFromISR(
        s_system_event_group,
        EVENT_BIT_BUTTON_PRESSED,
        &xHigherPriorityTaskWoken
    );

    if (xResult != pdFAIL) {
        // Запит на перемикання контексту, якщо демон таймерів має вищий пріоритет
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

void vInitInterruptExample(void)
{
    s_system_event_group = xEventGroupCreate();

    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_NEGEDGE,
        .mode = GPIO_MODE_INPUT,
        .pin_bit_mask = (1ULL << BUTTON_GPIO_PIN),
        .pull_up_en = GPIO_PULLUP_ENABLE
    };
    gpio_config(&io_conf);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(BUTTON_GPIO_PIN, gpio_isr_handler, NULL);
}
