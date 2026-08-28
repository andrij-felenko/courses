/* Знайти ціль-точку цього такту. Кладе її у *goal, повертає true, поки їдемо.
 * false — коли шлях завершено (апарат у межах goal_tol від останньої вершини). */
static bool pursuit_find_goal(pursuit_t *pp, vec2 c, float L, vec2 *goal)
{
    int last = pp->n - 1;

    /* 1) шукаємо перетин попереду, від поточного відрізка й далі */
    for (int i = pp->seg; i < last; ++i) {
        float t;
        if (seg_circle_hit(c, L, pp->path[i], pp->path[i + 1], &t)) {
            pp->seg = i;                       /* запам'ятали відрізок цілі */
            vec2 A = pp->path[i], B = pp->path[i + 1];
            goal->x = A.x + t * (B.x - A.x);
            goal->y = A.y + t * (B.y - A.y);
            return true;
        }
    }

    /* 2) перетину нема. Чи ми вже біля кінця шляху? */
    vec2 end = pp->path[last];
    float ex = end.x - c.x, ey = end.y - c.y;
    if (ex * ex + ey * ey <= pp->goal_tol * pp->goal_tol) {
        pp->finished = true;
        return false;                          /* доїхали — зупиняємось */
    }

    /* 3) не кінець, але перетину нема → ДІРКА: тягнемось до найближчої точки лінії */
    vec2 A = pp->path[pp->seg], B = pp->path[pp->seg + 1];
    *goal = seg_closest(c, A, B);
    return true;
}
