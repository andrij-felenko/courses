const uint8_t PIN_TOUCH = 4;

bool     prev  = false;   // стан входу з минулого проходу loop()
uint32_t count = 0;

void setup() {
    pinMode(PIN_TOUCH, INPUT);
    Serial.begin(9600);
}

void loop() {
    bool now = (digitalRead(PIN_TOUCH) == HIGH);

    if (now && !prev) {           // було 0, стало 1 → передній фронт = момент дотику
        count++;
        Serial.print("дотиків: ");
        Serial.println(count);
    }
    // if (!now && prev) { ... }  // тут ловився б задній фронт = момент відпускання

    prev = now;                   // запам'ятали для наступного проходу
    delay(20);
}
