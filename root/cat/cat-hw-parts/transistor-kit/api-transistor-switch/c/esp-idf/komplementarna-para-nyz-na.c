// Дві половини одного вузла: NPN тримає низ, PNP — верх.
static sw_t low_side  = { .pin = GPIO_NUM_5, .active_low = false };  // NPN низом:  «1» → увімк
static sw_t high_side = { .pin = GPIO_NUM_6, .active_low = true  };  // PNP верхом: «0» → увімк

void app_main(void) {
    ESP_ERROR_CHECK(sw_begin(&low_side));
    ESP_ERROR_CHECK(sw_begin(&high_side));   // обидва вимкнені (кожен у свій «вимкнено»)

    while (1) {
        // Попри протилежну апаратну полярність, семантика ОДНАКОВА:
        sw_on(&low_side);                    // gpio_set_level(GPIO_NUM_5, 1)
        sw_on(&high_side);                   // gpio_set_level(GPIO_NUM_6, 0) — теж «увімкнути»
        vTaskDelay(pdMS_TO_TICKS(1000));
        sw_off(&low_side);
        sw_off(&high_side);
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
