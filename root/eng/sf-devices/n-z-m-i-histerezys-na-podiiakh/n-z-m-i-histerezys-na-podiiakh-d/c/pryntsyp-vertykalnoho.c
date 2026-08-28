#include <stdint.h>
#include <stdbool.h>

#define CHANNELS_COUNT 32
#define WINDOW_SIZE_M  8

/* Стан паралельного векторного фільтра на 32 канали */
typedef struct {
    uint32_t slices[WINDOW_SIZE_M]; /* Кільцевий буфер бітових зрізів */
    uint8_t  write_index;           /* Індекс запису нового зрізу */
    uint32_t output_mask;           /* 32 відфільтровані вихідні біти */
} vector_filter32_t;

void vector_filter32_init(vector_filter32_t *vf, uint32_t initial_levels) {
    for (int i = 0; i < WINDOW_SIZE_M; i++) {
        vf->slices[i] = initial_levels;
    }
    vf->write_index = 0;
    vf->output_mask = initial_levels;
}

/**
 * @brief Паралельне оновлення 32 дискретних каналів за фіксований час O(1)
 * Поріг активації N_on = 6 (бітове представлення: 1 1 0_2)
 * Поріг деактивації N_off = 2 (бітове представлення: 0 1 0_2)
 */
uint32_t vector_filter32_step(vector_filter32_t *vf, uint32_t raw_inputs_32) {
    /* Запис нового зрізу в кільцевий буфер */
    vf->slices[vf->write_index] = raw_inputs_32;
    vf->write_index = (vf->write_index + 1) % WINDOW_SIZE_M;

    /* Вертикальне 3-бітове додавання 8 зрізів за допомогою побітових суматорів */
    uint32_t s0 = 0, s1 = 0, s2 = 0;

    for (int i = 0; i < WINDOW_SIZE_M; i++) {
        uint32_t a = vf->slices[i];
        
        /* Додавання до 3-бітового акумулятора (s2:s1:s0) */
        uint32_t carry0 = s0 & a;
        s0 ^= a;

        uint32_t carry1 = s1 & carry0;
        s1 ^= carry0;

        s2 ^= carry1;
    }

    /* 
     * Тепер для кожного з 32 каналів сума одиниць дорівнює:
     * Count[i] = (s2[i] << 2) | (s1[i] << 1) | s0[i]  (значення від 0 до 8)
     * 
     * Логіка гістерезису:
     * Умова ввімкнення (Count >= 6): (s2 & s1)
     * Умова вимкнення  (Count <= 2): (~s2 & ~s1) | (~s2 & ~s0)
     */
    uint32_t set_condition   = s2 & s1;
    uint32_t reset_condition = (~s2 & ~s1) | (~s2 & ~s0);

    /* Оновлення станів без розгалужень */
    vf->output_mask = (vf->output_mask | set_condition) & ~reset_condition;

    return vf->output_mask;
}
