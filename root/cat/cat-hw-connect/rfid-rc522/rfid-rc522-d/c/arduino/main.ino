#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN   5     // «SDA» на платі — це chip-select
#define RST_PIN  4

MFRC522 reader(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin();                 // піднімаємо апаратний SPI
  reader.PCD_Init();           // ініціалізуємо чип MFRC522
}

void loop() {
  // чи є нова мітка в полі?
  if (!reader.PICC_IsNewCardPresent()) return;
  // чи вдалося прочитати її UID?
  if (!reader.PICC_ReadCardSerial()) return;

  Serial.print("UID:");
  for (byte i = 0; i < reader.uid.size; i++) {
    Serial.print(reader.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(reader.uid.uidByte[i], HEX);   // друкуємо номер картки
  }
  Serial.println();

  reader.PICC_HaltA();         // відпускаємо мітку, щоб не читати без кінця
}
