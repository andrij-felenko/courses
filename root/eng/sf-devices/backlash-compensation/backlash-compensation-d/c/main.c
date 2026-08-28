#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_AXES 3
#define DIR_POS  1
#define DIR_NEG -1

typedef enum {
    ENGAGED_NEG = -1,
    CROSSING_GAP = 0,
    ENGAGED_POS = 1
} backlash_state_t;

typedef struct {
    int32_t backlash_steps;     /* Повний люфт в абсолютних кроках */
    int32_t max_comp_speed_hz;  /* Максимальна частота імпульсів вибірки люфту */
    int32_t comp_accel_hz2;     /* Прискорення вибірки люфту (крок/с^2) */
    int32_t deadband_threshold; /* Поріг ігнорування шуму реверсу (кроки) */
} backlash_config_t;

typedef struct {
    backlash_config_t config;
    backlash_state_t  state;
    int8_t            last_dir;
    int32_t           gap_progress_steps; /* Скільки кроків у зазорі пройдено */
    int32_t           current_comp_speed_hz;
    int32_t           accumulated_error;  /* Залишкова похибка інтерполяції */
} backlash_axis_t;

static backlash_axis_t axes[MAX_AXES];

void backlash_init_axis(uint8_t axis_idx, int32_t backlash_steps, int32_t max_speed_hz, int32_t accel_hz2) {
    if (axis_idx >= MAX_AXES) return;
    
    axes[axis_idx].config.backlash_steps = (backlash_steps > 0) ? backlash_steps : 0;
    axes[axis_idx].config.max_comp_speed_hz = (max_speed_hz > 100) ? max_speed_hz : 1000;
    axes[axis_idx].config.comp_accel_hz2 = (accel_hz2 > 100) ? accel_hz2 : 5000;
    axes[axis_idx].config.deadband_threshold = 2; /* 2 кроки мінімального порогу */
    
    axes[axis_idx].state = ENGAGED_POS;
    axes[axis_idx].last_dir = DIR_POS;
    axes[axis_idx].gap_progress_steps = 0;
    axes[axis_idx].current_comp_speed_hz = 0;
    axes[axis_idx].accumulated_error = 0;
}

/**
 * Обробка планового кроку в циклі інтерполятора (викликається з періодом dt).
 * @param axis_idx     Індекс осі (0=X, 1=Y, 2=Z)
 * @param commanded_dir Напрямок планового руху (DIR_POS або DIR_NEG)
 * @param dt_seconds    Крок квантування часу інтерполятора (наприклад, 0.001 для 1 кГц)
 * @param[out] out_steps Кількість кроків для відправки в апаратний буфер DDA
 * @param[out] is_reversing Чи перебуває вісь у фазі вибірки люфту
 */
void backlash_process_step(uint8_t axis_idx, int8_t commanded_dir, float dt_seconds, 
                           int32_t *out_steps, bool *is_reversing) {
    if (axis_idx >= MAX_AXES || !out_steps || !is_reversing) return;
    
    backlash_axis_t *axis = &axes[axis_idx];
    *out_steps = 0;
    *is_reversing = false;

    if (axis->config.backlash_steps == 0) {
        /* Люфт вимкнено — прозорий режим */
        *out_steps = 1;
        return;
    }

    /* Виявлення зміни напрямку руху */
    if (commanded_dir != 0 && commanded_dir != axis->last_dir) {
        if (axis->state != CROSSING_GAP) {
            axis->state = CROSSING_GAP;
            axis->gap_progress_steps = 0;
            axis->current_comp_speed_hz = 0;
        }
        axis->last_dir = commanded_dir;
    }

    if (axis->state == CROSSING_GAP) {
        *is_reversing = true;
        
        /* Плавний розгін вибірки люфту з обмеженням за a_max */
        axis->current_comp_speed_hz += (int32_t)(axis->config.comp_accel_hz2 * dt_seconds);
        if (axis->current_comp_speed_hz > axis->config.max_comp_speed_hz) {
            axis->current_comp_speed_hz = axis->config.max_comp_speed_hz;
        }

        /* Обчислення кроків для цього кванта часу з накопиченням залишку */
        float step_float = (float)axis->current_comp_speed_hz * dt_seconds;
        int32_t step_batch = (int32_t)step_float;
        axis->accumulated_error += (int32_t)((step_float - (float)step_batch) * 1000.0f);
        
        if (axis->accumulated_error >= 1000) {
            step_batch += 1;
            axis->accumulated_error -= 1000;
        }

        /* Перевірка чи не перевищуємо залишок люфту */
        int32_t remaining = axis->config.backlash_steps - axis->gap_progress_steps;
        if (step_batch >= remaining) {
            step_batch = remaining;
            axis->gap_progress_steps += step_batch;
            axis->state = (axis->last_dir == DIR_POS) ? ENGAGED_POS : ENGAGED_NEG;
            axis->current_comp_speed_hz = 0;
            *is_reversing = false;
        } else {
            axis->gap_progress_steps += step_batch;
        }

        *out_steps = step_batch;
    } else {
        /* Зачеплення встановлено — передаємо 1 плановий крок */
        *out_steps = 1;
    }
}
