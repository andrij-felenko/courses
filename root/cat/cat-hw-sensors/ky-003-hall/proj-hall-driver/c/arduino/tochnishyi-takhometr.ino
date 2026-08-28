const uint8_t HALL  = 2;
const uint8_t POLES = 1;          // скільки магнітів на оберт

volatile uint32_t lastEdge   = 0; // час попереднього фронту, мкс
volatile uint32_t period     = 0; // останній виміряний період, мкс
volatile bool     gotPulse   = false;

void onPulse() {
    uint32_t now = micros();      // мітка часу фронту; micros() в ISR на AVR читати можна
    if (lastEdge != 0) {          // перший фронт лише задає початок відліку — періоду ще нема
        period   = now - lastEdge;
        gotPulse = true;
    }
    lastEdge = now;               // інтервал рахуємо від попереднього фронту
}

void setup() {
    pinMode(HALL, INPUT_PULLUP);
    Serial.begin(115200);
    attachInterrupt(digitalPinToInterrupt(HALL), onPulse, FALLING);
}

const uint32_t STOP_US = 2000000; // 2 с без імпульсів → вважаємо, що зупинилось

void loop() {
    noInterrupts();
    uint32_t T    = period;
    uint32_t last = lastEdge;
    bool     fresh = gotPulse;
    gotPulse = false;
    interrupts();

    float rpm;
    if (micros() - last > STOP_US) {
        rpm = 0;                       // давно немає імпульсів — вал стоїть
    } else if (fresh && T > 0) {
        rpm = 60000000.0 / ((float)T * POLES);
    } else {
        return;                        // нового періоду ще нема — нічого не оновлюємо
    }

    Serial.print("RPM: ");
    Serial.println(rpm, 1);
    delay(100);                        // друк не заважає лічбі — імпульси ловить ISR
}
