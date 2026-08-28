    gpio_config_t io = {
        .pin_bit_mask = 1ULL << IRQ_GPIO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,   // IRQ активний високий → тягнемо вниз
        .intr_type    = GPIO_INTR_POSEDGE,      // фронт ↑
    };
    ESP_ERROR_CHECK(gpio_config(&io));
    ESP_ERROR_CHECK(gpio_install_isr_service(0));
    ESP_ERROR_CHECK(gpio_isr_handler_add(IRQ_GPIO, on_lightning_irq, NULL));

// Обробник переривання: КОРОТКО — лише прапорець.
// IRAM_ATTR — щоб виклик не чекав на flash-кеш.
static void IRAM_ATTR on_lightning_irq(void *arg) {
    irq_triggered = true;
}
