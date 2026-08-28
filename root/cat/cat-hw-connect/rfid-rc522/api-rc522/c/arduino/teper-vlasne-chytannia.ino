// Читаємо блок 4 (перший блок сектора 1) ключем A = FF..FF.
bool readBlock(byte blockAddr) {
  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;   // дефолтний ключ

  // --- КРОК 1: автентифікація сектора, у якому лежить цей блок ---
  // Команда 0x60 = PICC_CMD_MF_AUTH_KEY_A (ключем A).
  MFRC522::StatusCode st = reader.PCD_Authenticate(
      MFRC522::PICC_CMD_MF_AUTH_KEY_A, blockAddr, &key, &(reader.uid));
  if (st != MFRC522::STATUS_OK) {
    Serial.print(F("Auth провалилась: "));
    Serial.println(reader.GetStatusCodeName(st));
    return false;
  }

  // --- КРОК 2: читання 16 байтів у буфер ---
  // УВАГА: буфер має бути 18 байтів (16 даних + 2 CRC), і bufferSize теж 18.
  byte buffer[18];
  byte size = sizeof(buffer);          // = 18
  st = reader.MIFARE_Read(blockAddr, buffer, &size);
  if (st != MFRC522::STATUS_OK) {
    Serial.print(F("Read провалився: "));
    Serial.println(reader.GetStatusCodeName(st));
    return false;
  }

  // Друкуємо перші 16 байтів (17-й і 18-й — CRC, не дані)
  Serial.print(F("Блок "));
  Serial.print(blockAddr);
  Serial.print(F(":"));
  for (byte i = 0; i < 16; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
  Serial.println();
  return true;
}
