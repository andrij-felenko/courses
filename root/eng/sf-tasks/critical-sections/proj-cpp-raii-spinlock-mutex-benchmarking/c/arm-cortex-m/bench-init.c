#include <stdint.h>
#include "stm32f4xx.h"

typedef struct {
    volatile uint32_t lock_flag;
    uint32_t min_cycles;
    uint32_t max_cycles;
    uint64_t total_cycles;
    uint32_t sample_count;
} critical_section_bench_t;

void bench_init(critical_section_bench_t *b) {
    b->lock_flag = 0;
    b->min_cycles = 0xFFFFFFFFU;
    b->max_cycles = 0;
    b->total_cycles = 0;
    b->sample_count = 0;
    
    // Вмикаємо модуль трасування DWT та лічильник CYCCNT
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void bench_measure_spinlock(critical_section_bench_t *b, void (*work_func)(void)) {
    uint32_t start_cycles = DWT->CYCCNT;
    
    // Атомарне захоплення спін-замка через інструкції LDREX/STREX
    while (__LDREXW(&b->lock_flag) != 0 || __STREXW(1, &b->lock_flag) != 0) {
        __NOP(); // Пауза для зменшення навантаження на шину
    }
    __DMB(); // Вхідний бар'єр пам'яті
    
    work_func(); // Виконання корисного навантаження
    
    __DMB(); // Вихідний бар'єр пам'яті
    b->lock_flag = 0;
    
    uint32_t elapsed = DWT->CYCCNT - start_cycles;
    if (elapsed < b->min_cycles) b->min_cycles = elapsed;
    if (elapsed > b->max_cycles) b->max_cycles = elapsed;
    b->total_cycles += elapsed;
    b->sample_count++;
}
