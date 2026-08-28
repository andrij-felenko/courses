// Записати 16 байтів у блок 4. Спершу — та сама автентифікація.
MFRC522::MIFARE_Key key;
for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;

byte block = 4;

// Дані на запис — РІВНО 16 байтів. Тут: рядок-мітка + число балансу.
byte data[16] = {
  'B','A','L', 0x00,                 // сигнатура «BAL» + роздільник
  0x00, 0x00, 0x27, 0x10,            // баланс = 0x2710 = 10000 (напр. копійок)
  0x00, 0x00, 0x00, 0x00,            // решта — про запас, нулі
  0x00, 0x00, 0x00, 0x00
};

MFRC522::StatusCode st = reader.PCD_Authenticate(
    MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(reader.uid));
if (st != MFRC522::STATUS_OK) {
  Serial.print(F("Авт. перед записом не вдалась: "));
  Serial.println(reader.GetStatusCodeName(st));
  reader.PICC_HaltA(); reader.PCD_StopCrypto1();
  return;
}

// Запис: РІВНО 16 байтів, розмір передаємо 16 (не 18 — CRC тут додає бібліотека сама)
st = reader.MIFARE_Write(block, data, 16);
if (st == MFRC522::STATUS_OK) {
  Serial.println(F("Записано."));
} else {
  Serial.print(F("Запис не вдався: "));
  Serial.println(reader.GetStatusCodeName(st));   // напр. NACK, якщо ключ дозволяє лише читання
}

reader.PICC_HaltA();
reader.PCD_StopCrypto1();
