const int   SERVO_PIN = 9;
const int   FRAME_US  = 20000;        // кадр 20 мс = 50 Гц

// кут 0..180°  →  ширина 1000..2000 мкс (лінійна підстановка)
int angle_to_us(int deg) {
    if (deg < 0)   deg = 0;
    if (deg > 180) deg = 180;
    return 1000 + (long)deg * 1000 / 180;   // 0°→1000, 90°→1500, 180°→2000
}

// один кадр: імпульс заданої ширини + добивання паузи до 20 мс
void servo_frame(int pin, int width_us) {
    digitalWrite(pin, HIGH);
    delayMicroseconds(width_us);             // ширина = кут
    digitalWrite(pin, LOW);
    delayMicroseconds(FRAME_US - width_us);  // решта кадру — пауза
}
