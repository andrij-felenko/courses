// Другий прохід: нормувати три максимуми, зважити, вибрати найкращу пару.
// Повертає індекс переможця в cand[], або -1, якщо жодної допустимої нема.
int pick_best(const Cand cand[], int n)
{
    // 1) Знайти максимуми кожного доданка СЕРЕД ДОПУСТИМИХ пар.
    float h_max = 1e-6f, d_max = 1e-6f, v_max = 1e-6f;   // не нуль — щоб не ділити на 0
    for (int i = 0; i < n; i++) {
        if (!cand[i].admissible) continue;
        if (cand[i].heading  > h_max) h_max = cand[i].heading;
        if (cand[i].dist     > d_max) d_max = cand[i].dist;
        if (cand[i].velocity > v_max) v_max = cand[i].velocity;
    }

    // 2) Нормована зважена оцінка G для кожної допустимої пари.
    float G[N_V * N_W];
    for (int i = 0; i < n; i++) {
        if (!cand[i].admissible) { G[i] = -1.0f; continue; }   // недопустимі — геть
        G[i] = ALPHA * (cand[i].heading  / h_max)
             + BETA  * (cand[i].dist     / d_max)
             + GAMMA * (cand[i].velocity / v_max);
    }

    // 3) Легке згладжування по сусідах у сітці (гасить шумовий стрибок вибору).
    //    Сусіди по ω (± один стовпчик у тій самій v-смузі) — індекс i та i±1.
    int best = -1;
    float best_G = -1e9f;
    for (int i = 0; i < n; i++) {
        if (!cand[i].admissible) continue;
        float g = G[i];
        float acc = 2.0f * g, wsum = 2.0f;             // центр важить удвічі
        if (i > 0     && cand[i - 1].admissible) { acc += G[i - 1]; wsum += 1.0f; }
        if (i + 1 < n && cand[i + 1].admissible) { acc += G[i + 1]; wsum += 1.0f; }
        float g_smooth = acc / wsum;

        if (g_smooth > best_G) { best_G = g_smooth; best = i; }
    }
    return best;
}
