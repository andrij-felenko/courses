#include <IRremote.hpp>

const int PIN_RECV = 2;   // сюди підключений ІЧ-ПРИЙМАЧ (не передавач!)

void setup() {
    Serial.begin(115200);
    IrReceiver.begin(PIN_RECV, ENABLE_LED_FEEDBACK);   // почати приймання
    Serial.println("Тисни кнопки пульта...");
}

void loop() {
    if (IrReceiver.decode()) {            // прийнято повний кадр?
        IrReceiver.printIRResultShort(&Serial);   // що це було (протокол/адреса/команда)
        IrReceiver.printIRSendUsage(&Serial);     // ГОТОВИЙ рядок, ЯКИМ це переслати
        Serial.println();
        IrReceiver.resume();              // готові ловити наступну кнопку
    }
}
