// Дозвіл виходу для двох драйверів на спільному дроті DATA.
// OE == 1 → ніжка активно жене рівень; OE == 0 → ніжка в Hi-Z (вхід).

static void drv_release(uint8_t pin) {    // відпустити лінію: у Hi-Z
    gpio_set_direction(pin, GPIO_INPUT);  // напрям = вхід ⇒ обидва транзистори закриті
}
static void drv_take(uint8_t pin, uint8_t level) {  // взяти лінію: активний вихід
    gpio_write(pin, level);               // спершу задати рівень…
    gpio_set_direction(pin, GPIO_OUTPUT); // …тоді ввімкнути драйвер (дозвіл)
}

void hand_over(uint8_t from, uint8_t to, uint8_t level) {
    drv_release(from);   // 1) старий промовець ЙДЕ в Hi-Z — відпускає дріт
    drv_take(to, level); // 2) лише ТЕПЕР новий бере лінію й жене свій рівень
}
