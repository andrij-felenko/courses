#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <math.h>

#define NOWCAST_HOURS 12

typedef struct {
    float concentrations[NOWCAST_HOURS]; // Буфер погодинних концентрацій
    bool valid[NOWCAST_HOURS];           // Прапорці валідності даних
    size_t head;                         // Індекс найновішого вимірювання (C0)
    size_t count;                        // Кількість заповнених годин (до 12)
} nowcast_filter_t;

// Ініціалізація структури фільтра
void nowcast_init(nowcast_filter_t *f) {
    if (!f) return;
    f->head = 0;
    f->count = 0;
    for (size_t i = 0; i < NOWCAST_HOURS; ++i) {
        f->concentrations[i] = 0.0f;
        f->valid[i] = false;
    }
}

// Додавання нового вимірювання в кільцевий буфер
void nowcast_push(nowcast_filter_t *f, float concentration, bool is_valid) {
    if (!f) return;
    // Зсуваємо голову назад на 1 позицію по кільцю: новий елемент стає індексом 0
    f->head = (f->head + NOWCAST_HOURS - 1) % NOWCAST_HOURS;
    f->concentrations[f->head] = is_valid ? concentration : 0.0f;
    f->valid[f->head] = is_valid;
    if (f->count < NOWCAST_HOURS) {
        f->count++;
    }
}

// Обчислення адаптивної концентрації NowCast
bool nowcast_calculate(const nowcast_filter_t *f, float *out_result) {
    if (!f || !out_result || f->count == 0) return false;

    // Перевірка умови EPA: мінімум 2 з 3 останніх годин мають бути валідними
    size_t recent_valid = 0;
    size_t check_limit = f->count < 3 ? f->count : 3;
    for (size_t i = 0; i < check_limit; ++i) {
        size_t idx = (f->head + i) % NOWCAST_HOURS;
        if (f->valid[idx]) recent_valid++;
    }
    if (recent_valid < 2 && f->count >= 3) return false;

    // Пошук мінімального та максимального значень серед валідних годин
    float c_min = 1e9f;
    float c_max = -1.0f;
    size_t total_valid = 0;

    for (size_t i = 0; i < f->count; ++i) {
        size_t idx = (f->head + i) % NOWCAST_HOURS;
        if (f->valid[idx]) {
            float val = f->concentrations[idx];
            if (val < c_min) c_min = val;
            if (val > c_max) c_max = val;
            total_valid++;
        }
    }

    if (total_valid == 0) return false;

    // Обчислення вагового коефіцієнта w
    float w = 1.0f;
    if (c_max > 0.0f) {
        w = c_min / c_max;
        if (w < 0.5f) w = 0.5f;
    }

    // Зважене експоненційне сумування
    float sum_weighted_conc = 0.0f;
    float sum_weights = 0.0f;
    float current_weight = 1.0f;

    for (size_t i = 0; i < f->count; ++i) {
        size_t idx = (f->head + i) % NOWCAST_HOURS;
        if (f->valid[idx]) {
            sum_weighted_conc += f->concentrations[idx] * current_weight;
            sum_weights += current_weight;
        }
        current_weight *= w;
    }

    if (sum_weights <= 0.0f) return false;
    *out_result = sum_weighted_conc / sum_weights;
    return true;
}
