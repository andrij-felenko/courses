const uint8_t PIN_DIN  = 11;   // дані в MAX7219
const uint8_t PIN_CLK  = 13;   // такт
const uint8_t PIN_LOAD = 10;   // завантаження (CS)

// Надіслати один 16-бітний кадр: адреса реєстра + байт даних.
void max7219send(uint8_t addr, uint8_t data) {
    uint16_t frame16 = ((uint16_t)addr << 8) | data;   // старший байт = адреса
    digitalWrite(PIN_LOAD, LOW);                        // почали кадр
    for (int8_t i = 15; i >= 0; i--) {                  // старшим бітом уперед
        digitalWrite(PIN_CLK, LOW);
        digitalWrite(PIN_DIN, (frame16 >> i) & 1);      // виставити біт
        digitalWrite(PIN_CLK, HIGH);                    // фронт CLK → чип зчитав біт
    }
    digitalWrite(PIN_LOAD, HIGH);                       // фронт LOAD → клацнути в реєстр
}
