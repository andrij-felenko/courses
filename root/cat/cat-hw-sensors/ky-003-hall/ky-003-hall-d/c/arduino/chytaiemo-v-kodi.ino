const uint8_t HALL = 3;    // S давача KY-003
const uint8_t LED  = 13;   // вбудований світлодіод

void setup() {
    pinMode(HALL, INPUT_PULLUP);   // без підтяжки нога висить — читатимеш сміття
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    // вихід активний у нулі: LOW = є магніт
    bool magnet = (digitalRead(HALL) == LOW);
    digitalWrite(LED, magnet);
    if (magnet) Serial.println("магніт!");
    delay(50);
}
