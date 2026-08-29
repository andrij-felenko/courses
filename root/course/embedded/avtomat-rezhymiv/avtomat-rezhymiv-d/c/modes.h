#ifndef FM_MODES_H
#define FM_MODES_H

#include <stdbool.h>

/* Польотні режими, впорядковані за зростанням автономності: рух угору списком
   підвищує вимоги до сенсорного стека, рух униз — знімає їх. Саме на цьому
   порядку тримається каскадна деградація. */
typedef enum {
    FM_MODE_MANUAL = 0,     /* Acro: стіки задають кутові швидкості             */
    FM_MODE_STABILIZE,      /* автогоризонт, тяга напряму зі стіка              */
    FM_MODE_ALT_HOLD,       /* + вертикальний регулятор положення               */
    FM_MODE_POS_HOLD,       /* + горизонтальні регулятори швидкості й координат */
    FM_MODE_GUIDED,         /* цілевказівки ззовні по MAVLink                   */
    FM_MODE_AUTO,           /* політ за завантаженим планом місії               */
    FM_MODE_RTL,            /* повернення до точки старту                       */
    FM_MODE_LAND,           /* контрольований вертикальний спуск                */
    FM_MODE_EMERGENCY_LAND, /* спуск без навігації, на самих кутах і баро       */
    FM_MODE_TERMINATE,      /* відсічка живлення двигунів                       */
    FM_MODE_COUNT
} fm_mode_t;

bool        fm_mode_valid(fm_mode_t mode);
const char *fm_mode_name(fm_mode_t mode);

/* Вимоги режиму до оцінювачів. */
bool fm_mode_needs_attitude(fm_mode_t mode);
bool fm_mode_needs_altitude(fm_mode_t mode);
bool fm_mode_needs_position(fm_mode_t mode);

/* Хто керує вертикальною тягою: автомат чи безпосередньо ручка газу. */
bool fm_mode_auto_throttle(fm_mode_t mode);
bool fm_mode_manual_throttle(fm_mode_t mode);

/* Режими, які пілот скасовує рухом стіків (пріоритет людини). */
bool fm_mode_is_autonomous(fm_mode_t mode);

/* Режими, що їх ставить арбітр аварій, а не оператор. */
bool fm_mode_is_failsafe(fm_mode_t mode);

/* Наступна сходинка вниз ієрархією: PosHold -> AltHold -> Stabilize -> Manual. */
fm_mode_t fm_mode_degrade(fm_mode_t mode);

/* Найвищий режим, який дозволяє поточний набір справних оцінювачів; потрібен
   і для деградації, і для перехоплення стіками (щоб не впасти в ручну тягу). */
fm_mode_t fm_mode_best_available(bool attitude_ok, bool altitude_ok, bool position_ok);

#endif /* FM_MODES_H */
