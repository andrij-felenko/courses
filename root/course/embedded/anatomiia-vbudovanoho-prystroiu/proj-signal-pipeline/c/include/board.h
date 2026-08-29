#ifndef BOARD_H
#define BOARD_H

#include <stdint.h>

/* Апаратний шар для STM32G071 (Cortex-M0+, 48 МГц):
   TIM2 задає період квантування й сам запускає АЦП, DMA кладе результат
   у пам'ять і піднімає переривання, TIM3_CH1 віддає ШІМ.
   Процесор у самому вимірюванні не бере участі взагалі. */

#define SAMPLE_PERIOD_HZ 100U /* 10 мс — той самий dt, що зашитий у коефіцієнти */

typedef enum {
    BOARD_OK = 0,
    BOARD_ERR_PLL_TIMEOUT,
    BOARD_ERR_ADC_CALIBRATION,
    BOARD_ERR_ADC_NOT_READY,
    BOARD_ERR_BAD_CONFIG
} board_status_t;

board_status_t board_init(void);

/* Запис у регістр порівняння TIM3->CCR1. Значення береться на наступному
   оновленні таймера цілком — регістр із попереднім завантаженням. */
void board_set_duty(uint16_t duty);

/* Аварійне зупинення: ШІМ у нуль, переривання вимкнено, вічний цикл. */
void board_panic(board_status_t status);

/* Гачок застосунку. Викликається з переривання завершення передачі DMA,
   рівно раз на період квантування. Визначено в main.c. */
void app_on_sample(uint16_t raw_adc);

#endif /* BOARD_H */
