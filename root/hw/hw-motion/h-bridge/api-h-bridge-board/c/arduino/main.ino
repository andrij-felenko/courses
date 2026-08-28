// Керування модулем-драйвером (IN1/IN2 — напрямок, EN — ШІМ-швидкість).
// speed: -255..+255 (знак = напрямок, модуль = шпаруватість каналу EN).
void motor_drive(int speed) {
    if (speed >  255) speed =  255;          // обрізаємо до діапазону ШІМ
    if (speed < -255) speed = -255;
    int duty = speed < 0 ? -speed : speed;   // модуль = швидкість

    digitalWrite(IN1, speed >= 0);           // напрямок: вперед при speed >= 0
    digitalWrite(IN2, speed <  0);
    analogWrite(EN, speed == 0 ? 0 : duty);  // швидкість через ШІМ на виводі EN
}
