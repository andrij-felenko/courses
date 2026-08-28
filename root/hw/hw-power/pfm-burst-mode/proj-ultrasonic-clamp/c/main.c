#include <stdint.h>
#include <stdbool.h>

#define FREQ_CLAMP_MIN_HZ       26300U                      /* Мінімальна частота затиску */
#define CLAMP_TIMEOUT_US        (1000000U / FREQ_CLAMP_MIN_HZ) /* 38 мкс */
#define INFRASONIC_TIMEOUT_US   50000U                      /* 50 мс (поріг 20 Гц) */
#define CURRENT_PWM_THRESH_UA   50000U                      /* 50 мА - поріг переходу в ШІМ */
#define CURRENT_SLEEP_THRESH_UA 20U                         /* 20 мкА - поріг глибокого сну */
#define V_OVP_OFFSET_MV         120U                        /* Поріг захисту від перенапруги */

typedef enum {
    MODE_PWM_CONTINUOUS,
    MODE_BURST_ULTRASONIC,
    MODE_BURST_DEEP_SLEEP
} power_mode_t;

typedef struct {
    uint32_t v_target_mv;
    uint32_t v_hysteresis_mv;
    uint32_t peak_current_limit_ma;
    uint32_t sleep_timer_us;
    power_mode_t current_mode;
    uint32_t pulses_to_fire;
    bool gate_driver_active;
    bool ovp_alert;
} power_supervisor_t;

void power_supervisor_init(power_supervisor_t *ctx, uint32_t v_target_mv) {
    ctx->v_target_mv = v_target_mv;
    ctx->v_hysteresis_mv = 30; /* ±30 мВ навколо номіналу */
    ctx->peak_current_limit_ma = 400;
    ctx->sleep_timer_us = 0;
    ctx->current_mode = MODE_PWM_CONTINUOUS;
    ctx->pulses_to_fire = 0;
    ctx->gate_driver_active = true;
    ctx->ovp_alert = false;
}

void power_supervisor_update(power_supervisor_t *ctx, uint32_t v_out_mv, uint32_t i_load_ua, uint32_t dt_us) {
    uint32_t v_high = ctx->v_target_mv + ctx->v_hysteresis_mv;
    uint32_t v_low  = ctx->v_target_mv - ctx->v_hysteresis_mv;
    uint32_t v_ovp  = ctx->v_target_mv + V_OVP_OFFSET_MV;

    /* Захист від перенапруги при нульовому навантаженні з активним затиском */
    if (v_out_mv >= v_ovp) {
        ctx->gate_driver_active = false;
        ctx->pulses_to_fire = 0;
        ctx->ovp_alert = true;
        ctx->sleep_timer_us = 0;
        return;
    }
    ctx->ovp_alert = false;

    /* Визначення глобального режиму за струмом навантаження */
    if (i_load_ua > CURRENT_PWM_THRESH_UA) {
        ctx->current_mode = MODE_PWM_CONTINUOUS;
        ctx->gate_driver_active = true;
        ctx->pulses_to_fire = 1;
        ctx->peak_current_limit_ma = 1200;
        ctx->sleep_timer_us = 0;
        return;
    }

    if (i_load_ua < CURRENT_SLEEP_THRESH_UA) {
        ctx->current_mode = MODE_BURST_DEEP_SLEEP;
    } else {
        ctx->current_mode = MODE_BURST_ULTRASONIC;
    }

    /* Логіка гістерезисного автомата станів */
    if (v_out_mv >= v_high) {
        /* Досягнуто верхнього порогу: відключаємо драйвери та нарощуємо таймер сну */
        ctx->gate_driver_active = false;
        ctx->pulses_to_fire = 0;
        ctx->sleep_timer_us += dt_us;

        /* Перевірка умови ультразвукового затиску */
        if (ctx->current_mode == MODE_BURST_ULTRASONIC && ctx->sleep_timer_us >= CLAMP_TIMEOUT_US) {
            ctx->gate_driver_active = true;
            ctx->pulses_to_fire = 1;              /* Поодинокий імпульс затиску */
            ctx->peak_current_limit_ma = 180;     /* Знижений струм для захисту від сплеску */
            ctx->sleep_timer_us = 0;
        }
    } else if (v_out_mv <= v_low) {
        /* Напруга впала нижче порогу: видаємо повноцінну пачку підзарядки */
        ctx->gate_driver_active = true;
        ctx->pulses_to_fire = (ctx->current_mode == MODE_BURST_DEEP_SLEEP) ? 10 : 4;
        ctx->peak_current_limit_ma = 450;
        ctx->sleep_timer_us = 0;
    } else {
        /* Поточна напруга всередині вікна між V_low та V_high */
        if (!ctx->gate_driver_active) {
            ctx->sleep_timer_us += dt_us;
            if (ctx->current_mode == MODE_BURST_ULTRASONIC && ctx->sleep_timer_us >= CLAMP_TIMEOUT_US) {
                ctx->gate_driver_active = true;
                ctx->pulses_to_fire = 1;
                ctx->peak_current_limit_ma = 180;
                ctx->sleep_timer_us = 0;
            }
        }
    }
}
