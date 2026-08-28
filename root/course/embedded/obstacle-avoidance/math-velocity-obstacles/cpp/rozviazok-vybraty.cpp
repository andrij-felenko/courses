// Кандидати — сітка у просторі швидкостей; беремо найкращий безпечний.
// obst[k] — перешкоди (позиції, швидкості, радіуси); vA_desired — намір.
Vec choose_velocity(Vec vA_desired, Vec pA, float rA,
                    const Obstacle* obst, int n, float v_max) {
    Vec  best = {0.0f, 0.0f};             // запасний варіант — стояти
    float best_cost = 1e30f;
    const int   STEPS = 41;               // 41×41 напрямів-величин
    const float step  = 2.0f * v_max / (STEPS - 1);

    for (int i = 0; i < STEPS; i++) {
        for (int j = 0; j < STEPS; j++) {
            Vec v = { -v_max + i*step, -v_max + j*step };
            if (v.x*v.x + v.y*v.y > v_max*v_max) continue;   // поза межею швидкості

            bool unsafe = false;
            for (int k = 0; k < n; k++)                       // у якийсь конус?
                if (velocity_in_vo(v, obst[k].v, pA, obst[k].p,
                                   rA, obst[k].r)) { unsafe = true; break; }
            if (unsafe) continue;

            float dx = v.x - vA_desired.x, dy = v.y - vA_desired.y;
            float cost = dx*dx + dy*dy;                       // відхил від наміру
            if (cost < best_cost) { best_cost = cost; best = v; }
        }
    }
    return best;                          // найближча до бажаної безпечна швидкість
}
