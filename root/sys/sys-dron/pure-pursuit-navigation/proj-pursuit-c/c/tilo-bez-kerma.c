/* Замість кута керма — цільова кутова швидкість для диференціального тіла.
 * Далі ці v та omega розкладають на швидкості боків (див. керування ровером). */
typedef struct { float v, omega; } twist_t;

twist_t pursuit_step_diff(pursuit_t *pp, float px, float py,
                          float theta, float v)
{
    twist_t out = { 0.0f, 0.0f };
    if (pp->finished) return out;

    float L = pp->k_look * v;
    if (L < pp->L_min) L = pp->L_min;

    vec2 c = { px, py }, goal;
    if (!pursuit_find_goal(pp, c, L, &goal)) return out;   /* v=omega=0 */

    float dx = goal.x - px, dy = goal.y - py;
    float s = sinf(theta), co = cosf(theta);
    float x_lat = -s * dx + co * dy;
    float Lreal = sqrtf(dx * dx + dy * dy);
    if (Lreal < 1e-3f) { out.v = v; return out; }

    float kappa = 2.0f * x_lat / (Lreal * Lreal);
    out.v     = v;                             /* лінійна швидкість — від контуру швидкості */
    out.omega = v * kappa;                     /* кутова швидкість повороту */
    return out;
}
