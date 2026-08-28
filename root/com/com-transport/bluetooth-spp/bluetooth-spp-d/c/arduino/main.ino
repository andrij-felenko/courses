#include "BluetoothSerial.h"
BluetoothSerial SerialBT;                          // об'єкт «бездротового UART»

void setup() {
  SerialBT.begin("ESP32-robot");                   // піднімає SPP під цим іменем у списку Bluetooth
}

void loop() {
  if (SerialBT.available()) {                       // є вхідний байт? — точно як Serial
    char c = SerialBT.read();                       // прочитати один символ
    SerialBT.write((uint8_t)c);                     // і відправити його назад (ехо)
  }
}
