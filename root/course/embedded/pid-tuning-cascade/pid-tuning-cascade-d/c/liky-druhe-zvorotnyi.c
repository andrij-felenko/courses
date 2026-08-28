static float integral = 0.0f;
static float e_prev   = 0.0f;

float pid_backcalc(float setpoint, float measurement, float dt,
                   float u_min, float u_max, float Kaw) {
    float e = setpoint - measurement;
    float derivative = (e - e_prev) / dt;
    e_prev = e;

    float u_unsat = Kp * e + Ki * integral + Kd * derivative;

    // обрізаємо
    float u = u_unsat;
    if (u > u_max) u = u_max;
    if (u < u_min) u = u_min;

    // розвантаження: різниця (дійсне − бажане) підтягує інтеграл назад
    integral += (Ki * e + Kaw * (u - u_unsat)) * dt;
    return u;
}
