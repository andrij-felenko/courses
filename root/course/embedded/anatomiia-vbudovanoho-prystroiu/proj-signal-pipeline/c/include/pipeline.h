#ifndef PIPELINE_H
#define PIPELINE_H

#include <stdbool.h>
#include <stdint.h>

/* Параметри тракту: 12-бітний АЦП, опора 3300 мВ, 16-бітний регістр
   порівняння ШІМ. Жодного float у всьому файлі — ядро Cortex-M0+ без FPU. */
#define ADC_MAX_CODE 4095
#define ADC_VREF_MV  3300
#define PWM_MAX_DUTY 65535

/* Коефіцієнти регулятора у форматі Q8.8: ціле = коефіцієнт * 256.
   Q8_LIMIT — стеля, з якої порахований бюджет цілочисельного множення. */
#define Q8_ONE   256
#define Q8_LIMIT 32767

/* ---- Експоненційний фільтр (EMA) ------------------------------------- */

typedef struct {
    int32_t value;    /* поточне згладжене значення, мВ */
    uint8_t shift_k;  /* alpha = 1 / 2^shift_k */
    bool    primed;   /* чи прийнято перший відлік */
} ema_filter_t;

/* shift_k поза межами 1..12 відкидається: нуль знерухомив би фільтр,
   а завеликий зсув перетворив би різницю на нуль і фільтр застряг би. */
bool    ema_init(ema_filter_t *f, uint8_t shift_k);
int32_t ema_update(ema_filter_t *f, int32_t sample);

/* ---- ПІД-регулятор із фіксованою комою -------------------------------- */

typedef struct {
    int32_t kp_q8;
    int32_t ki_q8;
    int32_t kd_q8;
    int32_t out_min;
    int32_t out_max;
} pid_cfg_t;

typedef struct {
    pid_cfg_t cfg;
    int32_t   integral;        /* сума помилок, Q0 */
    int32_t   integral_limit;  /* межа суми: рахується один раз при налаштуванні */
    int32_t   prev_error;
    bool      have_prev;       /* на першому кроці диференційної складової немає */
} pid_t;

bool    pid_init(pid_t *p, const pid_cfg_t *cfg);
void    pid_reset(pid_t *p);
int32_t pid_update(pid_t *p, int32_t setpoint, int32_t measured);

/* ---- Наскрізний конвеєр ----------------------------------------------- */

typedef struct {
    ema_filter_t filter;
    pid_t        pid;
    int32_t      last_mv;    /* останнє відфільтроване значення, для діагностики */
    uint16_t     last_duty;  /* останнє записане значення шпаруватості */
} pipeline_t;

bool     pipeline_init(pipeline_t *pl, uint8_t shift_k, const pid_cfg_t *cfg);
uint16_t pipeline_step(pipeline_t *pl, uint16_t raw_adc, uint16_t target_mv);

/* Код АЦП у мілівольти; код понад 4095 (збій DMA, чужий запис) обрізається. */
int32_t adc_code_to_mv(uint16_t raw_adc);

#endif /* PIPELINE_H */
