#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t width;                   /* Ширина вікна стрічки: 32, 64 або 128 бітів */
    uint8_t fingerprint_bits;         /* Довжина відбитка r у бітах: від 4 до 16 */
    uint8_t overhead_percent;         /* Коефіцієнт надлишковості слотів у відсотках */
    uint16_t max_retries;             /* Максимальна кількість спроб із новим seed */
    uint64_t initial_seed;            /* Початковий seed хешування */
    bool use_homogeneous_scaling;     /* Однорідне масштабування проти крайових ефектів */
    bool use_interleaved_layout;      /* Чергування слотів для кеш-ліній CPU */
} RibbonOptions;

void ribbon_options_init_default(RibbonOptions *opts);
