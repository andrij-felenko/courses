const uint8_t TOUCH = 4;    // SIG давача TTP223
const uint8_t LED   = 13;   // вбудований світлодіод

void setup() {
    pinMode(TOUCH, INPUT);  // просто INPUT: вихід двотактний, підтяжка не потрібна
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    bool touched = (digitalRead(TOUCH) == HIGH);  // активний у 1: дотик = HIGH
    digitalWrite(LED, touched);
    if (touched) Serial.println("дотик!");
    delay(20);
}
