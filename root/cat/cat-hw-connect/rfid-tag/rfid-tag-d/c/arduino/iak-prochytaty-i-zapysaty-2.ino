// прочитати блок 4 (перший блок даних сектора 1), ключ A за замовчуванням
MFRC522::MIFARE_Key key;
for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;   // заводський ключ FF·6

byte block = 4;
byte buffer[18];                 // 16 байтів даних + 2 байти контрольної суми
byte size = sizeof(buffer);

// КРОК 1: довести знання ключа A саме для цього сектора
auto st = reader.PCD_Authenticate(
    MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(reader.uid));
if (st != MFRC522::STATUS_OK) {
  Serial.println("Ключ не підійшов — сектор замкнений");
  return;                        // без ключа далі ходу немає
}

// КРОК 2: тепер сектор відкритий — читаємо блок
st = reader.MIFARE_Read(block, buffer, &size);
if (st == MFRC522::STATUS_OK) {
  for (byte i = 0; i < 16; i++) Serial.print(buffer[i], HEX);
  Serial.println();
}
reader.PCD_StopCrypto1();        // ЗАВЖДИ закрити шифрування після роботи
