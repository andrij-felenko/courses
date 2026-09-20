#include <Arduino.h>
#include <SPI.h>

class NRF24L01 {
    uint8_t csn_pin;
    uint8_t ce_pin;
public:
    NRF24L01(uint8_t csn, uint8_t ce) : csn_pin(csn), ce_pin(ce) {}
    
    void init() {
        SPI.begin();
        pinMode(csn_pin, OUTPUT);
        digitalWrite(csn_pin, HIGH); // CSN неактивний (високий рівень)
        
        pinMode(ce_pin, OUTPUT);
        digitalWrite(ce_pin, LOW);   // CE неактивний (режим очікування)
    }

    // Читаємо STATUS (регістр 0x07) для діагностики.
    // Навіть відправка пустої команди (NOP, 0xFF) на nRF24L01 одразу повертає стан регістру STATUS.
    uint8_t read_status() {
        uint8_t status;
        
        // nRF24L01 вимагає MSBFIRST і SPI_MODE0
        SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE0));
        
        digitalWrite(csn_pin, LOW);   // Активація модуля (Chip Select Not)
        status = SPI.transfer(0xFF);  // Відправляємо NOP команду (0xFF), отримуємо статус
        digitalWrite(csn_pin, HIGH);  // Деактивація модуля
        
        SPI.endTransaction();
        
        return status;
    }
};

// Піни можуть відрізнятися. Зазвичай для Arduino Uno/Nano:
// CSN = 10, CE = 9. Адаптер живлення підключається до 5V та GND Arduino.
NRF24L01 radio(10, 9); 

void setup() {
    Serial.begin(115200);
    while (!Serial); // Чекаємо на підключення монітора порту (для Leonardo/Micro)
    
    radio.init();
    Serial.println("Початок перевірки nRF24L01 (через адаптер живлення)...");
}

void loop() {
    uint8_t status = radio.read_status();
    
    Serial.print("nRF24L01 STATUS: 0x");
    if (status < 16) Serial.print("0");
    Serial.println(status, HEX);
    
    // Статус 0x0E є дефолтним після включення (RX_P_NO = 111, TX_FULL = 0, MAX_RT = 0, RX_DR = 0, TX_DS = 0).
    // Якщо отримано 0x00 або 0xFF - ймовірно модуль не живиться або помилка в підключенні MISO/MOSI/SCK/CSN.
    if (status == 0x0E) {
        Serial.println("  -> Модуль на зв'язку. Живлення та SPI в нормі.");
    } else if (status == 0x00 || status == 0xFF) {
        Serial.println("  -> Увага! Модуль не відповідає. Перевірте контакти адаптера живлення та SPI шину.");
    }
    
    delay(2000);
}
