// Кут центру сектора k у радіанах (0 = прямо вперед).
static inline float sector_angle(int k)
{
    return (float)k * (2.0f * (float)M_PI / N_SECTORS);
}

// Найкоротша кутова різниця (a − b), зведена в діапазон (−π, π].
static float angle_diff(float a, float b)
{
    float d = a - b;
    while (d >  (float)M_PI) d -= 2.0f * (float)M_PI;
    while (d <= -(float)M_PI) d += 2.0f * (float)M_PI;
    return d;
}

// Вибрати долину, найближчу до цілі, і повернути кермовий кут.
// goal_angle — напрям на ціль (рад); повертає бажаний кермовий кут (рад).
float vfh_steer(const Valley valleys[], int nv, float goal_angle)
{
    if (nv == 0)
        return goal_angle;          // жодної долини: віддаємо намір як є (аварія — див. нижче)

    int   best = -1;
    float best_off = 1e9f;          // відхилення краю обраної долини від цілі

    for (int v = 0; v < nv; v++) {
        int   s  = valleys[v].start;
        int   w  = valleys[v].width;
        int   kf = (s + w - 1) % N_SECTORS;        // дальній край долини

        // Відхилення того краю долини, що ближчий до напряму на ціль.
        float off_s = fabsf(angle_diff(sector_angle(s),  goal_angle));
        float off_e = fabsf(angle_diff(sector_angle(kf), goal_angle));
        float off   = (off_e < off_s) ? off_e : off_s;

        // Якщо ціль дивиться ВСЕРЕДИНУ долини — відхилення нульове.
        // Простий тест: краї лежать по різні боки від напряму на ціль.
        float ds = angle_diff(sector_angle(s),  goal_angle);
        float de = angle_diff(sector_angle(kf), goal_angle);
        if (ds <= 0.0f && de >= 0.0f) off = 0.0f;

        if (off < best_off) { best_off = off; best = v; }
    }

    // Маємо найкращу долину — тепер кут усередині неї.
    int s = valleys[best].start;
    int w = valleys[best].width;
    int kf = (s + w - 1) % N_SECTORS;

    float target;
    if (w >= S_MAX) {
        // ШИРОКА долина: край, ближчий до цілі, + пів-S_MAX усередину.
        float off_s = fabsf(angle_diff(sector_angle(s),  goal_angle));
        float off_e = fabsf(angle_diff(sector_angle(kf), goal_angle));
        if (off_s <= off_e)
            target = sector_angle((s + S_MAX / 2) % N_SECTORS);          // від початку всередину
        else
            target = sector_angle((kf - S_MAX / 2 + N_SECTORS) % N_SECTORS);  // від кінця всередину

        // Якщо ціль лежить у самій широкій долині — просто йдемо на ціль.
        float ds = angle_diff(sector_angle(s),  goal_angle);
        float de = angle_diff(sector_angle(kf), goal_angle);
        if (ds <= 0.0f && de >= 0.0f) target = goal_angle;
    } else {
        // ВУЗЬКА долина: точно в середину проходу.
        target = sector_angle((s + w / 2) % N_SECTORS);
    }
    return target;
}
