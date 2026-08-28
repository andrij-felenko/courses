#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    FRAME_TYPE_I = 0,
    FRAME_TYPE_P = 1,
    FRAME_TYPE_B = 2
} frame_type_t;

typedef struct {
    double bitrate_kbps;     // цільовий бітрейт каналу (кбіт/с)
    double fps;              // частота кадрів (fps)
    double bufsize_kbits;    // місткість буфера VBV (кбіт)
    double buffer_fullness;  // поточне наповнення буфера (кбіт)
    
    // Ковзна модель складності X = S_bits * Qstep для I, P, B
    double complexity_x[3];
    int    last_qp[3];
    int    gop_size;
    int    frame_in_gop;
} vbv_rate_control_t;

// Ініціалізація регулятора
void vbv_rc_init(vbv_rate_control_t *rc, double bitrate_kbps, double fps, 
                 double bufsize_kbits, double initial_occupancy, int gop_size) {
    rc->bitrate_kbps = bitrate_kbps;
    rc->fps = fps;
    rc->bufsize_kbits = bufsize_kbits;
    // Стартове наповнення буфера (типово 90% для швидкого старту без Underflow)
    rc->buffer_fullness = bufsize_kbits * initial_occupancy;
    rc->gop_size = gop_size;
    rc->frame_in_gop = 0;

    // Базові оцінки складності для старту
    double bits_per_frame = (bitrate_kbps * 1000.0) / fps;
    double default_qstep = 4.0; // відповідає QP ~ 26
    rc->complexity_x[FRAME_TYPE_I] = bits_per_frame * 4.0 * default_qstep;
    rc->complexity_x[FRAME_TYPE_P] = bits_per_frame * 1.0 * default_qstep;
    rc->complexity_x[FRAME_TYPE_B] = bits_per_frame * 0.4 * default_qstep;

    rc->last_qp[FRAME_TYPE_I] = 24;
    rc->last_qp[FRAME_TYPE_P] = 26;
    rc->last_qp[FRAME_TYPE_B] = 28;
}

// Переведення QP у крок квантування Qstep і назад
static inline double qp_to_qstep(int qp) {
    return 0.625 * pow(2.0, (double)qp / 6.0);
}

static inline int qstep_to_qp(double qstep) {
    int qp = (int)round(6.0 * log2(qstep / 0.625));
    if (qp < 1) qp = 1;
    if (qp > 51) qp = 51;
    return qp;
}

// Планування QP перед кодуванням кадру
int vbv_rc_plan_frame(vbv_rate_control_t *rc, frame_type_t type, double satd_complexity, double *out_target_bits) {
    double bits_in_per_frame = (rc->bitrate_kbps * 1000.0) / rc->fps;
    double buf_bits = rc->buffer_fullness * 1000.0;
    double max_buf_bits = rc->bufsize_kbits * 1000.0;

    // 1. Базовий цільовий розмір кадру на основі співвідношення складностей
    double target_bits;
    if (type == FRAME_TYPE_I) {
        target_bits = bits_in_per_frame * 3.5;
    } else if (type == FRAME_TYPE_P) {
        target_bits = bits_in_per_frame * 1.0;
    } else {
        target_bits = bits_in_per_frame * 0.4;
    }

    // Модуляція вхідною складністю SATD від Lookahead (якщо передано)
    if (satd_complexity > 0.0) {
        target_bits *= satd_complexity;
    }

    // 2. VBV обмеження: захист від Underflow та Overflow
    // Захист дна буфера: буфер не повинен опуститися нижче 10%
    double min_buf_safety = 0.10 * max_buf_bits;
    double max_allowed_bits = buf_bits + bits_in_per_frame - min_buf_safety;
    if (max_allowed_bits < bits_in_per_frame * 0.2) {
        max_allowed_bits = bits_in_per_frame * 0.2;
    }
    if (target_bits > max_allowed_bits) {
        target_bits = max_allowed_bits;
    }

    // Захист стелі буфера: буфер не повинен переповнитися вище 95%
    double max_buf_ceiling = 0.95 * max_buf_bits;
    double min_allowed_bits = buf_bits + bits_in_per_frame - max_buf_ceiling;
    if (min_allowed_bits > 0 && target_bits < min_allowed_bits) {
        target_bits = min_allowed_bits;
    }

    *out_target_bits = target_bits;

    // 3. Розрахунок QP з моделі складності Qstep = X / target_bits
    double qstep = rc->complexity_x[type] / target_bits;
    int qp = qstep_to_qp(qstep);

    // Обмеження різкої зміни QP (не більше ±2 одиниць за кадр)
    int prev_qp = rc->last_qp[type];
    if (qp > prev_qp + 2) qp = prev_qp + 2;
    if (qp < prev_qp - 2) qp = prev_qp - 2;

    return qp;
}

// Оновлення стану після фактичного кодування кадру
void vbv_rc_update_frame(vbv_rate_control_t *rc, frame_type_t type, int used_qp, double actual_bits) {
    double bits_in_per_frame = (rc->bitrate_kbps * 1000.0) / rc->fps;
    
    // Оновлення віртуального буфера: приплив з каналу мінус витрачені біти
    rc->buffer_fullness += (bits_in_per_frame - actual_bits) / 1000.0;
    
    // Затискання меж буфера
    if (rc->buffer_fullness > rc->bufsize_kbits) {
        rc->buffer_fullness = rc->bufsize_kbits;
    }
    if (rc->buffer_fullness < 0.0) {
        rc->buffer_fullness = 0.0; // Underflow зафіксовано
    }

    // Оновлення ковної моделі складності X = S_actual * Qstep
    double qstep = qp_to_qstep(used_qp);
    double inst_x = actual_bits * qstep;
    double alpha = 0.85; // коефіцієнт інерції ковзного середнього
    rc->complexity_x[type] = alpha * rc->complexity_x[type] + (1.0 - alpha) * inst_x;

    rc->last_qp[type] = used_qp;
    rc->frame_in_gop = (rc->frame_in_gop + 1) % rc->gop_size;
}
