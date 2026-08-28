static inline float clampf(float v, float lo, float hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

float u = comp_step(&lead, e);
u = clampf(u, U_MIN, U_MAX);     // обмеження у фізичні межі привода
drive_actuator(u);
