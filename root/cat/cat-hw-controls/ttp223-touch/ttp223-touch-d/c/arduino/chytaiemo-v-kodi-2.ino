const uint8_t TOUCH = 4;

bool     prev  = false;   // попередній стан входу
uint32_t count = 0;       // скільки разів торкнулися

void setup() {
    pinMode(TOUCH, INPUT);
    Serial.begin(9600);
}

void loop() {
    bool now = (digitalRead(TOUCH) == HIGH);
    if (now && !prev) {           // щойно був 0, тепер 1 → фронт, момент дотику
        count++;
        Serial.print("дотиків: ");
        Serial.println(count);
    }
    prev = now;
    delay(20);
}
