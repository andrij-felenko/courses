// НЕПРАВИЛЬНО: обчислення dt через настінний час
void pid_update(float target, float current) {
    uint32_t now_ms = get_wall_time_ms();
    float dt = (float)(now_ms - last_time_ms) / 1000.0f;
    last_time_ms = now_ms;

    // Якщо час стрибнув назад, dt < 0 або dt == 0 (ділення на нуль!)
    float error = target - current;
    integral += error * dt;
    float derivative = (error - prev_error) / dt; // Вибух значення при dt -> 0
    prev_error = error;

    apply_actuator_output(Kp * error + Ki * integral + Kd * derivative);
}
