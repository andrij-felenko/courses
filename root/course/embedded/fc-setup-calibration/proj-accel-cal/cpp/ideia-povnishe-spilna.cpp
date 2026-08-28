// Каркас спільної підгонки (Ґаус–Ньютон) — суть, без матричної кухні.
// Мінімізуємо Σ (g − ‖M·(sᵢ − o)‖)² за 6 параметрами: o.{x,y,z}, s.{x,y,z}.
static bool accel_solve_ellipsoid(const vec3_t s[N_FACES], int n, accel_cal_t *cal)
{
    // старт: зсуви нуль, масштаби одиниця
    cal->offset = (vec3_t){0, 0, 0};
    cal->scale  = (vec3_t){1, 1, 1};

    for (int iter = 0; iter < 20; iter++) {
        // 1) для кожного вектора порахувати невязку εᵢ = g − ‖M·(sᵢ − o)‖
        // 2) зібрати якобіан ∂εᵢ/∂(параметри)
        // 3) розв'язати нормальні рівняння JᵀJ·Δp = −Jᵀε (6×6)
        // 4) оновити параметри: p += Δp
        float delta = gauss_newton_step(s, n, cal);   // повертає норму кроку
        if (delta < 1e-6f) break;                     // зійшлося
    }

    // та сама перевірка здорового глузду, що й у простому розв'язку
    for (int k = 0; k < 3; k++) {
        float sc = (&cal->scale.x)[k], of = (&cal->offset.x)[k];
        if (sc < 0.8f || sc > 1.2f || fabsf(of) > GRAVITY_MSS) return false;
    }
    return true;
}
