#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>

#define STATE_BUFFER_CAPACITY 128
#define STATE_DIM 6

/* Вектор стану: [pos_x, pos_y, pos_z, vel_x, vel_y, vel_z] */
typedef struct {
    uint64_t timestamp_us;
    float state[STATE_DIM];
    float transition_matrix_diag[STATE_DIM];
} NavStateSnapshot;

/* Кільцевий буфер станів для відкладеного злиття */
typedef struct {
    NavStateSnapshot buffer[STATE_BUFFER_CAPACITY];
    size_t head;
    size_t count;
} StateDelayBuffer;

void state_buffer_init(StateDelayBuffer *buf) {
    buf->head = 0;
    buf->count = 0;
    memset(buf->buffer, 0, sizeof(buf->buffer));
}

void state_buffer_push(StateDelayBuffer *buf, uint64_t timestamp_us, const float state[STATE_DIM], const float phi_diag[STATE_DIM]) {
    buf->buffer[buf->head].timestamp_us = timestamp_us;
    for (size_t i = 0; i < STATE_DIM; ++i) {
        buf->buffer[buf->head].state[i] = state[i];
        buf->buffer[buf->head].transition_matrix_diag[i] = phi_diag[i];
    }
    buf->head = (buf->head + 1) % STATE_BUFFER_CAPACITY;
    if (buf->count < STATE_BUFFER_CAPACITY) {
        buf->count++;
    }
}

/* Пошук та інтерполяція ретроспективного стану за міткою часу */
bool state_buffer_get_interpolated(const StateDelayBuffer *buf, uint64_t target_time_us, float out_state[STATE_DIM]) {
    if (buf->count < 2) {
        return false;
    }

    size_t newest_idx = (buf->head + STATE_BUFFER_CAPACITY - 1) % STATE_BUFFER_CAPACITY;
    size_t oldest_idx = (buf->head + STATE_BUFFER_CAPACITY - buf->count) % STATE_BUFFER_CAPACITY;

    uint64_t t_newest = buf->buffer[newest_idx].timestamp_us;
    uint64_t t_oldest = buf->buffer[oldest_idx].timestamp_us;

    if (target_time_us > t_newest || target_time_us < t_oldest) {
        return false; /* Затримка виходить за межі глибини буфера */
    }

    /* Пошук сусідніх кадрів зворотним переглядом */
    for (size_t i = 0; i < buf->count - 1; ++i) {
        size_t idx_curr = (newest_idx + STATE_BUFFER_CAPACITY - i) % STATE_BUFFER_CAPACITY;
        size_t idx_prev = (idx_curr + STATE_BUFFER_CAPACITY - 1) % STATE_BUFFER_CAPACITY;

        uint64_t t_curr = buf->buffer[idx_curr].timestamp_us;
        uint64_t t_prev = buf->buffer[idx_prev].timestamp_us;

        if (target_time_us >= t_prev && target_time_us <= t_curr) {
            float alpha = 0.0f;
            if (t_curr > t_prev) {
                alpha = (float)(target_time_us - t_prev) / (float)(t_curr - t_prev);
            }
            for (size_t j = 0; j < STATE_DIM; ++j) {
                out_state[j] = (1.0f - alpha) * buf->buffer[idx_prev].state[j] +
                               alpha * buf->buffer[idx_curr].state[j];
            }
            return true;
        }
    }
    return false;
}

/* Відкладене злиття спостереження позиції (Delayed Fusion) */
bool ekf_fuse_delayed_position(StateDelayBuffer *buf, uint64_t meas_time_us,
                               const float z_meas[3], const float r_cov[3],
                               float current_state[STATE_DIM]) {
    float hist_state[STATE_DIM];
    if (!state_buffer_get_interpolated(buf, meas_time_us, hist_state)) {
        return false; /* Не вдалося знайти історичний стан */
    }

    /* Обчислення нев'язки (інновації) на історичному стані */
    float innovation[3];
    for (size_t i = 0; i < 3; ++i) {
        innovation[i] = z_meas[i] - hist_state[i];
    }

    /* Спрощене діагональне підсилення Калмана для позиції */
    float k_gain[3];
    for (size_t i = 0; i < 3; ++i) {
        float p_cov = 1.0f; /* Апріорна дисперсія оцінки */
        k_gain[i] = p_cov / (p_cov + r_cov[i]);
    }

    /* Корекція поточного стану з урахуванням прямого переносу */
    for (size_t i = 0; i < 3; ++i) {
        float delta_pos = k_gain[i] * innovation[i];
        current_state[i] += delta_pos;
        current_state[i + 3] += delta_pos * 0.5f; /* Зв'язок корекції швидкості */
    }

    return true;
}

int main(void) {
    StateDelayBuffer buf;
    state_buffer_init(&buf);

    float current_state[STATE_DIM] = {0.0f, 0.0f, 0.0f, 10.0f, 0.0f, 0.0f};
    float phi_diag[STATE_DIM] = {1.0f, 1.0f, 1.0f, 1.0f, 1.0f, 1.0f};

    uint64_t current_time_us = 1000000; /* 1.000 с */
    uint64_t dt_us = 10000;             /* 10 мс (100 Гц IMU) */

    /* Імітація руху з постійною швидкістю 10 м/с вздовж осі X */
    for (int k = 0; k < 30; ++k) {
        current_time_us += dt_us;
        current_state[0] += current_state[3] * ((float)dt_us / 1000000.0f);
        state_buffer_push(&buf, current_time_us, current_state, phi_diag);
    }

    /* Прибуття запізнілого вимірювання GNSS із затримкою 150 мс */
    uint64_t gnss_delay_us = 150000;
    uint64_t gnss_time_us = current_time_us - gnss_delay_us;

    /* Фізична позиція на момент 150 мс тому з невеликим шумом вимірювання */
    float z_gnss[3] = {1.55f, 0.0f, 0.0f};
    float r_cov[3] = {0.25f, 0.25f, 0.25f};

    printf("Час: %llu мкс, Поточна позиція X до корекції: %.3f м\n",
           (unsigned long long)current_time_us, current_state[0]);

    if (ekf_fuse_delayed_position(&buf, gnss_time_us, z_gnss, r_cov, current_state)) {
        printf("Злиття успішне. Скоригована позиція X: %.3f м\n", current_state[0]);
    } else {
        printf("Помилка відкладеного злиття!\n");
    }

    return 0;
}
