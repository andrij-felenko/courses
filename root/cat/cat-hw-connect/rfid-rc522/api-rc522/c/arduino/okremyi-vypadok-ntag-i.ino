// Читання NTAG/Ultralight: сторінки по 4 байти, БЕЗ автентифікації.
// MIFARE_Read віддає 4 сторінки за раз (16 байтів у 18-байтовий буфер).
bool readNtagPage(byte page) {
  byte buffer[18];
  byte size = sizeof(buffer);

  // Ніякого PCD_Authenticate — базове читання NTAG відкрите.
  MFRC522::StatusCode st = reader.MIFARE_Read(page, buffer, &size);
  if (st != MFRC522::STATUS_OK) {
    Serial.print(F("NTAG read провалився: "));
    Serial.println(reader.GetStatusCodeName(st));
    return false;
  }

  // buffer[0..15] = сторінки page, page+1, page+2, page+3 (по 4 байти)
  for (byte p = 0; p < 4; p++) {
    Serial.print(F("Сторінка "));
    Serial.print(page + p);
    Serial.print(F(":"));
    for (byte i = 0; i < 4; i++) {
      byte v = buffer[p * 4 + i];
      Serial.print(v < 0x10 ? " 0" : " ");
      Serial.print(v, HEX);
    }
    Serial.println();
  }
  return true;
}
