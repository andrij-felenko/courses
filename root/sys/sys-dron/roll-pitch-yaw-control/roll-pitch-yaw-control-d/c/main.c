// Стан трьох ПІД живе МІЖ викликами (накопичений інтеграл і попередній кут).
typedef struct { float kp, ki, kd; float integ, prev_meas; } PID;

// Один такт одного ПІД: похибка -> команда осі. dt — фактичний крок (с).
static float pid_step(PID *c, float target, float meas, float dt) {
    float e      = target - meas;                 // похибка кута
    c->integ    += e * dt;                        // I: накопичуємо площу похибки
    c->integ     = clampf(c->integ, -I_MAX, I_MAX); // антивіндап (інакше дикий переліт)
    float deriv  = -(meas - c->prev_meas) / dt;   // D від ВИМІРУ (без ривка на зміні завдання)
    c->prev_meas = meas;
    return c->kp * e + c->ki * c->integ + c->kd * deriv; // P + I + D = команда осі
}

// Три ОКРЕМІ контури — по одному на вісь. Викликати РІВНОМІРНО з таймера.
void attitude_step(const float meas[3], const float target[3],
                   float throttle, float dt, float motor[4]) {
    // 1) три незалежні ПІД: кожен бачить ЛИШЕ свою вісь
    float roll  = pid_step(&pid_roll,  target[0], meas[0], dt);
    float pitch = pid_step(&pid_pitch, target[1], meas[1], dt);
    float yaw   = pid_step(&pid_yaw,   target[2], meas[2], dt);

    // 2) МІКШЕР: три команди + база -> тяга кожного мотора (знаки = геометрія рами)
    motor[0] = throttle - roll - pitch - yaw;   // M1 спереду-справа
    motor[1] = throttle - roll + pitch + yaw;   // M2 ззаду-справа
    motor[2] = throttle + roll + pitch - yaw;   // M3 ззаду-зліва
    motor[3] = throttle + roll - pitch + yaw;   // M4 спереду-зліва

    // 3) затиск у фізичні межі ESC (мотор не вміє менше 0 чи більше за повну тягу)
    for (int i = 0; i < 4; i++)
        motor[i] = clampf(motor[i], MOTOR_MIN, MOTOR_MAX);
}
