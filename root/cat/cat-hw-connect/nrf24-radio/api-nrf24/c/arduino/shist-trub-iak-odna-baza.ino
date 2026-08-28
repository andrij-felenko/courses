#include <SPI.h>
#include <RF24.h>

RF24 radio(9, 8);

// Труба 1 — повна адреса. Труби 2 і 4 різняться від неї ЛИШЕ останнім байтом.
const uint8_t addr1[5] = { 0xC2, 0xC2, 0xC2, 0xC2, 0xC2 };  // повна
const uint8_t addr2[5] = { 0xC2, 0xC2, 0xC2, 0xC2, 0xC3 };  // тільки .C3 «свій»
const uint8_t addr4[5] = { 0xC2, 0xC2, 0xC2, 0xC2, 0xC5 };  // тільки .C5 «свій»

void setup() {
  Serial.begin(115200);
  if (!radio.begin()) { Serial.println(F("nRF24 нема")); while (true) {} }

  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_250KBPS);
  radio.setChannel(76);

  radio.openReadingPipe(1, addr1);      // спершу труба 1 — вона задає старші 4 байти
  radio.openReadingPipe(2, addr2);      // труба 2: успадкує C2 C2 C2 C2, свій байт .C3
  radio.openReadingPipe(4, addr4);      // труба 4: успадкує ті ж 4 байти, свій байт .C5
  radio.startListening();
}

void loop() {
  uint8_t pipe;                         // сюди чип покладе номер труби, що спрацювала
  if (radio.available(&pipe)) {         // варіант available із номером труби
    char msg[32] = {0};
    radio.read(msg, sizeof(msg));
    Serial.print(F("труба "));
    Serial.print(pipe);                 // від кого саме прийшло
    Serial.print(F(": "));
    Serial.println(msg);
  }
}
