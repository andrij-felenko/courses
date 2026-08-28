static sw_t lamp = { .pin = GPIO_NUM_9, .active_low = false };   // канал LEDC уже налаштований

void lamp_breathe(void) {   // vTaskDelay крокує тіками планувальника (типово 10 мс)
    for (int d = 0; d <= 255; d++) {                             // розгоряння
        sw_analog(&lamp, LEDC_CHANNEL_0, d); vTaskDelay(pdMS_TO_TICKS(10));
    }
    for (int d = 255; d >= 0; d--) {                             // згасання
        sw_analog(&lamp, LEDC_CHANNEL_0, d); vTaskDelay(pdMS_TO_TICKS(10));
    }
}
