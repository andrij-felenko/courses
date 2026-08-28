/* Один такт pure pursuit. Вхід: позиція (px,py), курс theta [рад], швидкість v.
 * Вихід: кут керма delta [рад]. Коли шлях завершено — ставить pp->finished
 * і повертає 0 (кермо прямо). */
float pursuit_step(pursuit_t *pp, float px, float py, float theta, float v)
{
    if (pp->finished) return 0.0f;

    /* 1) випередження, пропорційне швидкості, з нижньою межею */
    float L = pp->k_look * v;
    if (L < pp->L_min) L = pp->L_min;

    /* 2) знайти ціль-точку */
    vec2 c = { px, py };
    vec2 goal;
    if (!pursuit_find_goal(pp, c, L, &goal)) {
        return 0.0f;                           /* шлях завершено */
    }

    /* 3) бічний зсув цілі в системі апарата (поворот на −theta) */
    float dx = goal.x - px;
    float dy = goal.y - py;
    float s = sinf(theta), co = cosf(theta);
    float x_lat = -s * dx + co * dy;           /* бічна координата цілі */

    /* 4) кривина дуги pure pursuit; L беремо як фактичну відстань до цілі */
    float Lx = dx, Ly = dy;
    float Lreal = sqrtf(Lx * Lx + Ly * Ly);    /* справжня відстань апарат→ціль */
    if (Lreal < 1e-3f) return 0.0f;            /* ціль злилась з апаратом — прямо */
    float kappa = 2.0f * x_lat / (Lreal * Lreal);

    /* 5) переклад у кут керма (велосипедна модель) + затиск межами */
    float delta = atanf(pp->wheelbase * kappa);
    if (delta >  pp->delta_max) delta =  pp->delta_max;
    if (delta < -pp->delta_max) delta = -pp->delta_max;

    return delta;
}
