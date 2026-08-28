#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PI_CONST 3.14159265358979323846f
#define TWO_PI   6.28318530717958647692f
#define ONE_BY_SQRT3 0.57735026919f
#define SQRT3        1.73205080757f

typedef struct {
    float x;
    float y;
    float z;
} Vec3;

typedef struct {
    float duty_a;
    float duty_b;
    float duty_c;
    uint8_t sector;
} SvpwmDuty;

typedef struct {
    float b0, b1, b2;
    float a1, a2;
    float x1, x2;
    float y1, y2;
} BiquadNotchFilter;

typedef struct {
    float kp;
    float ki;
    float kd;
    float integral;
    float prev_error;
    float out_max;
    float i_max;
    float d_filter_alpha; /* Коефіцієнт ФНЧ для похідної */
    float prev_d_filtered;
} PidController;

typedef struct {
    uint8_t pole_pairs;      /* Кількість пар полюсів (11 для 22P або 14 для 28P) */
    float zero_offset_rad;   /* Електричний нульовий зсув енкодера */
    float v_bus;             /* Напруга шини живлення (В) */
    float u_limit;           /* Максимальна амплітуда вихідної напруги */
    
    /* Стан осі */
    float mech_angle_rad;    /* Механічний кут з енкодера */
    float elec_angle_rad;    /* Електричний кут для перетворення Парка */
    float gyro_rate_rad_s;   /* Кутова швидкість з гіроскопа камери */
    
    /* Фільтрація резонансів */
    BiquadNotchFilter notch;
    
    /* Каскадні регулятори */
    PidController pos_pid;   /* Зовнішній контур: кут -> бажана швидкість */
    PidController rate_pid;  /* Внутрішній контур: швидкість -> напруга U_q */
    
    /* Виходи FOC */
    float u_d;
    float u_q;
    SvpwmDuty svpwm;
} GimbalAxis;

/* Нормалізація кута в межі [0, 2π) */
static inline float normalize_angle(float angle) {
    float a = fmodf(angle, TWO_PI);
    return (a >= 0.0f) ? a : (a + TWO_PI);
}

/* Ініціалізація біквадратного режекторного фільтра (Notch Filter) */
void notch_filter_init(BiquadNotchFilter *f, float center_freq_hz, float q_factor, float sample_rate_hz) {
    float omega = 2.0f * PI_CONST * center_freq_hz / sample_rate_hz;
    float sn = sinf(omega);
    float cs = cosf(omega);
    float alpha = sn / (2.0f * q_factor);
    
    float a0 = 1.0f + alpha;
    f->b0 = 1.0f / a0;
    f->b1 = (-2.0f * cs) / a0;
    f->b2 = 1.0f / a0;
    f->a1 = (-2.0f * cs) / a0;
    f->a2 = (1.0f - alpha) / a0;
    
    f->x1 = f->x2 = f->y1 = f->y2 = 0.0f;
}

/* Обробка вибірки через Notch-фільтр */
float notch_filter_update(BiquadNotchFilter *f, float in) {
    float out = f->b0 * in + f->b1 * f->x1 + f->b2 * f->x2 - f->a1 * f->y1 - f->a2 * f->y2;
    f->x2 = f->x1;
    f->x1 = in;
    f->y2 = f->y1;
    f->y1 = out;
    return out;
}

/* Обчислення електричного кута ротора */
void gimbal_axis_update_electrical_angle(GimbalAxis *axis, float raw_mech_angle) {
    axis->mech_angle_rad = raw_mech_angle;
    float elec = ((float)axis->pole_pairs * raw_mech_angle) - axis->zero_offset_rad;
    axis->elec_angle_rad = normalize_angle(elec);
}

/* Генератор просторово-векторної модуляції (SVPWM) */
SvpwmDuty svpwm_generate(float u_alpha, float u_beta, float v_bus) {
    SvpwmDuty out;
    if (v_bus <= 0.01f) {
        out.duty_a = out.duty_b = out.duty_c = 0.5f;
        out.sector = 0;
        return out;
    }
    
    float u_a_norm = u_alpha / v_bus;
    float u_b_norm = u_beta / v_bus;
    
    float v1 = u_b_norm;
    float v2 = (SQRT3 * u_a_norm - u_b_norm) * 0.5f;
    float v3 = (-SQRT3 * u_a_norm - u_b_norm) * 0.5f;
    
    uint8_t sector = 0;
    if (v1 > 0.0f) sector |= 1;
    if (v2 > 0.0f) sector |= 2;
    if (v3 > 0.0f) sector |= 4;
    
    float t1 = 0.0f, t2 = 0.0f;
    float ta = 0.5f, tb = 0.5f, tc = 0.5f;
    
    switch (sector) {
        case 3: /* Сектор 1 (0° .. 60°) */
            t1 = SQRT3 * u_a_norm - u_b_norm;
            t2 = 2.0f * u_b_norm;
            out.sector = 1;
            break;
        case 1: /* Сектор 2 (60° .. 120°) */
            t1 = SQRT3 * u_a_norm + u_b_norm;
            t2 = -SQRT3 * u_a_norm + u_b_norm;
            out.sector = 2;
            break;
        case 5: /* Сектор 3 (120° .. 180°) */
            t1 = 2.0f * u_b_norm;
            t2 = -SQRT3 * u_a_norm - u_b_norm;
            out.sector = 3;
            break;
        case 4: /* Сектор 4 (180° .. 240°) */
            t1 = -SQRT3 * u_a_norm + u_b_norm;
            t2 = -2.0f * u_b_norm;
            out.sector = 4;
            break;
        case 6: /* Сектор 5 (240° .. 300°) */
            t1 = -SQRT3 * u_a_norm - u_b_norm;
            t2 = SQRT3 * u_a_norm - u_b_norm;
            out.sector = 5;
            break;
        case 2: /* Сектор 6 (300° .. 360°) */
            t1 = -2.0f * u_b_norm;
            t2 = SQRT3 * u_a_norm + u_b_norm;
            out.sector = 6;
            break;
        default:
            t1 = 0.0f;
            t2 = 0.0f;
            out.sector = 0;
            break;
    }
    
    float t_sum = t1 + t2;
    if (t_sum > 1.0f) {
        t1 /= t_sum;
        t2 /= t_sum;
    }
    
    float t0 = 1.0f - t1 - t2;
    float t_half0 = t0 * 0.5f;
    
    switch (out.sector) {
        case 1:
            ta = t1 + t2 + t_half0;
            tb = t2 + t_half0;
            tc = t_half0;
            break;
        case 2:
            ta = t1 + t_half0;
            tb = t1 + t2 + t_half0;
            tc = t_half0;
            break;
        case 3:
            ta = t_half0;
            tb = t1 + t2 + t_half0;
            tc = t2 + t_half0;
            break;
        case 4:
            ta = t_half0;
            tb = t1 + t_half0;
            tc = t1 + t2 + t_half0;
            break;
        case 5:
            ta = t2 + t_half0;
            tb = t_half0;
            tc = t1 + t2 + t_half0;
            break;
        case 6:
            ta = t1 + t2 + t_half0;
            tb = t_half0;
            tc = t1 + t_half0;
            break;
        default:
            ta = tb = tc = 0.5f;
            break;
    }
    
    out.duty_a = ta;
    out.duty_b = tb;
    out.duty_c = tc;
    return out;
}
