/* Ініціалізація та прямий замір тактів за допомогою DWT на C */
#include "stm32f4xx.h"

void dwt_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk; /* Увімкнути трасування */
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;           /* Запустити лічильник */
    DWT->CYCCNT = 0;
}

uint32_t benchmark_matrix_multiply(void) {
    __asm__ volatile("" ::: "memory"); /* Бар'єр пам'яті компілятора */
    uint32_t start_cycles = DWT->CYCCNT;
    __asm__ volatile("" ::: "memory");

    /* Обчислювальний блок */
    calculate_inverse_park_transform();

    __asm__ volatile("" ::: "memory");
    uint32_t end_cycles = DWT->CYCCNT;
    __asm__ volatile("" ::: "memory");

    /* Завдяки модульній арифметиці uint32_t різниця правильна навіть при переповненні */
    return (end_cycles - start_cycles);
}
