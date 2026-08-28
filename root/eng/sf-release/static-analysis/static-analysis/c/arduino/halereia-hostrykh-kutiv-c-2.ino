// (а) правильно: порівняння, не присвоєння
if (digitalRead(2) == HIGH) {
    Serial.println("triggered");
}

// (б) правильно: ширина типу відповідає ширині маски
uint16_t mask16 = (1U << 9);           // 0x200 — влазить у 16 розрядів
Wire.beginTransmission(0x20);
Wire.write(highByte(mask16));
Wire.write(lowByte(mask16));
Wire.endTransmission();

// або якщо потрібен саме uint8_t — біт має влазити (0..7, не 9):
uint8_t mask8 = (1U << 2);             // 0x04 — влазить у uint8_t
