typedef struct {
    vec3_t offset;   // зсув осей, м/с²   → INS_ACCOFFS_X/Y/Z
    vec3_t scale;    // масштаб осей       → INS_ACCSCAL_X/Y/Z
} accel_cal_t;

// Розв'язати одну вісь із двох відліків: коли вона дивилась угору (−1g) і вниз (+1g).
// raw_up  — сире число цієї осі в положенні, де вісь угору;
// raw_down — сире число цієї осі в положенні, де вісь униз.
static void solve_axis(float raw_up, float raw_down, float *offset, float *scale)
{
    *offset = (raw_up + raw_down) * 0.5f;                 // середина → зсув
    *scale  = (2.0f * GRAVITY_MSS) / (raw_down - raw_up); // 2g / розмах → масштаб
}

// Простий (окремо по осях) розв'язок із шести зібраних векторів.
static bool accel_solve_simple(const vec3_t s[N_FACES], accel_cal_t *cal)
{
    // Яка вісь у якому положенні дивиться вгору/вниз (за нашим порядком граней):
    //   X: носом униз → X угору (−1g);  носом угору → X вниз (+1g)
    //   Y: на лівий бік → Y угору;       на правий бік → Y вниз
    //   Z: рівно        → Z угору;       на спину       → Z вниз
    solve_axis(s[FACE_NOSEDOWN].x, s[FACE_NOSEUP].x,  &cal->offset.x, &cal->scale.x);
    solve_axis(s[FACE_LEFT].y,     s[FACE_RIGHT].y,   &cal->offset.y, &cal->scale.y);
    solve_axis(s[FACE_LEVEL].z,    s[FACE_BACK].z,    &cal->offset.z, &cal->scale.z);

    // здоровий глузд: масштаб має бути близький до 1, зсув — менший за g
    for (int k = 0; k < 3; k++) {
        float sc = (&cal->scale.x)[k];
        float of = (&cal->offset.x)[k];
        if (sc < 0.8f || sc > 1.2f)          return false;   // розмах не той — грань знято криво
        if (fabsf(of) > GRAVITY_MSS)         return false;   // зсув завеликий — щось не так
    }
    return true;
}
