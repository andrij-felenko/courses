const uint8_t PIN_BTN = 2;
const uint8_t PIN_LED = 13;

bool lampOn = false;              // стан лампи, що ми перемикаємо
bool lastReading = HIGH;          // попереднє сире читання (у спокої = HIGH)
unsigned long lastChange = 0;     // коли сире читання востаннє змінилось
const unsigned long DEBOUNCE = 25;  // «тиша», мс — довша за брязкіт

void setup() {
    pinMode(PIN_BTN, INPUT_PULLUP);
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    bool reading = digitalRead(PIN_BTN);

    if (reading != lastReading) {   // сире читання смикнулось — запускаємо відлік
        lastChange = millis();
        lastReading = reading;
    }

    // Стан устояв довше за DEBOUNCE і це фронт натиску (перехід у LOW)?
    static bool stable = HIGH;
    if (millis() - lastChange > DEBOUNCE && reading != stable) {
        stable = reading;
        if (stable == LOW) {              // саме натиск (не відпускання)
            lampOn = !lampOn;             // перемикаємо лампу
            digitalWrite(PIN_LED, lampOn ? HIGH : LOW);
        }
    }
}
