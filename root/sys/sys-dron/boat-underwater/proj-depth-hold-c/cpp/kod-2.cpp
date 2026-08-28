/* --- Вертикальний контур утримання глибини --- */
typedef struct {
    /* параметри регулятора */
    float kp, ki, kd;       /* коеф. П, І, Д (для осі глибини)            */
    float tau_d;            /* стала фільтра похідної, с                 */
    float i_min, i_max;     /* межі інтеграла (антивіндап)               */
    float u_min, u_max;     /* межі виходу = межі вертикальної тяги, −1..+1 */
    /* стан */
    float integral;         /* накопичена тяга проти сталої плавучості   */
    float depth_prev;       /* глибина на попередньому такті             */
    float deriv_f;          /* згладжена вертикальна швидкість           */
} DepthPID;

static inline float clampf(float x, float lo, float hi)
{
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

void depth_pid_init(DepthPID *c, float kp, float ki, float kd, float tau_d,
                    float i_min, float i_max, float u_min, float u_max)
{
    c->kp = kp;  c->ki = ki;  c->kd = kd;  c->tau_d = tau_d;
    c->i_min = i_min;  c->i_max = i_max;
    c->u_min = u_min;  c->u_max = u_max;
    c->integral = 0.0f;  c->depth_prev = 0.0f;  c->deriv_f = 0.0f;
}

/* Скидання перед вмиканням режиму: щоб перша похідна не «вистрелила»,
   а інтеграл не тягнув накопичене за простою. */
void depth_pid_reset(DepthPID *c, float depth_now)
{
    c->integral   = 0.0f;
    c->depth_prev = depth_now;   /* перша похідна = 0, не сплеск          */
    c->deriv_f    = 0.0f;
}

/* Один такт. target/measured — глибина в метрах (вниз додатна).
   Повертає нормовану вертикальну тягу u ∈ [u_min, u_max]:
   u>0 — гребти ВНИЗ (глибше), u<0 — гребти ВГОРУ (до поверхні). */
float depth_pid_step(DepthPID *c, float target, float measured, float dt)
{
    float e = target - measured;                 /* глибше цілі → e<0     */

    /* I: накопичуємо й ОДРАЗУ затискаємо (антивіндап) */
    c->integral += e * dt;
    c->integral = clampf(c->integral, c->i_min, c->i_max);

    /* D: від ВИМІРУ (не від помилки) → нема поштовху на зміну target.
       (depth_prev − measured)/dt = мінус вертикальна швидкість. */
    float deriv = (c->depth_prev - measured) / dt;
    float a = dt / (dt + c->tau_d);              /* коеф. ФНЧ на похідну  */
    c->deriv_f += (deriv - c->deriv_f) * a;

    /* сума трьох складових */
    float u = c->kp * e + c->ki * c->integral + c->kd * c->deriv_f;

    /* межі вертикальної тяги (насичення рушіїв) */
    u = clampf(u, c->u_min, c->u_max);

    c->depth_prev = measured;
    return u;
}
