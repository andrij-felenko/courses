/* dt — час між відліками АЦП у секундах */
static const float dt = 0.010f;   /* 10 мс */
static float  x_prev    = 0.0f;
static bool   have_prev = false;

/* Повертає миттєву швидкість зміни сигналу [одиниць/с] */
float sample_rate_of_change(float x_now)
{
    if (!have_prev) {
        x_prev    = x_now;
        have_prev = true;
        return 0.0f;   /* перший відлік: похідна невідома */
    }
    float dx_dt = (x_now - x_prev) / dt;   /* скінченна різниця ≈ похідна */
    x_prev = x_now;
    return dx_dt;
}
