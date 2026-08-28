#include <stdint.h>
#include <stdbool.h>

#define ADC_MAX_CODE       4095U
#define ADC_VREF_MV        3300U
#define PWM_MAX_DUTY       65535U

/* Структура стану ПІД-регулятора */
typedef struct {
    int32_t kp;              /* Пропорційний коефіцієнт у форматі Q8 (Kp * 256) */
    int32_t ki;              /* Інтегральний коефіцієнт у форматі Q8 (Ki * 256) */
    int32_t kd;              /* Диференційний коефіцієнт у форматі Q8 (Kd * 256) */
    int32_t integral_accum;  /* Накопичена інтегральна сума */
    int32_t prev_error;      /* Помилка регулювання на попередньому кроці */
    int32_t out_min;         /* Нижня межа керуючого сигналу */
    int32_t out_max;         /* Верхня межа керуючого сигналу */
} PidController;

/* Структура стану експоненційного фільтра EMA */
typedef struct {
    int32_t filtered_val;    /* Поточне згладжене значення */
    uint8_t shift_k;         /* Коефіцієнт згладжування: alpha = 1 / (2^shift_k) */
    bool initialized;        /* Прапорець первинної ініціалізації */
} EmaFilter;

/* Ініціалізація фільтра */
void ema_filter_init(EmaFilter *filter, uint8_t shift_k) {
    filter->filtered_val = 0;
    filter->shift_k = shift_k;
    filter->initialized = false;
}

/* Оновлення стану фільтра новим відліком */
int32_t ema_filter_update(EmaFilter *filter, int32_t new_val) {
    if (!filter->initialized) {
        filter->filtered_val = new_val;
        filter->initialized = true;
        return new_val;
    }
    filter->filtered_val += (new_val - filter->filtered_val) >> filter->shift_k;
    return filter->filtered_val;
}

/* Ініціалізація ПІД-регулятора */
void pid_init(PidController *pid, int32_t kp_q8, int32_t ki_q8, int32_t kd_q8,
              int32_t out_min, int32_t out_max) {
    pid->kp = kp_q8;
    pid->ki = ki_q8;
    pid->kd = kd_q8;
    pid->integral_accum = 0;
    pid->prev_error = 0;
    pid->out_min = out_min;
    pid->out_max = out_max;
}

/* Розрахунок чергового кроку ПІД-регулювання */
int32_t pid_update(PidController *pid, int32_t setpoint, int32_t measured) {
    int32_t error = setpoint - measured;

    /* Пропорційна складова: (Kp * error) / 256 */
    int32_t p_term = (pid->kp * error) >> 8;

    /* Інтегральна складова з захистом від переповнення (Anti-Windup) */
    pid->integral_accum += error;
    int32_t i_term = (pid->ki * pid->integral_accum) >> 8;

    /* Динамічне обмеження інтегратора */
    if (i_term > pid->out_max) {
        i_term = pid->out_max;
        pid->integral_accum = (pid->out_max << 8) / (pid->ki > 0 ? pid->ki : 1);
    } else if (i_term < pid->out_min) {
        i_term = pid->out_min;
        pid->integral_accum = (pid->out_min << 8) / (pid->ki > 0 ? pid->ki : 1);
    }

    /* Диференційна складова */
    int32_t derivative = error - pid->prev_error;
    int32_t d_term = (pid->kd * derivative) >> 8;
    pid->prev_error = error;

    /* Сумарний керуючий сигнал */
    int32_t output = p_term + i_term + d_term;
    if (output > pid->out_max) output = pid->out_max;
    if (output < pid->out_min) output = pid->out_min;

    return output;
}

/* Повний наскрізний конвеєр обробки сигналу */
uint16_t process_signal_pipeline(uint16_t raw_adc, uint16_t target_mv,
                                 EmaFilter *filter, PidController *pid) {
    /* 1. Масштабування відліку АЦП у мілівольти */
    uint32_t mv_unfiltered = ((uint32_t)raw_adc * ADC_VREF_MV) / ADC_MAX_CODE;

    /* 2. Цифрова фільтрація високочастотних завад */
    int32_t mv_filtered = ema_filter_update(filter, (int32_t)mv_unfiltered);

    /* 3. Обчислення керуючого сигналу ПІД-регулятором */
    int32_t control_out = pid_update(pid, (int32_t)target_mv, mv_filtered);

    /* 4. Приведення до діапазону регістра порівняння ШІМ (0..65535) */
    if (control_out < 0) control_out = 0;
    if (control_out > (int32_t)PWM_MAX_DUTY) control_out = PWM_MAX_DUTY;

    return (uint16_t)control_out;
}
