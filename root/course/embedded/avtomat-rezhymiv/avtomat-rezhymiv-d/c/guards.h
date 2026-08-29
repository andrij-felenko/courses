#ifndef FM_GUARDS_H
#define FM_GUARDS_H

#include <stddef.h>
#include <stdint.h>

#include "modes.h"
#include "params.h"
#include "telemetry.h"

/* Причина відмови. Один enum на всі відмови автомата — і охоронців, і заслінки
   газу, і арбітра аварій: наземна станція має бачити не «не вийшло», а точну
   причину, до того ж машинно розрізнювану. */
typedef enum {
    FM_ALLOW = 0,
    FM_DENY_INVALID_MODE,      /* коду режиму не існує                          */
    FM_DENY_IMU,               /* гіроскоп або акселерометр несправні            */
    FM_DENY_ATTITUDE,          /* оцінка кутів горизонту недостовірна            */
    FM_DENY_ALT_ESTIMATE,      /* немає вертикальної оцінки (баро/далекомір)     */
    FM_DENY_NO_GNSS_FIX,       /* немає 3D Fix або замало супутників             */
    FM_DENY_BAD_DOP,           /* геометрія сузірʼя гірша за поріг               */
    FM_DENY_EKF_INNOVATION,    /* інновації фільтра поза гейтом                  */
    FM_DENY_EKF_GLITCH,        /* інновації понад 1.0 — виміри суперечать одні одним */
    FM_DENY_COMPASS,           /* курс недостовірний                             */
    FM_DENY_GUARD_UNSTABLE,    /* умова щойно виконалася, витримки ще нема       */
    FM_DENY_NO_MISSION,        /* буфер плану порожній                           */
    FM_DENY_BAD_MISSION,       /* CRC, висоти або координати плану непридатні    */
    FM_DENY_NO_HOME,           /* точку старту не зафіксовано                    */
    FM_DENY_GUIDED_LINK,       /* джерело цілевказівок мовчить                   */
    FM_DENY_THROTTLE_MISMATCH, /* стік газу не зведено з авторегулятором         */
    FM_DENY_FAILSAFE_LOCK,     /* активний аварійний режим вищого пріоритету     */
    FM_DENY_IN_AIR             /* дію заборонено, поки апарат у повітрі          */
} fm_deny_t;

/* Охоронці — чисті функції: жодного запису в стан, жодного побічного ефекту.
   Це не стиль, а вимога атомарності: автомат мусить мати право викликати їх
   у будь-якому порядку й будь-скільки разів, зокрема й для перевірки «а чи
   можна повернутися нагору», не змінивши цим нічого. */
fm_deny_t fm_guard_imu(const fm_state_t *s);
fm_deny_t fm_guard_attitude(const fm_state_t *s);
fm_deny_t fm_guard_altitude(const fm_state_t *s, const fm_params_t *p);
fm_deny_t fm_guard_position(const fm_state_t *s, const fm_params_t *p);
fm_deny_t fm_guard_guided(const fm_state_t *s, const fm_params_t *p);
fm_deny_t fm_guard_auto(const fm_state_t *s, const fm_params_t *p);
fm_deny_t fm_guard_rtl(const fm_state_t *s, const fm_params_t *p);

/* Диспетчер: охоронець цільового режиму. Невідомий код режиму сюди теж
   приходить — і дістає відмову, а не гілку «нічого не робимо». */
fm_deny_t fm_guard_check(fm_mode_t target, const fm_state_t *s, const fm_params_t *p);

/* Текст для STATUSTEXT: «Mode change failed: <режим> <причина>». Пише не більше
   n байтів разом із нулем. */
void fm_deny_text(fm_mode_t target, fm_deny_t deny, char *buf, size_t n);

/* Код результату для COMMAND_ACK. Тимчасові перешкоди (витримка, заслінка газу,
   мовчазний супровідний компʼютер) — TEMPORARILY_REJECTED: станція має право
   повторити запит. Постійні — DENIED. */
uint8_t fm_deny_mav_result(fm_deny_t deny);

#endif /* FM_GUARDS_H */
