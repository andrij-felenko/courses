// TIM->CCR1 — регістр порівняння каналу 1. Через увімкнену
// буферизацію (OC1PE=1) запис лягає в preload, а в тінь
// перейде на найближчому оновленні лічильника (на межі періоду).

volatile uint16_t g_target;   // куди хочемо дійти (0..ARR)

void led_set_brightness(uint16_t duty) {
    // Пишемо коли завгодно: апаратура однаково візьме значення
    // тільки на межі, тож поточний імпульс не порветься.
    TIM3->CCR1 = duty;        // осіло в preload
    g_target = duty;
}

// Виклик у повільному циклі — плавна анімація без глітчів:
void led_fade_step(void) {
    static uint16_t cur;
    if      (cur < g_target) cur++;
    else if (cur > g_target) cur--;
    led_set_brightness(cur);  // безпечно: тінь підхопить на update
}
