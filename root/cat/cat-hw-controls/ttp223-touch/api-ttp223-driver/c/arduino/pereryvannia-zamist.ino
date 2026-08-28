const uint8_t PIN_TOUCH = 2;              // на Uno переривання є на D2 і D3

volatile uint32_t touchCount = 0;         // спільна з ISR → обов'язково volatile
volatile bool     touchFlag  = false;

// Обробник переривання (ISR): максимально короткий, без Serial/delay усередині!
void onTouch() {
    touchCount++;
    touchFlag = true;
}

void setup() {
    pinMode(PIN_TOUCH, INPUT);
    // RISING = передній фронт = активація для активного-в-1
    attachInterrupt(digitalPinToInterrupt(PIN_TOUCH), onTouch, RISING);
    Serial.begin(9600);
}

void loop() {
    if (touchFlag) {                      // прапорець підняв ISR
        touchFlag = false;                // скинули й обробляємо в спокійному циклі
        Serial.print("дотиків: ");
        Serial.println(touchCount);
    }
    // процесор тут вільний: може спати, крутити іншу логіку — реакція прийде сама
}
