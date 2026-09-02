#ifndef ARBITER_H
#define ARBITER_H

#include <stdbool.h>
#include <stdint.h>

/* Канали уставки. Roll/Pitch — кут нахилу в радіанах, Yaw — кутова швидкість
   (рад/с), Thrust — нормована тяга [0..1]. Повний хід ручки по кутових осях
   відповідає 1.0, тож мертва смуга 0.08 — це рівно 8% ходу. */
enum { AX_ROLL = 0, AX_PITCH, AX_YAW, AX_THRUST, AX_COUNT };

/* Джерела рішень у порядку спадання авторитету: індекс і є пріоритет. */
typedef enum {
    SRC_FAILSAFE = 0,   /* аварійний автомат: батарея, геофенс, відмова датчиків */
    SRC_RC_PILOT,       /* пульт радіокерування в руках оператора */
    SRC_OFFBOARD,       /* бортовий комп'ютер зору, уставки кожні 25 мс */
    SRC_GCS_MISSION,    /* наземна станція: точки маршруту через 4G */
    SRC_COUNT,
    SRC_NONE = 255
} source_id_t;

typedef enum {
    ARB_OK = 0,
    ARB_ERR_SOURCE,      /* невідомий слот */
    ARB_ERR_NOT_FINITE,  /* NaN/Inf у каналі — типова ознака аварії процесу зору */
    ARB_ERR_RANGE,       /* уставка поза фізичними межами апарата */
    ARB_ERR_STALE        /* кадр старіший за вже прийнятий (переставлення пакетів) */
} arb_status_t;

typedef struct {
    uint64_t stamp_us;      /* мітка часу відправника */
    float    ch[AX_COUNT];
} setpoint_t;

typedef struct {
    uint32_t timeout_us;            /* сторожовий таймер життєздатності джерела */
    float    stick_deadband;        /* поріг ВХОДУ в ручний пріоритет */
    float    stick_deadband_exit;   /* поріг ВИХОДУ, нижчий — гістерезис проти тремтіння */
    float    max_slew_rate[AX_COUNT]; /* межа |du/dt| на канал, одиниць за секунду */
} source_cfg_t;

typedef struct {
    setpoint_t   sp;             /* остання ПРИЙНЯТА уставка */
    uint64_t     heartbeat_us;   /* коли її прийняли (за годинником борту) */
    source_cfg_t cfg;
    bool         has_data;
    bool         timed_out;
} source_slot_t;

typedef struct {
    source_slot_t slots[SRC_COUNT];
    source_id_t   active;
    source_id_t   previous;
    setpoint_t    out;              /* згладжена уставка на виході арбітра */
    bool          out_valid;        /* false — керувати нічим, апарат на аварійному профілі */
    uint64_t      last_eval_us;
    bool          failsafe_latched; /* аварія засувається до явного скидання */
    bool          override_latched; /* засувка гістерезису мертвої смуги */
    float         deflection;       /* норма Чебишова по стіках — у чорну скриньку */
    uint32_t      switches;
    uint32_t      rejects;
} arbiter_t;

void         arbiter_init(arbiter_t *arb);
arb_status_t arbiter_submit(arbiter_t *arb, source_id_t src,
                            const setpoint_t *sp, uint64_t now_us);
void         arbiter_raise_failsafe(arbiter_t *arb, float descent_thrust, uint64_t now_us);
void         arbiter_clear_failsafe(arbiter_t *arb);

/* Один виклик на такт польотного циклу: сторожі, вибір джерела, лімітер. */
source_id_t  arbiter_evaluate(arbiter_t *arb, uint64_t now_us, setpoint_t *out);

bool        arbiter_output_valid(const arbiter_t *arb);
bool        arbiter_is_live(const arbiter_t *arb, source_id_t src);
float       arbiter_deflection(const arbiter_t *arb);
uint32_t    arbiter_switch_count(const arbiter_t *arb);
uint32_t    arbiter_reject_count(const arbiter_t *arb);
const char *source_name(source_id_t src);
const char *arb_status_name(arb_status_t st);

#endif /* ARBITER_H */
