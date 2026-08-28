const uint8_t PIR = 2;     // OUT давача
const uint8_t LED = 13;    // вбудований світлодіод

void setup() {
    pinMode(PIR, INPUT);   // вихід давача сам штовхає рівень — підтяжка не потрібна
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    int motion = digitalRead(PIR);   // 1 = є рух, 0 = немає
    digitalWrite(LED, motion);
    if (motion) Serial.println("рух!");
    delay(50);
}
