#include <stdint.h>

#define BLK  16                    // відліків у блоці DMA (8 кГц / 16 ≈ 2 мс на блок)

// два буфери опорного й помилки: поки DMA пише один, ми рахуємо інший
static q15_t buf_ref[2][BLK];
static q15_t buf_err[2][BLK];
static volatile int  ready_idx = -1;    // який блок готовий до обробки (-1 = жодного)
static volatile uint32_t overruns = 0;  // лічильник пропущених блоків (для діагностики)

// --- ISR: викликається DMA, коли черговий блок наповнено. КОРОТКА. ---
void DMA_ADC_IRQHandler(void)
{
    int just_filled = dma_completed_buffer();   // 0 або 1 — який щойно повний

    if (ready_idx >= 0)            // попередній блок ще не обробили?!
        overruns++;                // ми не вклалися в бюджет — фіксуємо й їдемо далі

    ready_idx = just_filled;       // позначити готовий, головний цикл його забере
    dma_clear_flag();
    // більше в ISR нічого: жодних згорток. Лише «блок готовий».
}
