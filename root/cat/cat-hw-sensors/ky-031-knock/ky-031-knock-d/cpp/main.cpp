const uint8_t KNOCK = 2;        // вивід S давача стуку
const uint8_t LED   = 13;       // вбудований світлодіод
const unsigned long LOCKOUT = 250;   // глухе вікно після стуку, мс

unsigned long lastKnock = 0;    // час останнього зарахованого стуку
unsigned long count     = 0;    // лічильник стуків

void setup() {
    pinMode(KNOCK, INPUT_PULLUP);   // підтяжка вгору: спокій = 1, удар тягне до 0
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    // активний-НИЗЬКО: удар — це коли вхід просів у 0
    if (digitalRead(KNOCK) == LOW && millis() - lastKnock > LOCKOUT) {
        lastKnock = millis();
        count++;
        digitalWrite(LED, HIGH);
        Serial.print("стук #");
        Serial.println(count);
    }
    // гасимо світлодіод трохи згодом після спалаху
    if (millis() - lastKnock > 60) digitalWrite(LED, LOW);
}
