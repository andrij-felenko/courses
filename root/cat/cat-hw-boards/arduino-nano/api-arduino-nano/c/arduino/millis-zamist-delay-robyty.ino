const uint8_t PIN_LED = 13;
const uint8_t PIN_BTN = 2;

unsigned long ledLast = 0;      // коли востаннє перемкнули світлодіод
unsigned long msgLast = 0;      // коли востаннє слали повідомлення
bool ledOn = false;

void setup() {
    Serial.begin(9600);
    pinMode(PIN_LED, OUTPUT);
    pinMode(PIN_BTN, INPUT_PULLUP);
}

void loop() {
    unsigned long now = millis();

    // задача 1: блимати раз на секунду, нікого не блокуючи
    if (now - ledLast >= 1000) {
        ledLast = now;
        ledOn = !ledOn;
        digitalWrite(PIN_LED, ledOn ? HIGH : LOW);
    }

    // задача 2: слати число щопівсекунди
    if (now - msgLast >= 500) {
        msgLast = now;
        Serial.println(analogRead(A0));
    }

    // задача 3: кнопка реагує МИТТЄВО — жодного delay її не глушить
    if (digitalRead(PIN_BTN) == LOW) {
        // тут дія на натискання
    }
}
