const int TRIG_PIN = 9;
const int ECHO_PIN = 10;

void setup() {
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    Serial.begin(9600);
}

long measureCm() {
    // 1. Спусковий імпульс: 10 мкс високого рівня на TRIG
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // 2. Ширина високого імпульсу на ECHO = час польоту в мкс.
    //    Тайм-аут 30000 мкс, щоб не зависнути, коли луни немає.
    long t = pulseIn(ECHO_PIN, HIGH, 30000);

    if (t == 0) return -1;          // нічого не почули (порожньо/далеко)
    return t / 58;                  // мкс → см
}

void loop() {
    long cm = measureCm();
    if (cm < 0) Serial.println("out of range");
    else        { Serial.print(cm); Serial.println(" cm"); }
    delay(60);                       // пауза між вимірами ≥ 60 мс
}
