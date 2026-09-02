#ifndef BUMPLESS_PID_H
#define BUMPLESS_PID_H

#include <stdbool.h>
#include <stddef.h>

/*
 * ПІД-регулятор із безривковою передачею повноважень.
 *
 * Три кроки переходу з тексту реалізовані в bumpless_pid_handover():
 *   1) уставка прив'язується до поточного виміру  -> P(0+) = 0;
 *   2) пам'ять диференціатора прирівнюється факту -> D(0+) = 0;
 *   3) інтегратор передзавантажується різницею    -> I(0+) = u_prev - P - D - FF.
 *
 * Модуль не виділяє пам'яті й не має циклів зі змінною кількістю ітерацій:
 * час виконання сталий, його можна класти в переривання контуру керування.
 */

/* Прапорці телеметрії: чому саме регулятор не гарантує безривковості. */
#define PID_FAULT_NONE             0u
#define PID_FAULT_BAD_MEASUREMENT  (1u << 0) /* NaN/Inf з давача або з приводу */
#define PID_FAULT_BAD_DT           (1u << 1) /* dt <= 0, NaN або проґавлений такт */
#define PID_FAULT_PRELOAD_CLAMPED  (1u << 2) /* передзавантаження зрізане межею */
#define PID_FAULT_NOT_READY        (1u << 3) /* update() до handover() */
#define PID_FAULT_OUTPUT_SATURATED (1u << 4) /* вихід стоїть на упорі приводу */

/* Пауза, довша за цю, — це вже не джитер планувальника, а втрачений такт.
   Проінтегрувати таку «площу» помилки означає видати приводу сходинку. */
#define PID_DT_MAX 0.20f

typedef struct {
    float kp;                 /* пропорційний коефіцієнт [од. приводу / од. виміру] */
    float ki;                 /* інтегральний коефіцієнт [1/(од·с)] */
    float kd;                 /* коефіцієнт демпфування [с/од] */
    float kff;                /* пряме прогнозне керування від уставки */
    float out_min;            /* фізичні межі ходу приводу */
    float out_max;
    float i_min;              /* межі інтегратора (анти-віндап затиском) */
    float i_max;
    float slew_rate_max;      /* темп зміни уставки [од/с], 0 = без ремпінгу */
    float d_lpf_tau;          /* стала часу фільтра похідної [с], 0 = без фільтра */
    float max_expected_noise; /* розмах шуму виміру [од] — резерв для P при передзавантаженні */
} pid_config_t;

typedef struct {
    pid_config_t cfg;
    float integral;
    float prev_measurement;  /* пам'ять диференціатора: рахуємо похідну ВИМІРУ */
    float deriv_filt;        /* згладжена похідна */
    float target_setpoint;   /* кінцева ціль місії */
    float current_setpoint;  /* уставка після ремпінгу — саме її бачить контур */
    float last_output;
    bool  is_initialized;
    unsigned faults;
} bumpless_pid_t;

void bumpless_pid_init(bumpless_pid_t *pid, const pid_config_t *cfg);

/* Повне скидання стану. Конфігурацію не чіпає. */
void bumpless_pid_reset(bumpless_pid_t *pid);

/* Наївний старт «з чистого аркуша»: I = 0, уставка з місії, порожня пам'ять
   диференціатора. Лишено навмисно — на ньому демонструють удар інтегратора. */
void bumpless_pid_start_naive(bumpless_pid_t *pid, float setpoint);

/* Безривкове захоплення: уставка сідає на поточний вимір (P = 0). */
void bumpless_pid_handover(bumpless_pid_t *pid, float current_measurement,
                           float target_setpoint, float prev_actuator_output);

/* Узагальнений випадок: оператор вимагає тримати конкретну точку, тому
   P(0+) != 0 і його теж треба відняти від передзавантаження. */
void bumpless_pid_handover_hold(bumpless_pid_t *pid, float current_measurement,
                                float hold_setpoint, float target_setpoint,
                                float prev_actuator_output);

float bumpless_pid_update(bumpless_pid_t *pid, float measurement, float dt);

/* Межі інтегратора із запасом на пропорційне реагування:
   I_max_safe = out_max - kp * max_expected_noise (і симетрично знизу). */
void bumpless_pid_safe_i_limits(const pid_config_t *cfg,
                                float *i_min_safe, float *i_max_safe);

/* Розшифровка прапорців у рядок телеметрії; cap мусить бути > 0. */
void pid_fault_names(unsigned faults, char *out, size_t cap);

static inline void bumpless_pid_set_target(bumpless_pid_t *pid, float target)
{
    pid->target_setpoint = target;
}

static inline float bumpless_pid_last_output(const bumpless_pid_t *pid) { return pid->last_output; }
static inline float bumpless_pid_integral(const bumpless_pid_t *pid) { return pid->integral; }
static inline float bumpless_pid_setpoint(const bumpless_pid_t *pid) { return pid->current_setpoint; }
static inline bool bumpless_pid_ready(const bumpless_pid_t *pid) { return pid->is_initialized; }
static inline unsigned bumpless_pid_faults(const bumpless_pid_t *pid) { return pid->faults; }
static inline void bumpless_pid_clear_faults(bumpless_pid_t *pid) { pid->faults = PID_FAULT_NONE; }

#endif /* BUMPLESS_PID_H */
