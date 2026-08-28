static volatile uint32_t g_count_result = 0;  // події за останнє завершене вікно
static volatile bool     g_count_ready  = false;
static volatile uint32_t g_count_seq    = 0;

// Викликається в кінці кожного вікна воріт (update таймера-воріт).
void TIM_GATE_IRQHandler(void)
{
    if (!(TIM_GATE->SR & TIM_SR_UIF)) return;
    TIM_GATE->SR &= ~TIM_SR_UIF;

    uint32_t n = TIM_CNT->CNT;     // скільки подій лічильник набрав за вікно
    TIM_CNT->CNT = 0;              // обнулити для наступного вікна

    g_count_result = n;
    g_count_ready  = true;
    g_count_seq++;
}

float count_read_hz(uint32_t window_ticks)
{
    if (!g_count_ready) return 0.0f;                 // перше вікно ще не закрилось
    uint32_t n = g_count_result;                     // 32-біт читання атомарне на 32-біт ядрі
    // f = N / T, де T = window_ticks / TIMER_HZ (вікно в тих самих тиках кварцу)
    return (float)n * (float)TIMER_HZ / (float)window_ticks;
}
