const uint8_t PIN_TOUCH = 4;   // SIG давача TTP223

void setup() {
    pinMode(PIN_TOUCH, INPUT);         // INPUT, не INPUT_PULLUP: вихід двотактний
    Serial.begin(9600);
}

void loop() {
    bool touched = (digitalRead(PIN_TOUCH) == HIGH);  // активний у 1
    Serial.println(touched ? "палець" : "-");
    delay(100);
}
