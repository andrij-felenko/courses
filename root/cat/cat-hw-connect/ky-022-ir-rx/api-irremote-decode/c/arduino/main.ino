#include <IRremote.hpp>          // IRremote 4.x

const uint8_t IR_PIN = 2;        // вивід S модуля KY-022 → D2

void setup() {
  Serial.begin(115200);
  IrReceiver.begin(IR_PIN, ENABLE_LED_FEEDBACK);   // старт приймача
}

void loop() {
  if (IrReceiver.decode()) {                        // прийшов і розпізнався кадр?
    Serial.print("протокол: ");
    Serial.print(IrReceiver.getProtocolString());   // напр. "NEC"
    Serial.print("  адреса: 0x");
    Serial.print(IrReceiver.decodedIRData.address, HEX);
    Serial.print("  команда: 0x");
    Serial.println(IrReceiver.decodedIRData.command, HEX);
    IrReceiver.resume();                            // ГОТОВІ приймати наступний
  }
}
