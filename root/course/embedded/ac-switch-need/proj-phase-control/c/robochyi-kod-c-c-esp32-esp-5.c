void phase_control_init(void)
{
    // 1. Вихід на затвор — у нуль (симістор закритий), поки не накажемо
    gpio_config_t gate_cfg = {
        .pin_bit_mask = 1ULL << GATE_PIN,
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&gate_cfg);
    gpio_set_level(GATE_PIN, 0);

    // 2. Вхід ZCD — з перериванням на наростний фронт
    gpio_config_t zcd_cfg = {
        .pin_bit_mask = 1ULL << ZCD_PIN,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .intr_type = GPIO_INTR_POSEDGE,      // фронт = перехід нуля
    };
    gpio_config(&zcd_cfg);

    // 3. Апаратний таймер: 1 тік = 1 мкс (роздільність 1 МГц)
    gptimer_config_t timer_cfg = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = 1000000,            // 1 МГц → 1 мкс на тік
    };
    gptimer_new_timer(&timer_cfg, &g_timer);

    gptimer_event_callbacks_t cbs = { .on_alarm = on_fire };
    gptimer_register_event_callbacks(g_timer, &cbs, NULL);
    gptimer_enable(g_timer);

    // 4. Причепити обробник GPIO до ніжки ZCD
    gpio_install_isr_service(0);
    gpio_isr_handler_add(ZCD_PIN, zcd_gpio_isr, NULL);

    // 5. Безпечний старт: вимкнено, затримка максимальна
    g_fire_delay_us = DELAY_MAX_US;
    g_output_enabled = false;
}
