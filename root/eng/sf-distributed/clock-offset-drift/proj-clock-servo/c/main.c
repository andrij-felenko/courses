#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>

#define SUBNS_SHIFT         32
#define SUBNS_SCALE         (1ULL << SUBNS_SHIFT)

/* Параметри обмеження корекції */
#define MAX_SLEW_PPM        500.0       /* Максимальне підстроювання темпу (+-500 ppm) */
#define STEP_THRESHOLD_NS   100000000ULL /* 100 мс: понад це робимо разовий стрибок */
#define PPS_TIMEOUT_TICKS   2           /* Кількість пропущених секунд для переходу в Holdover */

typedef enum {
    SERVO_UNLOCKED = 0,
    SERVO_LOCKING  = 1,
    SERVO_LOCKED   = 2,
    SERVO_HOLDOVER = 3
} servo_state_t;

typedef struct {
    uint64_t sec;           /* Цілі секунди UTC/TAI */
    uint64_t nsec;          /* Цілі наносекунди (0..999999999) */
    uint32_t sub_nsec;      /* Дробова частина наносекунди (Q32) */
} clock_time_t;

typedef struct {
    /* Стан шкали часу */
    clock_time_t time;
    uint64_t last_hw_ticks;
    double nominal_tick_ns; /* Номінальна тривалість апаратного такту в нс */

    /* Параметри PI-регулятора */
    double kp;              /* Пропорційний коефіцієнт (1/с) */
    double ki;              /* Інтегральний коефіцієнт (1/с^2) */
    double integrated_drift_ppm; /* Оцінка постійного відхилення частоти кварцу (I-ланка) */
    double current_slew_ppm;     /* Поточна сумарна поправка швидкості ходу */

    /* Стан та діагностика */
    servo_state_t state;
    int64_t last_phase_error_ns;
    uint32_t consecutive_locked_secs;
    uint32_t missed_pps_count;
} clock_servo_t;

void clock_servo_init(clock_servo_t *cs, double nominal_freq_hz) {
    cs->time.sec = 0;
    cs->time.nsec = 0;
    cs->time.sub_nsec = 0;
    cs->last_hw_ticks = 0;
    cs->nominal_tick_ns = 1e9 / nominal_freq_hz;

    /* Оптимальні коефіцієнти: смуга ~0.05 Гц, демпфування zeta = 0.707 */
    cs->kp = 0.10;          /* Відпрацювання 10% фазового зсуву за секунду */
    cs->ki = 0.005;         /* Повільна інтеграція дрейфу частоти */
    cs->integrated_drift_ppm = 0.0;
    cs->current_slew_ppm = 0.0;

    cs->state = SERVO_UNLOCKED;
    cs->last_phase_error_ns = 0;
    cs->consecutive_locked_secs = 0;
    cs->missed_pps_count = 0;
}

/* Оновлення місцевого часу на основі пройдених апаратних тактів */
void clock_advance_ticks(clock_servo_t *cs, uint64_t current_hw_ticks) {
    uint64_t delta_ticks = current_hw_ticks - cs->last_hw_ticks;
    cs->last_hw_ticks = current_hw_ticks;

    /* Фактична швидкість з урахуванням корекції сервоконтролера */
    double rate_multiplier = 1.0 + (cs->current_slew_ppm * 1e-6);
    double elapsed_ns_exact = (double)delta_ticks * cs->nominal_tick_ns * rate_multiplier;

    uint64_t elapsed_ns_int = (uint64_t)elapsed_ns_exact;
    uint32_t elapsed_sub_ns = (uint32_t)((elapsed_ns_exact - (double)elapsed_ns_int) * SUBNS_SCALE);

    /* Додавання з урахуванням переносу розрядів */
    uint64_t total_sub = (uint64_t)cs->time.sub_nsec + elapsed_sub_ns;
    cs->time.sub_nsec = (uint32_t)(total_sub & (SUBNS_SCALE - 1));
    uint64_t carry_ns = total_sub >> SUBNS_SHIFT;

    uint64_t total_ns = cs->time.nsec + elapsed_ns_int + carry_ns;
    cs->time.sec += total_ns / 1000000000ULL;
    cs->time.nsec = total_ns % 1000000000ULL;
}

/* Обробка події PPS: вимірювання помилки фази та оновлення PI-сервоконтролера */
void clock_on_pps(clock_servo_t *cs, uint64_t pps_hw_ticks, uint64_t ref_sec) {
    /* 1. Доводимо час точно до моменту приходу фронту PPS */
    clock_advance_ticks(cs, pps_hw_ticks);
    cs->missed_pps_count = 0;

    /* 2. Обчислення похибки фази e_k = T_ref - T_local */
    int64_t sec_diff = (int64_t)ref_sec - (int64_t)cs->time.sec;
    int64_t error_ns = (sec_diff * 1000000000LL) - (int64_t)cs->time.nsec;
    cs->last_phase_error_ns = error_ns;

    /* 3. Грубий зсув (холодний старт або аварійний розрив) */
    if (llabs(error_ns) > (int64_t)STEP_THRESHOLD_NS) {
        cs->time.sec = ref_sec;
        cs->time.nsec = 0;
        cs->time.sub_nsec = 0;
        cs->integrated_drift_ppm = 0.0;
        cs->current_slew_ppm = 0.0;
        cs->state = SERVO_LOCKING;
        cs->consecutive_locked_secs = 0;
        return;
    }

    /* 4. PI-розрахунок керуючого впливу */
    double p_term = cs->kp * (double)error_ns * 1e-3; /* нс помилки -> ppm швидкості */
    cs->integrated_drift_ppm += cs->ki * (double)error_ns * 1e-3;

    /* Анти-віндап обмеження інтегратора */
    if (cs->integrated_drift_ppm > MAX_SLEW_PPM) cs->integrated_drift_ppm = MAX_SLEW_PPM;
    if (cs->integrated_drift_ppm < -MAX_SLEW_PPM) cs->integrated_drift_ppm = -MAX_SLEW_PPM;

    double total_slew = p_term + cs->integrated_drift_ppm;

    /* Насичення загального темпу slewing */
    if (total_slew > MAX_SLEW_PPM) total_slew = MAX_SLEW_PPM;
    if (total_slew < -MAX_SLEW_PPM) total_slew = -MAX_SLEW_PPM;
    cs->current_slew_ppm = total_slew;

    /* 5. Автомат станів захоплення */
    if (llabs(error_ns) < 100) { /* Фазова похибка менше 100 нс */
        cs->consecutive_locked_secs++;
        if (cs->consecutive_locked_secs >= 5) {
            cs->state = SERVO_LOCKED;
        }
    } else {
        cs->consecutive_locked_secs = 0;
        if (cs->state == SERVO_LOCKED) {
            cs->state = SERVO_LOCKING;
        }
    }
}

/* Обробка відсутності імпульсу PPS (викликається за тайм-аутом) */
void clock_on_pps_timeout(clock_servo_t *cs) {
    cs->missed_pps_count++;
    if (cs->missed_pps_count >= PPS_TIMEOUT_TICKS) {
        /* Перехід у режим Holdover: вимикаємо P-ланку, тримаємо вивчену I-ланку */
        cs->state = SERVO_HOLDOVER;
        cs->current_slew_ppm = cs->integrated_drift_ppm;
    }
}
