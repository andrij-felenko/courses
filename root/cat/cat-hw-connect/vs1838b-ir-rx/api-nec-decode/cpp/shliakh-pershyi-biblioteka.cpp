#include <IRremote.hpp>          // у версії 4.x підключати саме .hpp, і лише в ОДНОМУ файлі

const uint8_t PIN_IR = 2;        // OUT приймача заведено на цифровий вивід 2

void setup() {
    Serial.begin(115200);
    IrReceiver.begin(PIN_IR, ENABLE_LED_FEEDBACK);   // почати приймання; ENABLE_LED_FEEDBACK — блимати вбудованим LED на прийом
    Serial.println(F("Наводь пульт і тисни кнопки..."));
}

void loop() {
    if (IrReceiver.decode()) {                        // прийшов повний кадр?
        // головне — три поля результату:
        Serial.print(F("Протокол: "));
        Serial.print(getProtocolString(IrReceiver.decodedIRData.protocol));   // NEC / SONY / RC5 / UNKNOWN
        Serial.print(F("  адреса=0x"));
        Serial.print(IrReceiver.decodedIRData.address, HEX);
        Serial.print(F("  команда=0x"));
        Serial.println(IrReceiver.decodedIRData.command, HEX);

        IrReceiver.resume();                          // ОБОВ'ЯЗКОВО: звільнити буфер під наступний кадр
    }
}
