#include <avr/pgmspace.h>

// Таблиця з 256 значень гами — лежить у Flash, а не в SRAM
const uint8_t gamma[256] PROGMEM = {
    0, 0, 0, 0, 0, 1, 1, 1, /* ... ще 248 значень ... */ 255
};

void loop() {
    uint8_t raw = analogRead(A0) >> 2;         // 0…255
    uint8_t corrected = pgm_read_byte(&gamma[raw]);  // читаємо з Flash
    analogWrite(9, corrected);
}
