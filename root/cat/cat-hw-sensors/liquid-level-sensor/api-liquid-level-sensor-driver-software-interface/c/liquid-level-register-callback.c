// Реєстрація callback та обробка аварійних подій (C)
typedef void (*liquid_level_event_cb_t)(liquid_level_status_t status, float level_percent);

static liquid_level_event_cb_t g_event_callback = NULL;

void liquid_level_register_callback(liquid_level_event_cb_t cb) {
    g_event_callback = cb;
}

void liquid_level_process_tick(void) {
    float raw_adc = read_adc_hw();
    
    // Апаратна діагностика
    if (raw_adc < 50) {
        if (g_event_callback) g_event_callback(LIQUID_LEVEL_ERR_LINE_BREAK, 0.0f);
        return;
    }
    if (raw_adc > 4045) {
        if (g_event_callback) g_event_callback(LIQUID_LEVEL_ERR_SHORT_CIRCUIT, 0.0f);
        return;
    }
    
    float percent = liquid_level_get_percent();
    if (percent < 5.0f && g_event_callback) {
        g_event_callback(LIQUID_LEVEL_OK, percent); // Подія сухого ходу
    }
}
