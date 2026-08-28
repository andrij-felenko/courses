/* Перетин кола (центр c, радіус L) з відрізком A→B.
 * Якщо є корінь ПОПЕРЕДУ (більший) у межах [0,1] — кладе його в *t_out,
 * повертає true. Інакше false (перетину на цьому відрізку немає). */
static bool seg_circle_hit(vec2 c, float L, vec2 A, vec2 B, float *t_out)
{
    float dx = B.x - A.x,  dy = B.y - A.y;     /* d = B − A */
    float fx = A.x - c.x,  fy = A.y - c.y;     /* f = A − c */

    float a = dx * dx + dy * dy;               /* a = d·d   */
    float b = 2.0f * (fx * dx + fy * dy);      /* b = 2 f·d */
    float cc = fx * fx + fy * fy - L * L;      /* c = f·f − L² */

    if (a < 1e-9f) return false;               /* вироджений (нульовий) відрізок */

    float disc = b * b - 4.0f * a * cc;
    if (disc < 0.0f) return false;             /* коло не дістає відрізка (дірка) */

    float sq = sqrtf(disc);
    float t2 = (-b + sq) / (2.0f * a);         /* БІЛЬШИЙ корінь — попереду за рухом */

    if (t2 >= 0.0f && t2 <= 1.0f) {            /* і лежить у межах відрізка? */
        *t_out = t2;
        return true;
    }
    return false;                              /* попереднього перетину на відрізку нема */
}
