static float integral = 0.0f;
static float e_prev   = 0.0f;

float pid_clamp(float setpoint, float measurement, float dt,
                float u_min, float u_max) {
    float e = setpoint - measurement;

    // пробне накопичення
    float integral_candidate = integral + e * dt;

    float derivative = (e - e_prev) / dt;
    e_prev = e;

    // необмежений вихід із пробним інтегралом
    float u = Kp * e + Ki * integral_candidate + Kd * derivative;

    // фіксуємо інтеграл, лише якщо ми НЕ заганяємо вихід глибше в стелю
    bool saturated_high = (u > u_max) && (e > 0.0f);
    bool saturated_low  = (u < u_min) && (e < 0.0f);
    if (!saturated_high && !saturated_low) {
        integral = integral_candidate;   // приймаємо накопичення
    }                                     // інакше — лишаємо старий інтеграл

    // обрізаємо вихід до фізичних меж
    if (u > u_max) u = u_max;
    if (u < u_min) u = u_min;
    return u;
}
