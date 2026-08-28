#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN   5     // «SDA» на платі — це chip-select (SS/CS)
#define RST_PIN  4

MFRC522 reader(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(115200);
  SPI.begin();                 // піднімаємо апаратний SPI хоста
  reader.PCD_Init();           // ініціалізуємо чип MFRC522
  Serial.println(F("Піднесіть мітку..."));
}

void loop() {
  // 1. Чи з'явилась нова мітка? (швидка REQA-перевірка)
  if (!reader.PICC_IsNewCardPresent()) return;

  // 2. Провести антиколізію й прочитати UID у reader.uid
  if (!reader.PICC_ReadCardSerial()) return;

  // 3. UID тепер у reader.uid.uidByte[0 .. reader.uid.size-1]
  Serial.print(F("UID:"));
  for (byte i = 0; i < reader.uid.size; i++) {
    Serial.print(reader.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(reader.uid.uidByte[i], HEX);
  }
  Serial.println();

  // 4. Заодно — що це за тип мітки (Classic 1K? Ultralight? NTAG?)
  MFRC522::PICC_Type type = reader.PICC_GetType(reader.uid.sak);
  Serial.print(F("Тип: "));
  Serial.println(reader.PICC_GetTypeName(type));

  // 5. ВІДПУСТИТИ мітку — інакше читатимемо її без кінця
  reader.PICC_HaltA();
}
