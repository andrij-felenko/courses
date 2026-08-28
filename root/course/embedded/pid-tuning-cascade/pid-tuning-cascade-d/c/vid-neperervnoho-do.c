// стан регулятора між викликами
static float integral = 0.0f;
static float e_prev   = 0.0f;

float pid_step(float setpoint, float measurement, float dt) {
    float e = setpoint - measurement;
    integral += e * dt;                    // накопичуємо суму e·Δt
    float derivative = (e - e_prev) / dt;  // нахил між відліками
    e_prev = e;
    return Kp * e + Ki * integral + Kd * derivative;
}
