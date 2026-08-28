/* Оцінка струму конденсатора зі швидкості зміни виміряної напруги.
   i = C * dV/dt,  похідну беремо як (V[n] - V[n-1]) / dt           */

static const float C  = 100e-6f;   /* ємність, Ф (100 мкФ)          */
static const float dt = 1.0e-3f;   /* період відліків АЦП, с (1 мс) */

static float v_prev    = 0.0f;
static bool  have_prev = false;

/* Повертає оцінку струму крізь конденсатор у амперах */
float cap_current(float v_now)
{
    if (!have_prev) {              /* перший відлік: похідної ще нема */
        v_prev    = v_now;
        have_prev = true;
        return 0.0f;
    }
    float dvdt = (v_now - v_prev) / dt;   /* швидкість зміни напруги */
    v_prev = v_now;
    return C * dvdt;                       /* i = C * dV/dt           */
}
