// Прочитати блок 4 (сектор 1, локальний 0) ключем A.
// Новий брелок із заводу має на всіх секторах ключ FF FF FF FF FF FF.
MFRC522::MIFARE_Key key;
for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;   // заводський ключ, 6 байтів FF

byte block  = 4;
byte buffer[18];                 // 16 байтів даних + 2 байти CRC — МУСИТЬ бути 18
byte size   = sizeof(buffer);    // передаємо ЄМНІСТЬ буфера (18), не 16

// КРОК 2: довести знання ключа A саме цього сектора.
// blockAddr тут — будь-який блок сектора; беремо той, що читатимемо.
MFRC522::StatusCode st = reader.PCD_Authenticate(
    MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(reader.uid));
if (st != MFRC522::STATUS_OK) {
  Serial.print(F("Автентифікація не вдалась: "));
  Serial.println(reader.GetStatusCodeName(st));   // читабельна причина
  reader.PICC_HaltA();
  reader.PCD_StopCrypto1();     // навіть після невдачі — опустити шифрування
  return;
}

// КРОК 3: сектор відкрито — читаємо 16 байтів блока
st = reader.MIFARE_Read(block, buffer, &size);
if (st == MFRC522::STATUS_OK) {
  Serial.print(F("Блок "));
  Serial.print(block);
  Serial.print(F(":"));
  for (byte i = 0; i < 16; i++) {          // друкуємо ЛИШЕ 16, не 18
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
  }
  Serial.println();
} else {
  Serial.print(F("Читання не вдалось: "));
  Serial.println(reader.GetStatusCodeName(st));
}

reader.PICC_HaltA();             // відпустити мітку
reader.PCD_StopCrypto1();        // ОБОВ'ЯЗКОВО опустити шифрування
