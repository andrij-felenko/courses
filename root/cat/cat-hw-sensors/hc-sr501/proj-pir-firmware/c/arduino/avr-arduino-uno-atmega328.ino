#include <avr/sleep.h>
#include <avr/interrupt.h>

const uint8_t PIN_PIR = 2;    // OUT — на ногу з апаратним перериванням (D2)
const uint8_t PIN_LED = 13;

volatile bool motion_flag = false;   // ISR лише піднімає прапорець

void on_motion() {            // ISR: якнайкоротша, жодного Serial/delay усередині
    motion_flag = true;
}

void setup() {
    pinMode(PIN_PIR, INPUT);
    pinMode(PIN_LED, OUTPUT);
    Serial.begin(9600);
    delay(60000);             // разовий прогрів давача перед роботою
    Serial.println("Готовий. Засинаю до руху.");
}

void go_to_sleep() {
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);       // найглибший сон AVR
    sleep_enable();
    // Повісити переривання на передній фронт OUT, яке розбудить ядро:
    attachInterrupt(digitalPinToInterrupt(PIN_PIR), on_motion, RISING);
    sleep_cpu();                               // ← ядро засинає рівно тут

    // --- Прокинулися: виконання продовжиться з наступного рядка ---
    sleep_disable();
    detachInterrupt(digitalPinToInterrupt(PIN_PIR));
}

void loop() {
    go_to_sleep();            // засинаємо; повертаємось сюди після руху

    if (motion_flag) {
        motion_flag = false;
        Serial.println("Рух! Прокинувся, працюю.");
        digitalWrite(PIN_LED, HIGH);
        delay(300);
        digitalWrite(PIN_LED, LOW);
        // тут — корисна робота, після чого цикл знову приспить МК
    }
}
