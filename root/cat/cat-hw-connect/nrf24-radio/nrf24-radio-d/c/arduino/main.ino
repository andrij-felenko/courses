#include <SPI.h>
#include <RF24.h>          // бібліотека nRF24/RF24

// два вільні виводи: CE та CSN. SCK/MOSI/MISO бере апаратний SPI сам.
RF24 radio(9, 8);          // (CE, CSN)

const uint8_t address[6] = "node1";   // 5-байтова адреса «труби»

void setup() {
  radio.begin();                 // піднімає SPI й перевіряє чип
  radio.setPALevel(RF24_PA_LOW); // потужність: LOW на столі, HIGH — на дальність
  radio.setDataRate(RF24_250KBPS); // 250 кбіт/с — найдальше й найнадійніше
  radio.setChannel(76);          // канал (0…125); має збігатися на обох кінцях!
  radio.openWritingPipe(address);
  radio.stopListening();         // режим передавача
}

void loop() {
  const char msg[] = "hello";
  bool ok = radio.write(&msg, sizeof(msg));  // блокує, доки не буде ACK або крах спроб
  // ok == true  → приймач підтвердив прийом (авто-ACK)
  // ok == false → 15 спроб вичерпано: далеко, не той канал/адреса, нема живлення
  delay(1000);
}
