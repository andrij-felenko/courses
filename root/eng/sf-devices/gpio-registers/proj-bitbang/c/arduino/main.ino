#define PIN_DATA  23
#define PIN_CLK   18

void send_byte_slow(uint8_t b) {        // старший біт першим
    for (int i = 7; i >= 0; i--) {
        digitalWrite(PIN_DATA, (b >> i) & 1);  // виставити поточний біт
        digitalWrite(PIN_CLK, HIGH);           // наростальний фронт — приймач читає
        digitalWrite(PIN_CLK, LOW);
    }
}
