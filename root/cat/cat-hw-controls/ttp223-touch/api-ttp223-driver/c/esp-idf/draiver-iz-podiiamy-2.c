static touch_button_t btn;

void app_main(void) {
    tb_begin(&btn, GPIO_NUM_4, 1);      // SIG на GPIO4, активний у 1
    gpio_set_direction(PIN_LED, GPIO_MODE_OUTPUT);

    while (1) {
        tb_update(&btn);                // рушій драйвера, кожен прохід

        if (tb_pressed(&btn))  ESP_LOGI(TAG, "торкнулися");
        if (tb_released(&btn))          // скільки трималися — для довгого натиску
            ESP_LOGI(TAG, "відпустили, тримали (мс): %lld", tb_held_ms(&btn));
        gpio_set_level(PIN_LED, tb_held(&btn));   // світло, поки палець на пластинці

        vTaskDelay(pdMS_TO_TICKS(1));   // решта часу ядра — іншим задачам
    }
}
