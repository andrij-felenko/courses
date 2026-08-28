#include <SPI.h>
#include <LoRa.h>          // бібліотека sandeepmistry/arduino-LoRa

#define LORA_NSS   5
#define LORA_RST  14
#define LORA_DIO0  2

void setup() {
  LoRa.setPins(LORA_NSS, LORA_RST, LORA_DIO0);   // які ніжки керують чипом

  // 868E6 для Європи, 915E6 для США, 433E6 — де дозволено.
  // Частоту й SF на ОБОХ кінцях лінії треба виставити ОДНАКОВО.
  if (!LoRa.begin(868E6)) {
    // сюди потрапляємо, якщо чип не відгукнувся по SPI:
    // переплутані MISO/MOSI, не той NSS, нема живлення 3.3 В
    while (true) { /* модуль не знайдено */ }
  }
  LoRa.setSpreadingFactor(9);     // SF7…SF12: більше = далі, але повільніше
  LoRa.setTxPower(17);            // дБм; межа залежить від виходу PA, див. нижче
}

void loop() {
  LoRa.beginPacket();
  LoRa.print("hello");
  LoRa.endPacket();               // блокує, доки чип не передасть (DIO0 ↑)
  delay(5000);
}
