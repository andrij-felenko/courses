// Алгоритм відновлення шини SCCB при блокуванні веденого пристрою
bool sccbBusRecover(uint8_t sclPin, uint8_t sdaPin) {
    pinMode(sclPin, OUTPUT);
    pinMode(sdaPin, INPUT_PULLUP);
    
    // Подача 9 тактових імпульсів для розблокування шини
    for (uint8_t i = 0; i < 9; i++) {
        digitalWrite(sclPin, LOW);
        delayMicroseconds(5);
        digitalWrite(sclPin, HIGH);
        delayMicroseconds(5);
        if (digitalRead(sdaPin) == HIGH) {
            break; // Ведений пристрій відпустив лінію даних
        }
    }
    
    // Формування СТОП-умови на шині
    pinMode(sdaPin, OUTPUT);
    digitalWrite(sdaPin, LOW);
    delayMicroseconds(5);
    digitalWrite(sclPin, HIGH);
    delayMicroseconds(5);
    digitalWrite(sdaPin, HIGH);
    
    // Програмне скидання сенсора через регістр конфігурації 0x12
    return sccbWriteRegister(OV3640_SCCB_ADDR, 0x12, 0x80);
}
