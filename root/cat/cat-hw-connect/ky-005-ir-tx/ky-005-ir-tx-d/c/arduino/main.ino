#include <IRremote.hpp>

const int PIN_SEND = 3;      // вивід, на якому висить S (через резистор)

void setup() {
    IrSender.begin(PIN_SEND);          // бібліотека сама налаштує таймер під 38 кГц
}

void loop() {
    uint16_t address = 0x00;           // адреса пристрою
    uint8_t  command = 0x34;           // код команди (яку «кнопку» шлемо)
    IrSender.sendNEC(address, command, 0);   // 0 — без повторів
    delay(1000);
}
