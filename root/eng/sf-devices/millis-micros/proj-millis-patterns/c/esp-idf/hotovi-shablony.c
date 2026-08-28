#define PERIOD_US 500000LL           // 500 мс, виражені в мкс
int64_t last = 0;
bool on = false;

gpio_set_direction(LED_GPIO, GPIO_MODE_OUTPUT);
while (1) {
    int64_t now = esp_timer_get_time();
    if (now - last >= PERIOD_US) {   // настав час?
        last = now;                  // оновили мітку (саме now, не новий виклик)
        on = !on;
        gpio_set_level(LED_GPIO, on);
    }
    vTaskDelay(1);                   // віддали такт іншим задачам, не чекаючи періоду
}
