// Диспетчер станів універсального зарядного контролера
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    MODE_LEAD_ACID_IUOU,
    MODE_NIMH_FAST
} charge_mode_t;

typedef enum {
    STATE_IDLE,
    STATE_BULK_OR_FAST_CC,
    STATE_ABSORPTION_OR_TOPOFF,
    STATE_FLOAT_OR_TRICKLE,
    STATE_EMERGENCY_STOP
} fsm_state_t;

typedef struct {
    charge_mode_t mode;
    fsm_state_t   state;
    uint32_t      timer_sec;
    uint16_t      v_target_mv;
    uint16_t      i_target_ma;
    uint16_t      v_peak_mv;
} charger_core_t;

// Обробка кванта часу 1 секунда
void charger_process_1s(charger_core_t *fsm, uint16_t v_mv, uint16_t i_ma, int16_t t_c, int16_t dt_mdeg_s) {
    fsm->timer_sec++;

    // Захист за абсолютною температурою для обох хімій
    if (t_c > 55) {
        fsm->state = STATE_EMERGENCY_STOP;
        fsm->v_target_mv = 0;
        fsm->i_target_ma = 0;
        return;
    }

    switch (fsm->state) {
        case STATE_IDLE:
            if (v_mv > 1000) { // Батарею під'єднано
                fsm->timer_sec = 0;
                fsm->state = STATE_BULK_OR_FAST_CC;
                fsm->v_peak_mv = v_mv;
            }
            break;

        case STATE_BULK_OR_FAST_CC:
            if (fsm->mode == MODE_LEAD_ACID_IUOU) {
                // Свинець: чекаємо досягнення V_abs (14.4 В за 25°C з термокомпенсацією -24 мВ/°C)
                int32_t v_abs = 14400 - 24 * (t_c - 25);
                fsm->v_target_mv = (uint16_t)v_abs;
                fsm->i_target_ma = 2000; // 0.2C для 10 А·год
                if (v_mv >= v_abs) {
                    fsm->state = STATE_ABSORPTION_OR_TOPOFF;
                    fsm->timer_sec = 0;
                }
            } else {
                // NiMH: шукаємо спад -dV >= 4 мВ або dT/dt >= 1.0 °C/хв (17 м°C/с)
                if (v_mv > fsm->v_peak_mv) fsm->v_peak_mv = v_mv;
                fsm->i_target_ma = 1500; // 0.75C для 2000 мА·год
                bool neg_dv = (fsm->v_peak_mv >= v_mv + 4);
                bool fast_t = (dt_mdeg_s >= 17 && fsm->timer_sec > 300);
                if (neg_dv || fast_t) {
                    fsm->state = STATE_ABSORPTION_OR_TOPOFF;
                    fsm->timer_sec = 0;
                }
            }
            break;

        case STATE_ABSORPTION_OR_TOPOFF:
            if (fsm->mode == MODE_LEAD_ACID_IUOU) {
                // Свинець: утримуємо V_abs, чекаємо спаду струму < C/50 або таймера 4 год
                if (i_ma < 200 || fsm->timer_sec > 4 * 3600) {
                    fsm->state = STATE_FLOAT_OR_TRICKLE;
                    fsm->timer_sec = 0;
                }
            } else {
                // NiMH: 30 хвилин дозаряду струмом 0.1C
                fsm->i_target_ma = 200;
                if (fsm->timer_sec >= 1800) {
                    fsm->state = STATE_FLOAT_OR_TRICKLE;
                    fsm->timer_sec = 0;
                }
            }
            break;

        case STATE_FLOAT_OR_TRICKLE:
            if (fsm->mode == MODE_LEAD_ACID_IUOU) {
                // Свинець: буферна напруга 13.6 В з термокомпенсацією
                fsm->v_target_mv = (uint16_t)(13600 - 24 * (t_c - 25));
                fsm->i_target_ma = 500;
            } else {
                // NiMH: безпечний краплинний струм C/35 (55 мА)
                fsm->v_target_mv = 0;
                fsm->i_target_ma = 55;
            }
            break;

        case STATE_EMERGENCY_STOP:
            fsm->v_target_mv = 0;
            fsm->i_target_ma = 0;
            break;
    }
}
