#include <avr/pgmspace.h>

// Таблиця живе у Flash (простір КОДУ), а не в SRAM (простір ДАНИХ):
const uint8_t sine[4] PROGMEM = { 128, 218, 128, 38 };

uint8_t at(uint8_t i) {
    // Звичайне sine[i] читало б простір ДАНИХ за тією ж адресою — там сміття.
    // pgm_read_byte вмикає окрему «шину коду» й бере байт із Flash:
    return pgm_read_byte(&sine[i]);   // i=1 → 218
}
