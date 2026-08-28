#include <avr/pgmspace.h>

// PROGMEM — це атрибут "поклади в секцію .progmem", тобто у Flash.
// Компонувальник дасть sine адресу в просторі КОДУ, не даних:
const uint8_t sine[4] PROGMEM = { 128, 218, 128, 38 };

uint8_t at(uint8_t i) {
    // &sine[i] — це адреса у Flash (простір коду), число на кшталт 0x0100.
    // pgm_read_byte розгортається у:
    //   1) покласти цю адресу в регістр Z,
    //   2) виконати LPM Rd, Z — читання з пам'яті програм.
    return pgm_read_byte(&sine[i]);   // i=1 → 218
}
