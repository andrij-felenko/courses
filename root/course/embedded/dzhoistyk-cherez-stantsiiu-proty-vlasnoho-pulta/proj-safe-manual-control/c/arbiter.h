#ifndef ARBITER_H
#define ARBITER_H

#include <stdbool.h>
#include <stdint.h>

/* Арбітр ручного керування на борту.
 *
 * Чотири бар'єри зі статті:
 *   1) безумовний пріоритет фізичного пульта (перехоплення без згладжування);
 *   2) дворівнева шкала таймаутів 250 мс / 1000 мс;
 *   3) обмеження швидкості наростання осей;
 *   4) відлік таймауту ВИКЛЮЧНО за MANUAL_CONTROL (HEARTBEAT сюди не заходить —
 *      його приймає gcs_link.c і в арбітр не передає).
 *
 * Модуль без динамічної пам'яті: увесь стан у структурі, яку заводить виклик.
 */

enum {
    RC_DEADBAND_NORM     = 50,   /* 5% від діапазону [-1000..1000] */
    RC_THROTTLE_DEADBAND = 100,  /* газ зрушено з нуля більш ніж на 10% */
    RC_LINK_TIMEOUT_MS   = 100,  /* CRSF іде 50–500 Гц: 100 мс тиші — лінк мертвий */
    GCS_DEGRADE_MS       = 250,  /* м'яка нейтралізація осей */
    GCS_FAILSAFE_MS      = 1000, /* аварійна процедура */
    HOVER_THROTTLE       = 500   /* тяга «зависання» на час деградації */
};

/* Одиниць осі за секунду. Повний хід 2000 одиниць проходиться за 0.5 с —
 * саме цим платимо за захист механіки від пачки затриманих пакетів. */
#define AXIS_SLEW_PER_SEC 4000.0f

typedef struct {
    int16_t  roll;     /* [-1000..1000], позитивний — вправо */
    int16_t  pitch;    /* [-1000..1000], позитивний — вперед */
    int16_t  throttle; /* [0..1000] */
    int16_t  yaw;      /* [-1000..1000], позитивний — за годинниковою */
    uint16_t buttons;  /* бітова маска кнопок джойстика */
} control_axes_t;

typedef enum {
    ARB_DISARMED = 0,
    ARB_RC_ACTIVE,
    ARB_GCS_ACTIVE,
    ARB_GCS_DEGRADED,
    ARB_FAILSAFE
} arbiter_state_t;

typedef enum {
    FS_NONE = 0,
    FS_RTL,   /* є домашня точка і фікс — повертаємось */
    FS_LAND   /* без домашньої точки лишається лише посадка на місці */
} failsafe_action_t;

typedef enum {
    ARM_ACCEPTED = 0,
    ARM_NEED_CONFIRMATION, /* перший запит на арм завжди відхиляємо */
    ARM_DENIED_NO_LINK,    /* свіжого MANUAL_CONTROL немає */
    ARM_DENIED_STICKS,     /* стіки не в нейтралі */
    ARM_DENIED_FAILSAFE,   /* під час аварійної процедури арм заборонено */
    ARM_DISARMED           /* роззброєння приймаємо завжди й негайно */
} arm_result_t;

/* Внутрішній стан лімітера швидкості наростання: тримаємо у float, бо при
 * dt = 2.5 мс крок 10 одиниць, а цілочисельне округлення вниз на високих
 * частотах контуру просто зупиняло б рух осі. */
typedef struct {
    float roll, pitch, yaw, throttle;
} axes_f_t;

typedef struct {
    arbiter_state_t   state;
    failsafe_action_t failsafe;
    bool              armed;
    bool              home_valid; /* є фікс і записана домашня точка */

    control_axes_t out;      /* те, що піде в контур стабілізації */
    axes_f_t       out_f;    /* та сама точка, але з дробовою частиною */

    control_axes_t rc;       /* сирі осі фізичного пульта */
    control_axes_t gcs;      /* сирі осі MANUAL_CONTROL */
    uint32_t       rc_ms;    /* мітка часу останнього кадру пульта */
    uint32_t       gcs_ms;   /* мітка часу останнього MANUAL_CONTROL */
    bool           rc_seen;
    bool           gcs_seen;
    bool           rc_link_lost;

    uint32_t preempt_events;  /* скільки разів пульт перехоплював керування */
    uint32_t degrade_events;
    uint32_t failsafe_events;
} arbiter_t;

void arbiter_init(arbiter_t *a);
void arbiter_set_home_available(arbiter_t *a, bool ok);

/* Кадр від фізичного пульта (CRSF/ExpressLRS/S.BUS уже розібрано). */
void arbiter_feed_rc(arbiter_t *a, const control_axes_t *rc, uint32_t now_ms);

/* Осі з MAVLink MANUAL_CONTROL #69: x=тангаж, y=крен, z=тяга, r=рискання. */
void arbiter_feed_manual_control(arbiter_t *a, int16_t x, int16_t y, int16_t z,
                                 int16_t r, uint16_t buttons, uint32_t now_ms);

/* Арм/дизарм ЛИШЕ окремою командою, ніяких комбінацій стіків. */
arm_result_t arbiter_request_arm(arbiter_t *a, bool arm, bool confirmed, uint32_t now_ms);

/* Викликається з частоти контуру стабілізації (400 Гц), а не з приходу пакета. */
void arbiter_update(arbiter_t *a, uint32_t now_ms, float dt_sec);

const char *arbiter_state_name(arbiter_state_t s);
const char *arbiter_failsafe_name(failsafe_action_t f);
const char *arbiter_arm_result_name(arm_result_t r);

#endif /* ARBITER_H */
