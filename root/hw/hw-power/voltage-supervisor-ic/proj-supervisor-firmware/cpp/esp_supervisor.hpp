/* esp_supervisor.hpp — C++ обгортка */
#pragma once
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "driver/gpio.h"

class EspWindowWatchdog {
public:
    explicit EspWindowWatchdog(gpio_num_t wdiPin, gpio_num_t pfoPin)
        : wdiPin_(wdiPin), pfoPin_(pfoPin), eventGroup_(xEventGroupCreate()) {
        
        gpio_config_t out_conf = {
            .pin_bit_mask = (1ULL << wdiPin_),
            .mode = GPIO_MODE_OUTPUT,
            .pull_up_en = GPIO_PULLUP_DISABLE,
            .pull_down_en = GPIO_PULLDOWN_DISABLE,
            .intr_type = GPIO_INTR_DISABLE
        };
        gpio_config(&out_conf);
    }

    void reportTaskHealth(EventBits_t taskBit) noexcept {
        xEventGroupSetBits(eventGroup_, taskBit);
    }

    void runSupervisorLoop(EventBits_t expectedTasksMask, uint32_t periodMs) noexcept {
        TickType_t lastWake = xTaskGetTickCount();
        const TickType_t period = pdMS_TO_TICKS(periodMs);
        int state = 0;

        while (true) {
            vTaskDelayUntil(&lastWake, period);

            EventBits_t bits = xEventGroupWaitBits(
                eventGroup_, expectedTasksMask, pdTRUE, pdTRUE, 0
            );

            if ((bits & expectedTasksMask) == expectedTasksMask) {
                state = !state;
                gpio_set_level(wdiPin_, state);
            }
        }
    }

private:
    gpio_num_t wdiPin_;
    gpio_num_t pfoPin_;
    EventGroupHandle_t eventGroup_;
};
