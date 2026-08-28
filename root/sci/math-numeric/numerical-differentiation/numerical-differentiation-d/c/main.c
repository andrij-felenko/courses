#include <stdbool.h>
#include <math.h>

/* --- 1. Фільтрований диференціатор першого порядку (LPF Differentiator) --- */
typedef struct {
    float prev_input;    /* попереднє значення x[k-1] */
    float output;        /* поточна оцінка похідної y[k] */
    float cutoff_hz;     /* частота зрізу фільтра низьких частот */
} LowPassDifferentiator;

void lpf_diff_init(LowPassDifferentiator* self, float cutoff_hz) {
    self->prev_input = 0.0f;
    self->output = 0.0f;
    self->cutoff_hz = (cutoff_hz > 0.1f) ? cutoff_hz : 0.1f;
}

float lpf_diff_update(LowPassDifferentiator* self, float input, float dt) {
    if (dt <= 0.000001f) {
        return self->output; /* захист від некоректного кроку часу */
    }
    
    /* Розрахунок коефіцієнта згладжування фільтра низьких частот: alpha = dt / (RC + dt) */
    const float tau = 1.0f / (2.0f * 3.1415926535f * self->cutoff_hz);
    const float alpha = dt / (tau + dt);
    
    /* Чисельна зворотна різниця */
    const float raw_diff = (input - self->prev_input) / dt;
    self->prev_input = input;
    
    /* Експоненційне згладжування похідної */
    self->output += alpha * (raw_diff - self->output);
    return self->output;
}

/* --- 2. Диференціатор Савицького–Голея (вікно 5 точок, поліном 2-го степеня) --- */
typedef struct {
    float buf[5];        /* кільцевий буфер вимірів положення */
    int head;            /* індекс останнього доданого елемента */
    int count;           /* кількість накопичених відліків */
} SavitzkyGolay5;

void sg5_init(SavitzkyGolay5* self) {
    for (int i = 0; i < 5; ++i) self->buf[i] = 0.0f;
    self->head = 0;
    self->count = 0;
}

void sg5_push(SavitzkyGolay5* self, float val) {
    self->head = (self->head + 1) % 5;
    self->buf[self->head] = val;
    if (self->count < 5) self->count++;
}

bool sg5_compute(const SavitzkyGolay5* self, float dt, float* out_velocity, float* out_accel) {
    if (self->count < 5 || dt <= 0.000001f) {
        return false; /* буфер ще не заповнено для повноцінної згортки */
    }
    
    /* Витягуємо відліки від найстарішого до найновішого: y_0, y_1, y_2, y_3, y_4 */
    float y[5];
    for (int i = 0; i < 5; ++i) {
        int idx = (self->head - 4 + i + 5) % 5;
        y[i] = self->buf[idx];
    }
    
    /* Ваги Савицького–Голея для 1-ї похідної: [-2, -1, 0, 1, 2] / (10 * dt) */
    if (out_velocity) {
        *out_velocity = (-2.0f * y[0] - 1.0f * y[1] + 0.0f * y[2] + 1.0f * y[3] + 2.0f * y[4]) / (10.0f * dt);
    }
    
    /* Ваги Савицького–Голея для 2-ї похідної: [2, -1, -2, -1, 2] / (7 * dt^2) */
    if (out_accel) {
        *out_accel = (2.0f * y[0] - 1.0f * y[1] - 2.0f * y[2] - 1.0f * y[3] + 2.0f * y[4]) / (7.0f * dt * dt);
    }
    
    return true;
}
