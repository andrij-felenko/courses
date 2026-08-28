// Драйвер DC-мотора через H-міст (тип TB6612/DRV8833): два ШІМ-входи на мотор.
// speed: -255..+255 (знак = напрямок, модуль = шпаруватість).
#define PWM_CH_IN1  0      // апаратний ШІМ-канал входу IN1
#define PWM_CH_IN2  1      // апаратний ШІМ-канал входу IN2

void motor_drive(int speed) {
    if (speed > 255)  speed = 255;          // обрізаємо до діапазону
    if (speed < -255) speed = -255;

    int duty = speed < 0 ? -speed : speed;  // модуль = шпаруватість

    if (speed > 0) {                        // уперед: ШІМ на IN1, IN2 мовчить
        ledcWrite(PWM_CH_IN1, duty);
        ledcWrite(PWM_CH_IN2, 0);
    } else if (speed < 0) {                 // назад: навпаки
        ledcWrite(PWM_CH_IN1, 0);
        ledcWrite(PWM_CH_IN2, duty);
    } else {                                // 0 → вибіг (обидва входи в нулі)
        ledcWrite(PWM_CH_IN1, 0);
        ledcWrite(PWM_CH_IN2, 0);
    }
}

void motor_brake(void) {                    // різке гальмо: обидва входи високі
    ledcWrite(PWM_CH_IN1, 255);             // → мотор закорочено всередині моста
    ledcWrite(PWM_CH_IN2, 255);
}
