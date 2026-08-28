// Кільце дальностей: dist[i] — відстань до перешкоди під кутом angle[i].
// Апарат у початку координат; goal_x, goal_y — напрям на ціль (одиничний).
const int   N        = 72;          // 72 промені = крок 5°
const float influence = 2.0f;       // радіус впливу перешкоди, м: далі — ігноруємо
const float k_rep    = 1.5f;        // сила відштовхування
const float k_att    = 1.0f;        // сила притягання до цілі

float fx = k_att * goal_x;          // тяга цілі
float fy = k_att * goal_y;

for (int i = 0; i < N; i++) {
    float d = dist[i];
    if (d <= 0.0f || d > influence) continue;   // немає відбитку або задалеко

    // Одиничний вектор ВІД перешкоди до апарата (напрям поштовху).
    float ox = -cosf(angle[i]);
    float oy = -sinf(angle[i]);

    // Що ближче перешкода, то сильніший поштовх (∝ 1/d² — різко зростає впритул).
    float strength = k_rep * (1.0f / (d * d));
    fx += strength * ox;
    fy += strength * oy;
}

float heading = atan2f(fy, fx);     // куди кермувати цієї миті
