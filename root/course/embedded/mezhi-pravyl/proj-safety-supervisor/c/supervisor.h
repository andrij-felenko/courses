#ifndef SAFETY_SUPERVISOR_H
#define SAFETY_SUPERVISOR_H

#include <stdint.h>
#include <stdbool.h>
#include "blackbox.h"

/* Фізичні інваріанти апарата. Це не налаштування, а межі заліза:
 * міняються разом із машиною, а не з місією. */
#define SAFETY_MARGIN_M        0.35f   /* геометричний буфер до перешкоди, м */
#define MAX_BRAKE_ACCEL_MPS2   3.0f    /* що реально дають гальма, м/с² */
#define MAX_ACCEL_MPS2         1.5f    /* стеля розгону при повній батареї, м/с² */
#define LATENCY_PAD_SEC        0.04f   /* транспортна затримка тракту: давач + утримання + ESC */
#define MAX_ALLOWED_SPEED_MPS  2.5f    /* стеля лінійної швидкості, м/с */
#define MAX_YAW_RATE_RADPS     1.8f    /* стеля рискання, рад/с */
#define CRITICAL_VOLTAGE_V     13.8f   /* нижче — ризик апаратного скидання МК */
#define NOMINAL_VOLTAGE_V      16.0f   /* повна батарея, В */
#define WATCHDOG_MAX_TICKS     20u     /* 20 тактів по 5 мс = 100 мс глухоти планувальника */
#define SENSOR_HOLD_MAX_SEC    0.050f  /* скільки терпимо числення замість виміру */
#define TILT_WARN_FRACTION     0.8f    /* із якої частки критичного крену починаємо тиснути */

/* Команда керування: те, що планувальник просить, і те, що фільтр віддає мікшеру. */
typedef struct {
    float vx;       /* лінійна швидкість уперед, м/с */
    float vy;       /* бічна швидкість, м/с (для ровера завжди 0) */
    float yaw_rate; /* кутова швидкість рискання, рад/с */
} CommandVector;

/* Знімок давачів на поточний такт швидкого циклу. */
typedef struct {
    float obstacle_dist_m;     /* найменша відстань за променем руху, м */
    bool  obstacle_dist_valid; /* прапорець справності далекоміра (шина, CRC, діапазон) */
    float battery_voltage;     /* напруга силової шини, В */
    float current_tilt_rad;    /* поточне відхилення платформи від вертикалі, рад */
    float max_tilt_limit;      /* критичний кут перекидання, рад */
    bool  emergency_switch;    /* апаратна кнопка аварійної зупинки */
} SensorEnvelope;

typedef enum {
    SAFETY_PASS_THROUGH  = 0, /* команда планувальника пройшла без змін */
    SAFETY_CLAMPED       = 1, /* команду спроєктовано на допустиму область */
    SAFETY_BRAKE_ENGAGED = 2, /* керує сам супервізор: детерміноване сповільнення */
    SAFETY_ESTOP_ACTIVE  = 3  /* повний нуль на приводи */
} SafetyStatus;

typedef struct {
    uint32_t      current_tick;    /* такти швидкого циклу */
    uint32_t      last_plan_tick;  /* коли востаннє приїхала придатна уставка */
    CommandVector candidate;       /* остання достовірна уставка (утримується між пакетами) */
    float         last_out_vx;     /* що віддали приводам минулого такту */
    float         dr_dist_m;       /* оцінка дистанції за інерціальним численням, м */
    float         dr_elapsed_s;    /* скільки триває невизначеність далекоміра, с */
    bool          dist_trusted;    /* остання дистанція — вимір, а не числення */
    float         uptime_s;        /* час від старту, с (для міток чорної скриньки) */
    BlackBox      log;             /* чорна скринька спрацьовувань */
} SafetySupervisor;

void safety_init(SafetySupervisor *s);

/* Виклик із повільного потоку: планувальник приніс нову уставку.
 * Повертає false, якщо пакет непридатний, — тоді позначка свіжості НЕ оновлюється
 * і сторож рано чи пізно забере керування. */
bool safety_submit_plan(SafetySupervisor *s, const CommandVector *cmd);

/* Один такт швидкого циклу: O(1), без динамічної памʼяті, без блокувань. */
SafetyStatus safety_step(SafetySupervisor *s, const SensorEnvelope *sensors,
                         float dt_sec, CommandVector *out_safe_cmd);

#endif /* SAFETY_SUPERVISOR_H */
