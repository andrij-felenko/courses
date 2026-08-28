#include <SPI.h>
#include <RF24.h>

// Два вільні цифрові виводи: (CE, CSN). SCK/MOSI/MISO бере апаратний SPI сам.
RF24 radio(9, 8);                       // CE=9, CSN=8 (типово для AVR/Uno)

// Адреса «труби» — 5 байтів. Пишемо байтовим масивом, а не рядком:
// так видно, що це саме п'ять байтів, і немає плутанини з нуль-термінатором.
const uint8_t addr[5] = { 0xE7, 0xE7, 0xE7, 0xE7, 0xE7 };

void setup() {
  Serial.begin(115200);

  if (!radio.begin()) {                 // піднімає SPI й перевіряє звʼязок із чипом
    Serial.println(F("nRF24 не відповідає — перевір живлення й розводку SPI"));
    while (true) {}                      // далі йти немає сенсу
  }

  radio.setPALevel(RF24_PA_LOW);        // потужність: LOW на столі, HIGH/MAX на дальність
  radio.setDataRate(RF24_250KBPS);      // 250 кбіт/с — найдальше й найнадійніше
  radio.setChannel(76);                 // канал 0..125; МУСИТЬ збігатися з приймачем
  radio.openWritingPipe(addr);          // куди пишемо
  radio.stopListening();                // режим передавача
}

void loop() {
  static uint32_t counter = 0;
  char msg[32];
  snprintf(msg, sizeof(msg), "hello %lu", counter++);

  bool ok = radio.write(msg, strlen(msg) + 1);   // + 1, щоб полетів і завершальний \0

  if (ok) Serial.print(F("ACK  "));               // приймач підтвердив прийом
  else    Serial.print(F("нема ACK  "));          // 15 спроб вичерпано
  Serial.println(msg);

  delay(1000);
}
