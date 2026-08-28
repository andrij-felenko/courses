#include <SPI.h>

const uint8_t PIN_CS = 10;      // вибір пристрою (chip select)

// прочитати один регістр: шлемо адресу, приймаємо відповідь
uint8_t spi_read_reg(uint8_t reg) {
    digitalWrite(PIN_CS, LOW);              // «слухай мене»
    SPI.transfer(reg | 0x80);               // старший біт = «читання» (типово)
    uint8_t value = SPI.transfer(0x00);     // порожній байт — щоб зсунути відповідь
    digitalWrite(PIN_CS, HIGH);             // «все, відпускаю»
    return value;
}

void setup() {
    Serial.begin(9600);
    pinMode(PIN_CS, OUTPUT);
    digitalWrite(PIN_CS, HIGH);             // спокій = не вибрано
    SPI.begin();                            // D13/D11/D12 налаштує сама
    // швидкість, порядок бітів і режим — з даташита пристрою:
    SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
}

void loop() {
    uint8_t id = spi_read_reg(0x0F);        // умовний регістр «хто ти»
    Serial.println(id, HEX);
    delay(500);
}
