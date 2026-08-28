// Той самий ключ, той самий тип: для коду MOSFET нічим не відрізняється від NPN низом.
static sw_t mosfet = { .pin = GPIO_NUM_5, .active_low = false };

void app_main(void) {
    ESP_ERROR_CHECK(sw_begin(&mosfet));   // затвор у «0», канал закритий
    // Апаратно: затвор → (опц. 100…220 Ом) → вивід; підтяжка 100 кОм затвор→GND.
    // ⚠ 3.3 В на затворі 2N7000 замало — див. перевірку нижче.
    while (1) {
        sw_on(&mosfet);  vTaskDelay(pdMS_TO_TICKS(500));
        sw_off(&mosfet); vTaskDelay(pdMS_TO_TICKS(500));
    }
}
