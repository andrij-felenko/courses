// Прокрутити дугу пари (v, w) і знайти відстань по дузі до першої
// перешкоди (з урахуванням габариту апарата). Повертає зазор, м.
// obst_dist[] — кільце дальностей: obst_dist[i] = відстань під кутом сектора i.
float arc_clearance(float v, float w, const float obst_dist[N_RAYS])
{
    // Стоїмо на місці — нема руху, нема й дуги: зазор невизначений.
    if (v < 1e-4f) return D_INF;

    const int   STEPS = 20;                    // поділок часу вздовж дуги
    const float dt    = T_PREDICT / STEPS;     // крок часу прокрутки

    float x = 0.0f, y = 0.0f, th = 0.0f;       // поза апарата в його ж кадрі
    float travelled = 0.0f;                    // пройдено по дузі, м

    for (int s = 0; s < STEPS; s++) {
        // Крок руху по дузі за час dt (проста інтеграція кінематики).
        x  += v * cosf(th) * dt;
        y  += v * sinf(th) * dt;
        th += w * dt;
        travelled += v * dt;                   // приріст довжини дуги = v·dt

        // Полярні координати поточної точки апарата.
        float r   = sqrtf(x * x + y * y);      // як далеко від старту
        float ang = atan2f(y, x);              // під яким кутом ця точка

        // Який промінь давача дивиться в цей бік.
        int idx = (int)lroundf(ang / (2.0f * (float)M_PI) * N_RAYS);
        idx = ((idx % N_RAYS) + N_RAYS) % N_RAYS;   // у діапазон [0, N_RAYS)

        // Перешкода в цьому напрямку ближча, ніж наша точка + габарит?
        // Тоді тіло апарата в цій точці чиркне об перешкоду.
        if (obst_dist[idx] < r + ROBOT_RADIUS)
            return travelled;                  // зіткнення: віддаємо пройдений шлях
    }
    return D_INF;                              // до горизонту чисто
}
