void loop() {
  if (!reader.PICC_IsNewCardPresent()) return;
  if (!reader.PICC_ReadCardSerial()) return;

  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;   // пробуємо заводський ключ

  // Повний дамп: UID, SAK, тип чипа й ВЕСЬ вміст (для Classic — усі сектори).
  // PICC_DumpToSerial сам автентифікується цим ключем на кожному секторі.
  reader.PICC_DumpToSerial(&(reader.uid));

  // PICC_DumpToSerial наприкінці САМ кличе HaltA і StopCrypto1 — тут добавляти не треба.
}
