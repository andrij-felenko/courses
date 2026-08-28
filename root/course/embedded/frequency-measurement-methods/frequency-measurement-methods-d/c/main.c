// Таймер тактується від APB = 1 МГц (1 тик = 1 мкс).
// На кожен фронт сигналу апаратура записує CCR у регістр захоплення
// й викликає це переривання.
#define TIMER_HZ   1000000u          // частота лічби таймера, Гц

volatile uint32_t g_period_ticks = 0;   // останній період у тиках
volatile uint8_t  g_have_period  = 0;

void TIM_CC_IRQHandler(void)
{
    static uint16_t prev = 0;
    static uint8_t  primed = 0;

    uint16_t now = TIM_GetCapture();     // апаратний знімок лічильника

    if (primed) {
        // 16-бітний таймер: віднімання в uint16_t саме обробляє
        // одне перевертання лічильника (now < prev) без if-ів.
        g_period_ticks = (uint16_t)(now - prev);
        g_have_period  = 1;
    }
    prev   = now;
    primed = 1;
}

// Перетворення в герци — у звичайному коді, не в перериванні.
float read_frequency_hz(void)
{
    if (!g_have_period || g_period_ticks == 0)
        return 0.0f;                     // ще немає даних або поділ на нуль
    return (float)TIMER_HZ / (float)g_period_ticks;
}
