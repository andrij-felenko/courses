#include <SPI.h>
#include <RF24.h>

RF24 radio(9, 8);                       // CE=9, CSN=8 — ті самі виводи

// ТА САМА адреса, що й у передавача. Один байт розбіжності = вічна тиша.
const uint8_t addr[5] = { 0xE7, 0xE7, 0xE7, 0xE7, 0xE7 };

void setup() {
  Serial.begin(115200);

  if (!radio.begin()) {
    Serial.println(F("nRF24 не відповідає"));
    while (true) {}
  }

  radio.setPALevel(RF24_PA_LOW);        // ті самі налаштування ефіру, що й у передавача
  radio.setDataRate(RF24_250KBPS);
  radio.setChannel(76);
  radio.openReadingPipe(1, addr);       // слухаємо цю адресу на трубі №1
  radio.startListening();               // режим приймача
}

void loop() {
  if (radio.available()) {              // у буфері чипа є пакет?
    char msg[32] = {0};
    radio.read(msg, sizeof(msg));       // забрати його (розмір буфера >= розміру пакета)
    Serial.print(F("прийшло: "));
    Serial.println(msg);
  }
}
