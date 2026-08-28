const uint8_t  LASER  = 4;    // KY-008 S
const uint8_t  LDR    = A0;   // KY-018 сигнал -> аналоговий вхід (Arduino)
const int      THRESH = 400;  // поріг «світло/темно», підбирається під місце

void setup() {
    pinMode(LASER, OUTPUT);
    digitalWrite(LASER, HIGH);   // промінь горить постійно — тримає бар'єр
    Serial.begin(115200);
}

void loop() {
    int light = analogRead(LDR);          // 0..1023 на Arduino Uno
    bool broken = (light < THRESH);       // темно -> промінь перекрито

    if (broken) {
        Serial.println("ПЕРЕТИН!");
    }
    delay(20);
}
