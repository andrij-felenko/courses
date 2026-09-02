/*
 * Безривковий ПІД-регулятор для вбудованих систем реального часу.
 *
 * Модуль не виділяє пам'яті, не блокується і не має циклів зі змінною
 * кількістю ітерацій: час виконання кожної функції сталий.
 */
#ifndef BUMPLESS_PID_H
#define BUMPLESS_PID_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Конфігураційні коефіцієнти контуру.
 *
 * Структура лише читається, тож її кладуть у Flash/ROM (`static const`)
 * і однією копією обслуговують кілька осей польотного контролера:
 * у стані регулятора лежить ВКАЗІВНИК на неї, а не копія.
 */
typedef struct {
    float kp;             /* Пропорційний коефіцієнт [од. приводу / од. виміру] */
    float ki;             /* Інтегральний коефіцієнт [од. приводу / (од. виміру·с)] */
    float kd;             /* Диференційний коефіцієнт демпфування [од. приводу·с / од. виміру] */
    float kff;            /* Коефіцієнт прямого модельного зв'язку (Feedforward) */
    float out_min;        /* Нижня фізична межа виходу приводу (наприклад, -1.0 або 0.0) */
    float out_max;        /* Верхня фізична межа виходу приводу (наприклад, +1.0 або 100.0) */
    float i_min;          /* Нижня межа інтегратора для анти-віндапу */
    float i_max;          /* Верхня межа інтегратора для анти-віндапу */
    float slew_rate_max;  /* Максимальна швидкість зміни уставки [од/с], 0 = миттєво */
} pid_config_t;

/*
 * Прапорці останнього такту. Уміщені в один байт, тож не коштують
 * жодного зайвого слова в структурі стану.
 */
#define PID_FLAG_SATURATED    0x01u  /* вихід уперся в out_min/out_max */
#define PID_FLAG_I_CLAMPED    0x02u  /* інтегратор уперся в i_min/i_max */
#define PID_FLAG_I_HELD       0x04u  /* інтегрування зупинено анти-віндапом */
#define PID_FLAG_SENSOR_FAULT 0x08u  /* вимір не є скінченним числом */
#define PID_FLAG_DT_INVALID   0x10u  /* dt <= 0 або не скінченне */
#define PID_FLAG_SLEWING      0x20u  /* уставка обмежена темпом наростання */
#define PID_FLAG_FRESH        0x40u  /* службовий: такт одразу після handover */

/*
 * Знімок внутрішніх доданків за такт — для телеметрії й налагодження.
 * Заповнюється лише тоді, коли виклик його попросив; сам регулятор
 * цієї структури не зберігає.
 */
typedef struct {
    float setpoint;     /* уставка, з якою рахували цей такт */
    float measurement;  /* вимір, який прийняли */
    float error;        /* setpoint − measurement */
    float p_term;
    float i_term;
    float d_term;
    float ff_term;
    float output;       /* остаточний обмежений сигнал керування */
    uint8_t flags;      /* набір PID_FLAG_* */
} pid_trace_t;

/*
 * Динамічний стан одного контуру: 28 байтів на 32-бітному ядрі
 * (вказівник 4 + п'ять float 20 + прапорець 1 + байт станів 1 + 2 вирівнювання).
 * Поля відкриті для інспектора телеметрії, але писати в них ззовні
 * дозволено лише через `bumpless_pid_set_target`.
 */
typedef struct {
    const pid_config_t *cfg; /* спільна конфігурація у Flash */
    float integral;          /* Накопичений інтеграл в одиницях приводу */
    float prev_measurement;  /* Попереднє значення виміру для D-складової */
    float target_setpoint;   /* Цільова уставка від планувальника місії */
    float current_setpoint;  /* Поточна згладжена уставка після Slew Limiter */
    float last_output;       /* Останній сформований сигнал керування */
    bool  is_initialized;    /* Прапорець готовності регулятора до роботи */
    uint8_t flags;           /* Прапорці останнього такту, PID_FLAG_* */
} bumpless_pid_t;

/* Чи придатна конфігурація: межі не перевернуті, коефіцієнти скінченні. */
bool bumpless_pid_config_valid(const pid_config_t *cfg);

/*
 * Скидає внутрішній стан у безпечні початкові значення й приймає
 * конфігураційні коефіцієнти. Непридатна конфігурація лишає регулятор
 * неініціалізованим — тоді `bumpless_pid_update` завжди віддає 0.
 */
void bumpless_pid_init(bumpless_pid_t *pid, const pid_config_t *cfg);

/*
 * Безривкова передача повноважень. Викликається одноразово в момент
 * зміни активного режиму, тим самим свіжим відліком, що піде в update.
 */
void bumpless_pid_handover(bumpless_pid_t *pid,
                          float current_measurement,
                          float target_setpoint,
                          float prev_actuator_output);

/* Один крок замкненого контуру. */
float bumpless_pid_update(bumpless_pid_t *pid, float measurement, float dt);

/* Те саме, але з викладенням доданків у знімок телеметрії (trace може бути NULL). */
float bumpless_pid_update_traced(bumpless_pid_t *pid,
                                 float measurement,
                                 float dt,
                                 pid_trace_t *trace);

/* Зміна цільової уставки на льоту; до неї веде обмежувач швидкості. */
static inline void bumpless_pid_set_target(bumpless_pid_t *pid, float target) {
    pid->target_setpoint = target;
}

static inline float bumpless_pid_output(const bumpless_pid_t *pid) {
    return pid->last_output;
}

static inline uint8_t bumpless_pid_flags(const bumpless_pid_t *pid) {
    return (uint8_t)(pid->flags & (uint8_t)~PID_FLAG_FRESH);
}

#ifdef __cplusplus
}
#endif

#endif /* BUMPLESS_PID_H */
