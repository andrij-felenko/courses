/* Найближча точка відрізка A→B до точки c (проєкція, затиснута в [0,1]). */
static vec2 seg_closest(vec2 c, vec2 A, vec2 B)
{
    float dx = B.x - A.x,  dy = B.y - A.y;
    float len2 = dx * dx + dy * dy;
    if (len2 < 1e-9f) return A;                /* вироджений відрізок → сам A */

    float t = ((c.x - A.x) * dx + (c.y - A.y) * dy) / len2;
    if (t < 0.0f) t = 0.0f;                    /* до початку — тримаємось A */
    if (t > 1.0f) t = 1.0f;                    /* за кінець — тримаємось B */

    vec2 p = { A.x + t * dx, A.y + t * dy };
    return p;
}
