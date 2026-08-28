#include <stdint.h>

#define Q      16                 /* дробових бітів у Q-форматі коефіцієнтів */
#define Q_ONE  (1L << Q)          /* 1.0 у Q16 = 65536                        */

typedef struct {
    /* параметри (задаємо раз при ініціалізації, усе в Q16) */
    int32_t kp_q;                 /* Kp у Q16                                 */
    int32_t ki_q;                 /* Ki у Q16                                 */
    int32_t kt_q;                 /* коефіцієнт зворотн. перерахунку, Q16     */
    int32_t u_min, u_max;         /* межі виходу (одиниці виконавчого органу) */
    /* стан (живе між тактами) */
    int64_t integ;                /* накопичувач — ПОВНИЙ масштаб, широке слово */
} PI_fx;

void pi_fx_init(PI_fx *c, int32_t kp_q, int32_t ki_q, int32_t kt_q,
                int32_t u_min, int32_t u_max)
{
    c->kp_q  = kp_q;
    c->ki_q  = ki_q;
    c->kt_q  = kt_q;
    c->u_min = u_min;
    c->u_max = u_max;
    c->integ = 0;                 /* обов'язково з нуля                       */
}
