#include <stdint.h>
#include <stdbool.h>

#define LOOP_FREQUENCY_HZ     20000.0f
#define LOOP_DT_SECONDS       (1.0f / LOOP_FREQUENCY_HZ)
#define TELEMETRY_QUEUE_MASK  (64 - 1)

/* Параметри конфігурації та стан дискретного ПІД-регулятора */
typedef struct {
    /* Коефіцієнти регулятора */
    float kp;
    float ki;
    float kd;
    float d_filter_time_const; /* Постійна часу фільтра D-складової (Tf) */

    /* Межі насичення виходу */
    float out_min;
    float out_max;

    /* Внутрішній стан (змінні накопичувачів) */
    float integrator;
    float prev_measured;
    float d_filtered;
} FastPidController;

/* Зріз телеметрії для передачі у фоновий потік */
typedef struct {
    float target;
    float measured;
    float duty_cycle;
    uint32_t timestamp_ticks;
} ControlTelemetry;

/* Безблокувальна SPSC-черга (Single-Producer Single-Consumer) */
typedef struct {
    ControlTelemetry ring[64];
    volatile uint32_t head;
    volatile uint32_t tail;
} FastSpscQueue;

static FastPidController g_current_pid;
static FastSpscQueue g_telemetry_stream;

/* Ініціалізація параметрів контуру */
void fast_pid_init(FastPidController *pid, float kp, float ki, float kd, float tf, float out_min, float out_max) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->d_filter_time_const = tf;
    pid->out_min = out_min;
    pid->out_max = out_max;
    pid->integrator = 0.0f;
    pid->prev_measured = 0.0f;
    pid->d_filtered = 0.0f;
}

/* Швидкий обчислювальний крок за фіксований апаратний dt */
float fast_pid_compute(FastPidController *pid, float setpoint, float measured, float dt) {
    float error = setpoint - measured;

    /* 1. Пропорційний член */
    float p_term = pid->kp * error;

    /* 2. Диференціювання від виміряного значення з ФНЧ (Derivative on Measurement) */
    float d_raw = (measured - pid->prev_measured) / dt;
    pid->prev_measured = measured;

    float alpha = dt / (pid->d_filter_time_const + dt);
    pid->d_filtered += alpha * (d_raw - pid->d_filtered);
    float d_term = -pid->kd * pid->d_filtered;

    /* 3. Сумарний ненасичений вихід */
    float raw_output = p_term + pid->integrator + d_term;

    /* 4. Обмеження насичення вихідного сигналу */
    float clamped_output = raw_output;
    if (clamped_output > pid->out_max) {
        clamped_output = pid->out_max;
    } else if (clamped_output < pid->out_min) {
        clamped_output = pid->out_min;
    }

    /* 5. Умовне інтегрування (Clamping Anti-Windup) */
    bool is_clamped = (raw_output != clamped_output);
    bool error_deepens_saturation = ((error > 0.0f && raw_output > pid->out_max) ||
                                     (error < 0.0f && raw_output < pid->out_min));

    if (!is_clamped || !error_deepens_saturation) {
        pid->integrator += pid->ki * error * dt;
    }

    return clamped_output;
}

/* Неблокуючий запис телеметрії з ISR у чергу */
static inline void queue_push_from_isr(FastSpscQueue *q, const ControlTelemetry *telem) {
    uint32_t current_head = q->head;
    uint32_t next_head = (current_head + 1) & TELEMETRY_QUEUE_MASK;
    if (next_head != q->tail) {
        q->ring[current_head] = *telem;
        __sync_synchronize();
        q->head = next_head;
    }
}

/* Обробник апаратного переривання АЦП найвищого пріоритету (Zero Jitter ISR) */
void HardRealTime_ADC_ISR(void) {
    /* Апаратні адреси регістрів периферії STM32 */
    volatile uint32_t *const tim1_ccr1 = (volatile uint32_t *)(0x40012C34);
    volatile uint32_t *const tim1_arr  = (volatile uint32_t *)(0x40012C2C);
    volatile uint32_t *const tim1_cnt  = (volatile uint32_t *)(0x40012C24);
    volatile uint32_t *const adc1_sr   = (volatile uint32_t *)(0x40012000);
    volatile uint32_t *const adc1_dr   = (volatile uint32_t *)(0x4001204C);

    /* 1. Скидання апаратного прапорця переривання EOC */
    *adc1_sr &= ~0x02;

    /* 2. Зчитування результату синхронної вибірки струму */
    uint16_t adc_raw = (uint16_t)(*adc1_dr & 0x0FFF);
    float current_measured = ((float)adc_raw - 2048.0f) * (3.3f / 4096.0f) * 10.0f; /* 10 А/В */
    float current_target = 3.0f; /* 3 Ампери */

    /* 3. Прецизійний розрахунок регулятора (час виконання ≈ 1.6 мкс) */
    float duty = fast_pid_compute(&g_current_pid, current_target, current_measured, LOOP_DT_SECONDS);

    /* 4. Оновлення тіньового регістра ШІМ з автоматичним захистом діапазону */
    uint32_t arr_val = *tim1_arr;
    uint32_t compare_val = (uint32_t)(duty * (float)arr_val);
    if (compare_val > arr_val) compare_val = arr_val;
    *tim1_ccr1 = compare_val;

    /* 5. Відправка телеметрії без очікування */
    ControlTelemetry log_sample = {
        .target = current_target,
        .measured = current_measured,
        .duty_cycle = duty,
        .timestamp_ticks = *tim1_cnt
    };
    queue_push_from_isr(&g_telemetry_stream, &log_sample);
}
