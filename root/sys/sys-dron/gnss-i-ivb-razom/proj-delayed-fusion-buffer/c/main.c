#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define BUFFER_SIZE 256
#define BUFFER_MASK (BUFFER_SIZE - 1)

typedef struct {
    float x, y, z;
} vec3_t;

typedef struct {
    float w, x, y, z;
} quat_t;

/* Знімок навігаційного стану на певний момент часу */
typedef struct {
    uint32_t timestamp_ms;
    vec3_t pos;           /* NED координати (метри) */
    vec3_t vel;           /* NED швидкість (м/с) */
    quat_t q;             /* Орієнтація Body -> NED */
    vec3_t gyro_bias;     /* Зміщення гіроскопа (рад/с) */
    vec3_t accel_bias;    /* Зміщення акселерометра (м/с²) */
} nav_state_t;

/* Кільцевий буфер історичних станів */
typedef struct {
    nav_state_t buffer[BUFFER_SIZE];
    uint32_t head;
    uint32_t count;
} state_ring_buffer_t;

void ring_buffer_init(state_ring_buffer_t *rb) {
    memset(rb, 0, sizeof(state_ring_buffer_t));
}

void ring_buffer_push(state_ring_buffer_t *rb, const nav_state_t *state) {
    rb->buffer[rb->head & BUFFER_MASK] = *state;
    rb->head++;
    if (rb->count < BUFFER_SIZE) {
        rb->count++;
    }
}

/* Пошук найближчого стану в буфері за часовою міткою */
bool ring_buffer_find(const state_ring_buffer_t *rb, uint32_t target_time_ms, nav_state_t *out_state) {
    if (rb->count == 0) return false;

    uint32_t oldest_idx = (rb->head >= rb->count) ? (rb->head - rb->count) : 0;
    uint32_t oldest_time = rb->buffer[oldest_idx & BUFFER_MASK].timestamp_ms;
    uint32_t newest_time = rb->buffer[(rb->head - 1) & BUFFER_MASK].timestamp_ms;

    /* Перевірка виходу за межі буфера */
    if (target_time_ms < oldest_time || target_time_ms > newest_time) {
        return false;
    }

    /* Лінійний пошук від найновішого до найстарішого запису */
    for (uint32_t i = 1; i <= rb->count; ++i) {
        uint32_t idx = (rb->head - i) & BUFFER_MASK;
        if (rb->buffer[idx].timestamp_ms <= target_time_ms) {
            *out_state = rb->buffer[idx];
            return true;
        }
    }
    return false;
}

/* Обчислення інновації та перевірка за Махаланобісом (Gating) */
bool evaluate_gnss_innovation(
    const nav_state_t *historical_state,
    const vec3_t *gnss_pos,
    float pos_noise_var,
    float state_var,
    vec3_t *out_innovation,
    float *out_gain
) {
    /* Інновація: y = z - H * x_hist */
    out_innovation->x = gnss_pos->x - historical_state->pos.x;
    out_innovation->y = gnss_pos->y - historical_state->pos.y;
    out_innovation->z = gnss_pos->z - historical_state->pos.z;

    /* Коваріація інновації: S = P + R */
    float S = state_var + pos_noise_var;
    if (S <= 1e-6f) return false;

    /* Квадрат відстані Махаланобіса d² = yᵀ · S⁻¹ · y */
    float d2 = (out_innovation->x * out_innovation->x +
                out_innovation->y * out_innovation->y +
                out_innovation->z * out_innovation->z) / S;

    /* Поріг відсікання викидів: χ² для 3 ступенів вільності (99% = 11.34) */
    const float GATE_THRESHOLD = 11.34f;
    if (d2 > GATE_THRESHOLD) {
        return false; /* Викид (наприклад, перевідбиття сигналу або стрибок псевдодальності) */
    }

    /* Підсилення Калмана K = P / S */
    *out_gain = state_var / S;
    return true;
}

/* Ретроспективне оновлення поточного стану (Error-State Feedback) */
void apply_delayed_correction(
    nav_state_t *current_state,
    const vec3_t *innovation,
    float gain
) {
    /* Поправка положення та швидкості інжектується в поточний стан */
    current_state->pos.x += gain * innovation->x;
    current_state->pos.y += gain * innovation->y;
    current_state->pos.z += gain * innovation->z;

    /* Поправка швидкості через крос-коваріацію */
    float vel_gain = gain * 0.45f;
    current_state->vel.x += vel_gain * innovation->x;
    current_state->vel.y += vel_gain * innovation->y;
    current_state->vel.z += vel_gain * innovation->z;
}
