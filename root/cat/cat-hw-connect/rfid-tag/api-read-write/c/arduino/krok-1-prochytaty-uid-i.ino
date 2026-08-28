#include <SPI.h>
#include <MFRC522.h>            // бібліотека miguelbalboa/rfid

#define RST_PIN  9
#define SS_PIN   10             // «SDA» на червоній платі — це chip-select

MFRC522 reader(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin();
  reader.PCD_Init();            // підняти чип MFRC522 по SPI
  Serial.println(F("Піднесіть мітку..."));
}

void loop() {
  // чи є нова мітка в полі? (не крутимо ту саму по колу)
  if (!reader.PICC_IsNewCardPresent()) return;
  // чи прочитався її серійний номер (UID)?
  if (!reader.PICC_ReadCardSerial()) return;

  // --- UID: байти лежать у reader.uid.uidByte[], довжина в reader.uid.size ---
  Serial.print(F("UID ("));
  Serial.print(reader.uid.size);            // 4 або 7
  Serial.print(F(" байт):"));
  for (byte i = 0; i < reader.uid.size; i++) {
    Serial.print(reader.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(reader.uid.uidByte[i], HEX);
  }
  Serial.println();

  // --- тип чипа: розкодувати з SAK (байт reader.uid.sak) ---
  MFRC522::PICC_Type type = reader.PICC_GetType(reader.uid.sak);
  Serial.print(F("Чип: "));
  Serial.println(reader.PICC_GetTypeName(type));   // напр. "MIFARE 1KB"

  reader.PICC_HaltA();         // відпустити мітку
}
