// Прямий біт-бенгінг на платформі Arduino
const int PIN_SCLK = 13;
const int PIN_MOSI = 11;
const int PIN_MISO = 12;
const int PIN_CS   = 10;

enum class SpiBbMode : uint8_t { Mode0 = 0, Mode1 = 1, Mode2 = 2, Mode3 = 3 };
SpiBbMode active_mode = SpiBbMode::Mode0;

void spi_bb_setup(SpiBbMode mode) {
    active_mode = mode;
    pinMode(PIN_SCLK, OUTPUT);
    pinMode(PIN_MOSI, OUTPUT);
    pinMode(PIN_MISO, INPUT);
    pinMode(PIN_CS, OUTPUT);

    digitalWrite(PIN_CS, HIGH);
    bool cpol = (active_mode == SpiBbMode::Mode2 || active_mode == SpiBbMode::Mode3);
    digitalWrite(PIN_SCLK, cpol ? HIGH : LOW);
}

uint8_t spi_bb_transfer(uint8_t byte_out) {
    bool cpol = (active_mode == SpiBbMode::Mode2 || active_mode == SpiBbMode::Mode3);
    bool cpha = (active_mode == SpiBbMode::Mode1 || active_mode == SpiBbMode::Mode3);
    uint8_t byte_in = 0;

    for (int8_t bit = 7; bit >= 0; --bit) {
        bool bit_val = bitRead(byte_out, bit);

        if (!cpha) {
            digitalWrite(PIN_MOSI, bit_val ? HIGH : LOW);
            delayMicroseconds(1);
            digitalWrite(PIN_SCLK, cpol ? LOW : HIGH); // 1-й фронт
            delayMicroseconds(1);
            if (digitalRead(PIN_MISO)) bitSet(byte_in, bit);
            digitalWrite(PIN_SCLK, cpol ? HIGH : LOW); // 2-й фронт
        } else {
            digitalWrite(PIN_SCLK, cpol ? LOW : HIGH); // 1-й фронт
            digitalWrite(PIN_MOSI, bit_val ? HIGH : LOW);
            delayMicroseconds(1);
            digitalWrite(PIN_SCLK, cpol ? HIGH : LOW); // 2-й фронт
            delayMicroseconds(1);
            if (digitalRead(PIN_MISO)) bitSet(byte_in, bit);
        }
    }
    return byte_in;
}
