const uint8_t PIN_VRX = A0;
const uint8_t PIN_VRY = A1;
const uint8_t PIN_SW  = 2;

void setup() {
    pinMode(PIN_SW, INPUT_PULLUP);   // КЛЮЧОВЕ: на модулі підтяжки немає
    Serial.begin(9600);
}

void loop() {
    int x = analogRead(PIN_VRX);          // 0..1023: центр ≈ 512
    int y = analogRead(PIN_VRY);          // 0..1023: центр ≈ 512
    bool pressed = (digitalRead(PIN_SW) == LOW);  // натиск = LOW (підтяжка!)

    Serial.print("X="); Serial.print(x);
    Serial.print(" Y="); Serial.print(y);
    Serial.print(" SW="); Serial.println(pressed ? "натиснуто" : "-");
    delay(500);
}
