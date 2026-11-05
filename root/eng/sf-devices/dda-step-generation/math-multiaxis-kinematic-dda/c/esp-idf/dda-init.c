#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

#define NUM_AXES 3

typedef struct {
    int32_t delta;       // Переміщення осі у кроках
    int32_t accumulator; // Акумулятор помилки DDA
    int8_t direction;    // Напрямок руху (+1 або -1)
} dda_axis_t;

typedef struct {
    dda_axis_t axes[NUM_AXES];
    uint8_t lead_axis;   // Індекс ведучої осі (0..NUM_AXES-1)
    uint32_t total_steps;// Загальна кількість кроків (S_max)
    uint32_t current_step;// Поточний виконаний крок
} dda_generator_t;

// Ініціалізація DDA-вектора для 3 осей (X, Y, Z)
void dda_init(dda_generator_t *gen, int32_t dx, int32_t dy, int32_t dz) {
    int32_t deltas[NUM_AXES] = {dx, dy, dz};
    int32_t max_delta = 0;
    gen->lead_axis = 0;

    for (int i = 0; i < NUM_AXES; i++) {
        if (deltas[i] < 0) {
            gen->axes[i].direction = -1;
            gen->axes[i].delta = -deltas[i];
        } else {
            gen->axes[i].direction = 1;
            gen->axes[i].delta = deltas[i];
        }

        if (gen->axes[i].delta > max_delta) {
            max_delta = gen->axes[i].delta;
            gen->lead_axis = i;
        }
    }

    gen->total_steps = max_delta;
    gen->current_step = 0;

    // Ініціалізація акумуляторів E_0 = S_max / 2
    for (int i = 0; i < NUM_AXES; i++) {
        gen->axes[i].accumulator = max_delta / 2;
    }
}

// Виконання одного тику DDA в обробнику переривання
bool dda_step_tick(dda_generator_t *gen, bool step_out[NUM_AXES]) {
    if (gen->current_step >= gen->total_steps) {
        return false; // Траєкторію завершено
    }

    for (int i = 0; i < NUM_AXES; i++) {
        step_out[i] = false;
        if (i == gen->lead_axis) {
            step_out[i] = true; // Ведуча вісь завжди робить крок на кожному тику
        } else {
            // Оновлення акумулятора веденої осі
            gen->axes[i].accumulator += gen->axes[i].delta;
            if (gen->axes[i].accumulator >= (int32_t)gen->total_steps) {
                step_out[i] = true;
                gen->axes[i].accumulator -= gen->total_steps;
            }
        }
    }

    gen->current_step++;
    return true;
}
