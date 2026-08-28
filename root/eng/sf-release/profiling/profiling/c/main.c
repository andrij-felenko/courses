#include "stm32f4xx.h"            // CoreDebug, DWT, SystemCoreClock
#include "FreeRTOS.h"
#include "task.h"

// ── Увімкнути лічильник тактів DWT (раз під час старту) ──────────────
static void cyccnt_enable(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk; // дозволити трасування
    DWT->CYCCNT = 0;                                // обнулити лічильник
    DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;           // увімкнути CYCCNT
}

static uint32_t max_cycles = 0;   // фіксуємо МАКСИМУМ (найгірший випадок)
static uint32_t iter = 0;

void sensor_task(void *arg) {
    cyccnt_enable();
    for (;;) {
        // ── 1. Вимір тривалості ділянки лічильником тактів ──────────
        uint32_t t0 = DWT->CYCCNT;

        read_sensor_and_process();   // підозрювана ділянка

        uint32_t t1 = DWT->CYCCNT;
        uint32_t dt = t1 - t0;       // різниця беззнакових → переповнення
                                     // нешкідливе для коротких ділянок
        if (dt > max_cycles) max_cycles = dt;

        // ── 2. Друкуємо РІДКО — раз на 1000 ітерацій, поза гарячим шляхом ─
        if (++iter % 1000 == 0) {
            uint32_t us = max_cycles / (SystemCoreClock / 1000000u); // такти → мкс
            UBaseType_t stack_left = uxTaskGetStackHighWaterMark(NULL);
            // мінімальний залишок стека (у словах): чим менше, тим небезпечніше
            size_t heap_left = xPortGetFreeHeapSize();
            size_t heap_min  = xPortGetMinimumEverFreeHeapSize();
            // heap_min — водяний знак купи: найменше за весь час;
            // якщо він повільно тане між замірами — є витік

            printf("[profile] max dt = %lu тактів (~%lu мкс) | "
                   "stack залишок = %lu слів | heap %lu / min %lu Б\n",
                   (unsigned long)max_cycles, (unsigned long)us,
                   (unsigned long)stack_left,
                   (unsigned long)heap_left, (unsigned long)heap_min);
            max_cycles = 0;          // скидаємо для наступного вікна
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
