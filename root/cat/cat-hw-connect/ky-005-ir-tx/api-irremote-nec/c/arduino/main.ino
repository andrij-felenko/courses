#include <IRremote.hpp>

void setup() {
    IrSender.begin(3);
}

void loop() {
    IrSender.sendNEC(0x00, 0x34, 0);   // адреса 0x00, команда 0x34, 0 повторів
    delay(1000);
}
