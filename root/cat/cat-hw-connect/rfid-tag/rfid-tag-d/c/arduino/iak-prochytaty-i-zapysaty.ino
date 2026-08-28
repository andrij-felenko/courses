#include <SPI.h>
#include <MFRC522.h>            // бібліотека miguelbalboa/rfid

#define RST_PIN  9
#define SS_PIN   10

MFRC522 reader(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  reader.PCD_Init();            // ініціалізувати читач по SPI
}

void loop() {
  // чи є нова мітка в полі?
  if (!reader.PICC_IsNewCardPresent()) return;
  // чи прочитався її серійний номер (UID)?
  if (!reader.PICC_ReadCardSerial()) return;

  // UID лежить у reader.uid.uidByte[], довжина — reader.uid.size (4 або 7)
  Serial.print("UID:");
  for (byte i = 0; i < reader.uid.size; i++) {
    Serial.print(reader.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(reader.uid.uidByte[i], HEX);   // друкуємо hex-байти
  }
  Serial.println();

  reader.PICC_HaltA();         // відпустити мітку, щоб не читати її по колу
}
