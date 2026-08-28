// Чи безпечна швидкість v за наявної відстані d до перешкоди?
static bool speed_is_safe(float v, float d, float a, float t_lag)
{
    float d_stop = v * t_lag + (v * v) / (2.0f * a);
    return d_stop <= d;                       // встигаємо стати?
}

// Найбільша безпечна швидкість перед перешкодою на відстані d.
// Розв'язок нерівності v·t_lag + v²/(2a) ≤ d відносно v (беремо додатний корінь).
static float max_safe_speed(float d, float a, float t_lag)
{
    // ½/a · v² + t_lag · v − d = 0  →  v = (−t_lag + √(t_lag² + 2d/a)) / (1/a)
    float A = 1.0f / (2.0f * a);
    float B = t_lag;
    float C = -d;
    float disc = B * B - 4.0f * A * C;         // завжди ≥ 0, бо C < 0
    return (-B + sqrtf(disc)) / (2.0f * A);
}

// Виклик:
float d = 2.0f, a = 3.0f, t_lag = 0.1f;
float v_max = max_safe_speed(d, a, t_lag);     // ≈ 3.16 м/с
bool  ok    = speed_is_safe(2.0f, d, a, t_lag); // true: 2 м/с ще безпечно
