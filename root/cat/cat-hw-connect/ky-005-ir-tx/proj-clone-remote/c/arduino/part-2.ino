#include <IRremote.hpp>

void setup() {
    IrSender.begin(3);   // KY-005 через резистор на виводі 3
}

void loop() {
    // рядки, які нам надрукував printIRSendUsage — просто вставлені сюди:
    IrSender.sendNEC(0xF1, 0x76, 0);   // «гучність +», зняте з рідного пульта
    delay(2000);
    IrSender.sendNEC(0xF1, 0x77, 0);   // «гучність −»
    delay(2000);
}
