// Записати 16 байтів у блок і перечитати назад для перевірки.
bool writeAndVerify(byte blockAddr, byte *data16) {
  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;

  // --- Автентифікація (для запису вимагає ключа з правом писати) ---
  MFRC522::StatusCode st = reader.PCD_Authenticate(
      MFRC522::PICC_CMD_MF_AUTH_KEY_A, blockAddr, &key, &(reader.uid));
  if (st != MFRC522::STATUS_OK) return false;

  // --- ЗАПИС: рівно 16 байтів (не 18! CRC додасть сама бібліотека) ---
  st = reader.MIFARE_Write(blockAddr, data16, 16);
  if (st != MFRC522::STATUS_OK) {
    Serial.print(F("Write провалився: "));
    Serial.println(reader.GetStatusCodeName(st));
    return false;
  }
  Serial.println(F("Записано."));

  // --- Перечитуємо назад для впевненості ---
  byte buffer[18];
  byte size = sizeof(buffer);
  st = reader.MIFARE_Read(blockAddr, buffer, &size);
  if (st == MFRC522::STATUS_OK) {
    Serial.print(F("Перечитано:"));
    for (byte i = 0; i < 16; i++) {
      Serial.print(buffer[i] < 0x10 ? " 0" : " ");
      Serial.print(buffer[i], HEX);
    }
    Serial.println();
  }
  return true;
}

void demoWrite() {
  // 16 байтів даних. Пишемо у блок 4 (сектор 1) — НЕ у блок 0 і НЕ у трейлер!
  byte payload[16] = {
    'H','e','l','l','o',' ','R','F','I','D',0,0,0,0,0,0
  };
  writeAndVerify(4, payload);

  // ОБОВ'ЯЗКОВИЙ фінал сесії з міткою:
  reader.PICC_HaltA();         // 1. відпустити мітку (HLTA)
  reader.PCD_StopCrypto1();    // 2. вимкнути шифр на боці зчитувача
}
