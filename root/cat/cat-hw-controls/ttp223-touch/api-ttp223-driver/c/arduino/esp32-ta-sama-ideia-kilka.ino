const uint8_t PIN_TOUCH = 4;                  // звичайний GPIO, не strapping-нога

volatile uint32_t touchCount = 0;
volatile bool     touchFlag  = false;

// На ESP32 ISR має лежати в IRAM → атрибут IRAM_ATTR обов'язковий
void IRAM_ATTR onTouch() {
    touchCount++;
    touchFlag = true;
}

void setup() {
    pinMode(PIN_TOUCH, INPUT);                // двотактний вихід → без підтяжки
    attachInterrupt(PIN_TOUCH, onTouch, RISING);   // RISING = активний у 1
    Serial.begin(115200);
}

void loop() {
    if (touchFlag) {
        touchFlag = false;
        Serial.printf("дотиків: %u\n", touchCount);
    }
    // тут ESP32 може займатися Wi-Fi, сном чи будь-чим — дотик прийде перериванням
}
