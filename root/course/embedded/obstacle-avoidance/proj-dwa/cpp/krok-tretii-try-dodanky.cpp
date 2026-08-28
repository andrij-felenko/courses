typedef struct {
    float v, w;         // сама пара швидкостей
    float heading;      // сирий доданок «до цілі», рад
    float dist;         // сирий доданок «зазор», м
    float velocity;     // сирий доданок «швидкість», м/с
    int   admissible;   // 1 = допустима (див. Va нижче), 0 = відкинута
} Cand;

// Найкоротша кутова різниця (a − b), зведена в діапазон (−π, π].
static float angle_diff(float a, float b)
{
    float d = a - b;
    while (d >  (float)M_PI) d -= 2.0f * (float)M_PI;
    while (d <= -(float)M_PI) d += 2.0f * (float)M_PI;
    return d;
}

// Сирі три доданки для однієї пари (goal_ang — напрям на ціль, рад).
static void score_raw(Cand *c, const float obst_dist[N_RAYS], float goal_ang)
{
    // Кінцевий курс апарата після прокрутки дуги на T_PREDICT.
    float final_heading = c->w * T_PREDICT;              // Δθ = ω·t
    float err = fabsf(angle_diff(final_heading, goal_ang));
    c->heading = (float)M_PI - err;                      // менше відхилення — більше

    // Зазор до перешкоди на дузі (габарит уже враховано всередині).
    c->dist = arc_clearance(c->v, c->w, obst_dist);
    if (c->dist > D_INF) c->dist = D_INF;                // обрізаємо зверху

    c->velocity = c->v;                                  // сира швидкість

    // ── Va: допустимість за гальмівним шляхом (математика — в основній статті). ──
    // Пара допустима, лише якщо з неї встигаємо стати перед знайденою перешкодою:
    // повний шлях зупинки не довший за зазор dist.
    float d_stop = c->v * T_LAG + (c->v * c->v) / (2.0f * A_BRAKE);
    c->admissible = (d_stop <= c->dist) ? 1 : 0;
}
