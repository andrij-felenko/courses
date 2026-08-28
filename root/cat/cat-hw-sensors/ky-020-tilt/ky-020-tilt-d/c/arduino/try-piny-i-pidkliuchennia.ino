const uint8_t TILT = 2;    // пін S давача
const uint8_t LED  = 13;   // вбудований світлодіод

void setup() {
    pinMode(TILT, INPUT);  // підтяжка вже на модулі — INPUT_PULLUP не обов'язковий
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    // УВАГА: логіка перевернута — нахил дає LOW, спокій HIGH
    bool tilted = (digitalRead(TILT) == LOW);
    digitalWrite(LED, tilted);        // світимо, поки нахилено
    if (tilted) Serial.println("нахил!");
    delay(50);
}
