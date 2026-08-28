const uint8_t SOUND = 2;
const unsigned long WINDOW = 150;
volatile unsigned long lastHit = 0;
volatile unsigned long count   = 0;
volatile bool ready = false;

void onSound() {                          // ISR
    unsigned long t = millis();           // millis() у ISR на AVR читати можна
    if (t - lastHit > WINDOW) {           // дебаунс прямо в перериванні
        lastHit = t;
        count++;
        ready = true;
    }
}

void setup() {
    pinMode(SOUND, INPUT);
    attachInterrupt(digitalPinToInterrupt(SOUND), onSound, FALLING);
    Serial.begin(9600);
}

void loop() {
    if (ready) {
        ready = false;
        Serial.print("плеск #");
        Serial.println(count);            // друкуємо вже поза ISR
    }
}
