// Викликається, коли затримка t_fire спливла. Смикає затвор коротким імпульсом.
static bool IRAM_ATTR on_fire(void *arg)
{
    gptimer_stop(g_timer);            // одноразовий будильник, більше не потрібен

    // Короткий імпульс: підняти затвор, зачекати GATE_PULSE_US, опустити.
    // Затримка тут — десятки мкс, це припустимо навіть в ISR (див. нижче чому).
    gpio_set_level(GATE_PIN, 1);
    esp_rom_delay_us(GATE_PULSE_US);  // калібрована коротка пауза, ~80 мкс
    gpio_set_level(GATE_PIN, 0);

    return false;
}
