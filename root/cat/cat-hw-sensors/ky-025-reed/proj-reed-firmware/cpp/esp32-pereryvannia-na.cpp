const uint8_t REED = 4;          // D0 на GPIO4 (майже будь-яка нога годиться)
const int     ACTIVE = LOW;

const uint32_t DEBOUNCE_MS = 30;

volatile uint32_t counter    = 0;
volatile uint32_t t_last_isr = 0;

// На ESP32 ISR має лежати в IRAM → атрибут IRAM_ATTR обов'язковий.
void IRAM_ATTR on_reed() {
    uint32_t now = millis();
    if (now - t_last_isr >= DEBOUNCE_MS) {
        t_last_isr = now;
        counter++;
    }
}

void setup() {
    pinMode(REED, INPUT_PULLUP);   // у KY-025 підтяжка є на платі; для голого геркона — своя
    Serial.begin(115200);
    // Активний LOW → магніт дає спад → FALLING:
    attachInterrupt(digitalPinToInterrupt(REED), on_reed, FALLING);
    Serial.println("ESP32: переривання на герконі увімкнено.");
}

uint32_t shown = 0;

void loop() {
    if (counter != shown) {
        shown = counter;
        Serial.printf("подій: %u\n", shown);
    }
    // основний код вільний; наприклад, тут може крутитися Wi-Fi / дисплей
}
