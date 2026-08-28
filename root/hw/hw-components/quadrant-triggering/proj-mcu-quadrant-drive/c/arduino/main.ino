/* Arduino / ATmega328P / RP2040: Негативний затворний драйв */
const int PIN_ZERO_CROSS = 2;
const int PIN_TRIAC_GATE = 3;

volatile unsigned int delay_us = 6000; // Регулювання від 500 до 9500 мкс

void IRAM_ATTR zeroCrossInterrupt() {
    // Чекаємо заданого фазового кута
    delayMicroseconds(delay_us);
    
    // Формуємо серію з 10 імпульсів негативної полярності
    for (int i = 0; i < 10; i++) {
        digitalWrite(PIN_TRIAC_GATE, LOW);  // Вмикаємо затвор (Q-II / Q-III)
        delayMicroseconds(10);
        digitalWrite(PIN_TRIAC_GATE, HIGH); // Вимикаємо затвор
        delayMicroseconds(30);
    }
}

void setup() {
    pinMode(PIN_TRIAC_GATE, OUTPUT);
    digitalWrite(PIN_TRIAC_GATE, HIGH); // Вимкнено за замовчуванням (V_G = VCC)
    
    pinMode(PIN_ZERO_CROSS, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_ZERO_CROSS), zeroCrossInterrupt, RISING);
}

void loop() {
    // Фонова логіка оновлення яскравості чи швидкості
}
