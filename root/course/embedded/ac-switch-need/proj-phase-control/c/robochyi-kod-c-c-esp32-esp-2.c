// Викликається на КОЖНОМУ переході нуля (сто разів на секунду для 50 Гц).
// Єдина робота: перезапустити таймер на поточну затримку t_fire.
static bool IRAM_ATTR on_zero_cross(void *arg)
{
    if (!g_output_enabled) {
        return false;                 // регулятор вимкнено — нічого не робимо
    }

    // Скинути лічильник у нуль і завести будильник на g_fire_delay_us.
    gptimer_set_raw_count(g_timer, 0);
    gptimer_alarm_config_t alarm = {
        .alarm_count = g_fire_delay_us,   // спрацює через t_fire мкс
        .flags.auto_reload_on_alarm = false,
    };
    gptimer_set_alarm_action(g_timer, &alarm);
    gptimer_start(g_timer);
    return false;                     // пробудження задачі не потрібне
}
