// counter_sig — лічить фронти сигналу (external clock), 32-біт.
// timer_ref   — лічить тики кварцу f_ref, на КОЖЕН фронт сигналу робить
//               input capture (захоплення референсного часу цього фронту).

static volatile uint32_t g_recip_n   = 0;   // періодів сигналу у вікні
static volatile uint64_t g_recip_m   = 0;   // тиків опорного годинника у вікні
static volatile bool     g_recip_rdy = false;
static volatile uint32_t g_recip_seq = 0;

// Стан вікна, що «прилипає» до фронтів. Оновлюється лише в ISR захоплення.
static uint32_t win_n_start;     // лічильник періодів на початку вікна
static uint64_t win_t_start;     // опорний час (48-біт) на початку вікна
static uint32_t win_t0_lo;       // молодші біти, щоб знати «коли минув час»
static bool     win_open = false;

#define RECIP_WINDOW_TICKS  (TIMER_HZ / 10u)   // бажане вікно ≈ 100 мс

// Переривання захоплення таймера-референса: спрацьовує на КОЖЕН фронт сигналу.
void TIM_REF_CC_IRQHandler(void)
{
    if (!(TIM_REF->SR & TIM_SR_CC1IF)) return;

    uint16_t cap = (uint16_t)TIM_REF->CCR1;          // знімок опорного часу фронту
    uint32_t ovf = g_ref_ovf;                        // переповнення опорного таймера
    if ((TIM_REF->SR & TIM_SR_UIF) && cap < (TIMER_ARR / 2)) ovf++;  // та сама гонка
    uint64_t t_now = ((uint64_t)ovf << 16) | cap;    // повний опорний час фронту

    uint32_t n_now = TIM_SIG->CNT;                   // скільки фронтів уже набрано

    if (!win_open) {                                 // відкриваємо нове вікно на цьому фронті
        win_n_start = n_now;
        win_t_start = t_now;
        win_open    = true;
        return;
    }

    // Вікно відкрите: чи минув уже бажаний час від його початку?
    if ((t_now - win_t_start) >= RECIP_WINDOW_TICKS) {
        // Так — закриваємо ворота РІВНО на цьому фронті (ціле число періодів!).
        g_recip_n   = n_now - win_n_start;           // N_сиг: цілі періоди сигналу
        g_recip_m   = t_now - win_t_start;           // M_ref: тики опорного годинника
        g_recip_rdy = true;
        g_recip_seq++;
        win_open    = false;                         // наступний фронт відкриє нове вікно
    }
}

// Перетворення в герци — поза ISR.
float reciprocal_read_hz(void)
{
    uint32_t n; uint64_t m;
    atomic_load_recip(&n, &m);            // узгоджене читання пари (нижче)
    if (!g_recip_rdy || n == 0 || m == 0)
        return 0.0f;                      // вікно ще не закрилось / поділ на нуль
    // f = N_сиг · f_ref / M_ref
    return (float)n * (float)TIMER_HZ / (float)m;
}
