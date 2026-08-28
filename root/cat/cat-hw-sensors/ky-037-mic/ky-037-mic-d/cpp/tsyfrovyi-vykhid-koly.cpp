const uint8_t SOUND = 3;          // цифровий вихід KY-037
const uint8_t LED   = 13;         // вбудований світлодіод плати

void setup() {
    pinMode(SOUND, INPUT);
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    int hit = digitalRead(SOUND);  // спрацював поріг чи ні
    digitalWrite(LED, hit);        // світимо, поки є звук понад поріг
    Serial.println(hit);
}
