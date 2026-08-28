// Звуковий давач на LM393 → ESP32.
// DO давача на GPIO4, вбудований світлодіод на GPIO2 (є на більшості плат).
// ISR має жити в IRAM (IRAM_ATTR); спільну змінну ховаємо в критичну секцію.

const uint8_t SOUND = 4;                  // DO на GPIO4 (переривання є на будь-якій GPIO)
const uint8_t LED   = 2;                  // вбудований світлодіод
const unsigned long WINDOW = 150;

volatile unsigned long lastHit = 0;
volatile unsigned long count   = 0;
volatile bool ready = false;
portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;   // спінлок для спільних даних

void IRAM_ATTR onSound() {                // на ESP32 ISR позначаємо IRAM_ATTR
    unsigned long t = millis();           // millis() читає апаратний таймер — у ISR можна
    portENTER_CRITICAL_ISR(&mux);
    if (t - lastHit > WINDOW) {
        lastHit = t;
        count++;
        ready = true;
    }
    portEXIT_CRITICAL_ISR(&mux);
}

void setup() {
    pinMode(SOUND, INPUT);
    pinMode(LED, OUTPUT);
    Serial.begin(115200);
    attachInterrupt(digitalPinToInterrupt(SOUND), onSound, FALLING);
    Serial.println("готово. плесніть у долоні.");
}

void loop() {
    bool got = false;
    unsigned long c = 0;
    portENTER_CRITICAL(&mux);             // акуратно знімаємо спільні дані
    if (ready) { ready = false; got = true; c = count; }
    portEXIT_CRITICAL(&mux);

    if (got) {
        digitalWrite(LED, HIGH);
        Serial.print("плеск #");
        Serial.println(c);
        delay(30);
        digitalWrite(LED, LOW);
    }
}
