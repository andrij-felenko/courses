#include <stdint.h>
#include <stdbool.h>

#define LOOP_FREQ_HZ       20000.0f
#define LOOP_DT_S          (1.0f / LOOP_FREQ_HZ)
#define SPSC_QUEUE_SIZE    64

/* Регістри та апаратні структури периферії */
typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCMR2;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
    volatile uint32_t RCR;
    volatile uint32_t CCR1;
    volatile uint32_t CCR2;
    volatile uint32_t CCR3;
    volatile uint32_t CCR4;
    volatile uint32_t BDTR;
} HwTimerRegisters;

typedef struct {
    volatile uint32_t SR;
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMPR1;
    volatile uint32_t SMPR2;
    volatile uint32_t DR;
} HwAdcRegisters;

/* Конфігурація та стан ПІД-регулятора */
typedef struct {
    float kp;
    float ki;
    float kd;
    float tf_d;             /* Постійна часу фільтра низьких частот для D-складової */
    float out_min;
    float out_max;

    /* Внутрішній стан накопичувачів */
    float integrator;
    float prev_meas;
    float d_filtered;
} DeterministicPid;

typedef struct {
    float target;
    float measured;
    float output;
    uint32_t timestamp_us;
} TelemetryItem;

/* Кільцевий буфер SPSC (Single-Producer Single-Consumer) */
typedef struct {
    TelemetryItem buffer[SPSC_QUEUE_SIZE];
    volatile uint32_t head;
    volatile uint32_t tail;
} SpscQueue;

/* Глобальні статичні екземпляри */
static DeterministicPid g_current_pid;
static SpscQueue g_telemetry_queue;

static inline void spsc_init(SpscQueue *q) {
    q->head = 0;
    q->tail = 0;
}

static inline bool spsc_push(SpscQueue *q, const TelemetryItem *item) {
    uint32_t next_head = (q->head + 1) & (SPSC_QUEUE_SIZE - 1);
    if (next_head == q->tail) {
        return false; /* Буфер заповнений, викидаємо телеметрію без блокування */
    }
    q->buffer[q->head] = *item;
    __sync_synchronize(); /* Memory barrier */
    q->head = next_head;
    return true;
}

bool spsc_pop(SpscQueue *q, TelemetryItem *item) {
    if (q->head == q->tail) {
        return false; /* Черга порожня */
    }
    *item = q->buffer[q->tail];
    __sync_synchronize();
    q->tail = (q->tail + 1) & (SPSC_QUEUE_SIZE - 1);
    return true;
}

void pid_init(DeterministicPid *pid, float kp, float ki, float kd, float tf_d, float min_val, float max_val) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->tf_d = tf_d;
    pid->out_min = min_val;
    pid->out_max = max_val;
    pid->integrator = 0.0f;
    pid->prev_meas = 0.0f;
    pid->d_filtered = 0.0f;
}

/* Швидкий неблокуючий розрахунок ПІД за фіксований крок dt */
float pid_update(DeterministicPid *pid, float setpoint, float measured, float dt) {
    float error = setpoint - measured;

    /* 1. Пропорційна складова */
    float p_term = pid->kp * error;

    /* 2. Диференційна складова від вимірюваної величини з ФНЧ (Derivative on Measurement) */
    float d_meas = (measured - pid->prev_meas) / dt;
    pid->prev_meas = measured;

    /* Фільтр першого порядку: d_filtered = d_filtered + alpha * (d_meas - d_filtered) */
    float alpha = dt / (pid->tf_d + dt);
    pid->d_filtered += alpha * (d_meas - pid->d_filtered);
    float d_term = -pid->kd * pid->d_filtered;

    /* 3. Попередній ненасичений вихід для anti-windup */
    float unsaturated_out = p_term + pid->integrator + d_term;

    /* 4. Обмеження виходу (Saturation) */
    float output = unsaturated_out;
    if (output > pid->out_max) {
        output = pid->out_max;
    } else if (output < pid->out_min) {
        output = pid->out_min;
    }

    /* 5. Умовне інтегрування (Clamping Anti-Windup) */
    bool is_saturated = (unsaturated_out != output);
    bool same_direction = ((error > 0.0f && unsaturated_out > pid->out_max) ||
                           (error < 0.0f && unsaturated_out < pid->out_min));

    if (!is_saturated || !same_direction) {
        pid->integrator += pid->ki * error * dt;
    }

    return output;
}

/* Обробник апаратного переривання АЦП найвищого пріоритету (Zero Jitter) */
void ADC1_2_IRQHandler(void) {
    HwTimerRegisters *tim1 = (HwTimerRegisters *)0x40012C00;
    HwAdcRegisters   *adc1 = (HwAdcRegisters *)0x40012000;

    /* Очищення прапорця завершення перетворення (EOC) */
    adc1->SR &= ~0x02;

    /* Зчитування 12-бітного результату струму шунта */
    uint16_t raw_adc = (uint16_t)(adc1->DR & 0x0FFF);
    float current_amps = ((float)raw_adc - 2048.0f) * (3.3f / 4096.0f) * 10.0f; /* 10 А/В */

    /* Цільовий струм із глобальної уставки */
    float target_amps = 2.5f;

    /* Обчислення регулятора (час виконання ≈ 1.8 мкс на Cortex-M4F 168 МГц) */
    float duty_cycle = pid_update(&g_current_pid, target_amps, current_amps, LOOP_DT_S);

    /* Оновлення тіньового регістра порівняння таймера ШІМ (Shadow / Preload) */
    uint32_t arr = tim1->ARR;
    uint32_t ccr_val = (uint32_t)(duty_cycle * (float)arr);
    if (ccr_val > arr) ccr_val = arr;
    tim1->CCR1 = ccr_val;

    /* Відправка телеметрії в lock-free чергу */
    TelemetryItem telem = {
        .target = target_amps,
        .measured = current_amps,
        .output = duty_cycle,
        .timestamp_us = tim1->CNT
    };
    spsc_push(&g_telemetry_queue, &telem);
}
