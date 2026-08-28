#include <stdint.h>
#include <math.h>

#define N        256u        // розмір таблиці — степінь двійки
#define LOG2N    8u          // log2(N): стільки старших біт фази йдуть в індекс
#define DAC_MAX  4095u       // 12-бітний ЦАП: рівні 0…4095

static uint16_t table[N];             // таблиця відліків, заповнюється раз
static volatile uint32_t phase = 0;   // фазовий акумулятор — 32-бітний БЕЗЗНАКОВИЙ
static volatile uint32_t step  = 0;   // слово керування частотою (ФКС)

extern void dac_write(uint16_t level);   // драйвер ЦАП конкретної плати

// Таблиця (раз при старті): один період синуса, зміщений у діапазон ЦАП 0…DAC_MAX
void dds_build_table(void)
{
    for (uint32_t k = 0; k < N; k++) {
        double s = sin(2.0 * M_PI * k / N);                       // −1…+1
        table[k] = (uint16_t)lround((DAC_MAX / 2.0) * (1.0 + s)); // → 0…DAC_MAX
    }
}

// Зміна частоти — це просто запис нового step (фаза не рветься):
void dds_set_freq(double f_out, double f_s)
{
    step = (uint32_t)llround(f_out * 4294967296.0 / f_s);   // 2³² = 4294967296
}

// Гаряча петля — виклик із переривання таймера рівно на такт fₛ:
void dds_sample_isr(void)
{
    uint32_t index = phase >> (32u - LOG2N);  // старші біти → індекс у таблиці
    dac_write(table[index]);                  // видати готовий відлік — одиниці тактів
    phase += step;                            // крок + обгортка: uint32 переповнюється сам
}
