/* calib_fsm.h — кінцевий автомат стендового прогону Compass-Mot.
 *
 * Автомат нічого не знає ні про конкретний ESC, ні про шину магнітометра:
 * усе залізо заходить крізь набір указівників на функції. Завдяки цьому
 * той самий автомат крутиться і на платі, і на столі в симуляції стенда.
 */
#ifndef CALIB_FSM_H
#define CALIB_FSM_H

#include "compass_mot.h"

typedef enum {
    CM_IDLE = 0,
    CM_BASELINE,    /* 2 с при зупинених моторах: знімаємо B_base   */
    CM_RAMP_UP,     /* сходинки газу по 10% з витримкою             */
    CM_PEAK_HOLD,   /* 1.5 с на 85%                                 */
    CM_RAMP_DOWN,   /* плавний скид: бережемо ключі від зворотної ЕРС */
    CM_SOLVE,       /* розв'язок OLS                                */
    CM_SAVE,        /* запис k у енергонезалежну пам'ять            */
    CM_DONE,
    CM_FAILED
} cm_state_t;

/* Контракт із залізом стенда. */
typedef struct {
    vec3_t (*read_field)(void *ctx);       /* мкТл                        */
    float  (*read_current)(void *ctx);     /* А з шунта Power Module      */
    void   (*set_throttle)(void *ctx, float pct);  /* 0..100              */
    bool   (*save_params)(void *ctx, vec3_t k);    /* EEPROM/FRAM         */
    void   *ctx;
} cm_io_t;

typedef struct {
    cm_state_t        state;
    cm_io_t           io;

    uint32_t          t_state_ms;   /* коли зайшли в поточний стан   */
    uint32_t          t_step_ms;    /* коли зайшли на поточну сходинку */
    float             throttle_pct;

    double            base_sum[3];  /* накопичення B_base            */
    uint32_t          base_n;

    compass_mot_ols_t ols;
    compass_mot_fit_t fit;          /* дійсний лише в CM_DONE        */
    compass_mot_err_t err;
    const char       *fail_reason;  /* NULL, поки все гаразд         */
} cm_calib_t;

/* Готує автомат і одразу глушить газ. Прогін починається з першого step(). */
void cm_calib_start(cm_calib_t *c, const cm_io_t *io, uint32_t now_ms);

/* Один такт автомата; викликати з періодом польотного циклу (10 мс).
 * Повертає стан ПІСЛЯ такту. Термінальні стани — CM_DONE і CM_FAILED. */
cm_state_t cm_calib_step(cm_calib_t *c, uint32_t now_ms);

/* Аварійна зупинка ззовні (кнопка, зникнення зв'язку, пропелер зірвало). */
void cm_calib_abort(cm_calib_t *c, const char *reason);

const char *cm_state_name(cm_state_t st);

#endif /* CALIB_FSM_H */
