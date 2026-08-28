// зовнішній контур кута: його вихід — бажана кутова швидкість для внутрішнього
float rate_setpoint = pid_angle_step(angle_target, angle_meas, dt);

// фізична межа кутової швидкості апарата
const float RATE_MAX = 400.0f;   // град/с, приклад

// затиск завдання + анти-віндап зовнішнього інтеграла
if (rate_setpoint >  RATE_MAX) { rate_setpoint =  RATE_MAX; angle_integral_freeze = true; }
if (rate_setpoint < -RATE_MAX) { rate_setpoint = -RATE_MAX; angle_integral_freeze = true; }

// далі внутрішній контур відпрацьовує (уже обмежене) завдання швидкості
float u = pid_rate_step(rate_setpoint, gyro_rate, dt);
