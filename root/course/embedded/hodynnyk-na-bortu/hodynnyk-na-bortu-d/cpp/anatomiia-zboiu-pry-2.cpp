// НЕПРАВИЛЬНО: обчислення dt через настінний час
void pid_update(float target, float current) {
    auto now = std::chrono::system_clock::now();
    std::chrono::duration<float> dt_duration = now - last_time;
    last_time = now;

    float dt = dt_duration.count();
    // При коригуванні назад dt від'ємне, що інвертує знак інтегратора й похідної
    float error = target - current;
    integral += error * dt;
    float derivative = (error - prev_error) / dt;

    apply_actuator_output(Kp * error + Ki * integral + Kd * derivative);
}
