const uint8_t TILT = 2;    // пін S давача

inline bool isTilted() {
    // Уся інверсія — ТУТ, і більше ніде. LOW = кулька сіла на землю = нахил.
    return digitalRead(TILT) == LOW;
}

void setup() {
    pinMode(TILT, INPUT);  // підтяжка вже на модулі; INPUT_PULLUP теж годиться, гірше не буде
    Serial.begin(9600);
}

void loop() {
    Serial.println(isTilted() ? "нахил" : "рівно");
    delay(200);
}
