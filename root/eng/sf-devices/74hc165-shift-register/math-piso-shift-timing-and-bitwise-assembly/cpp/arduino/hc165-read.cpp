uint8_t hc165_read(void) {
    uint8_t data = 0;
    
    // Імпульс защіпки
    digitalWrite(LATCH_PIN, LOW);
    delayMicroseconds(1);
    digitalWrite(LATCH_PIN, HIGH);
    
    // Зчитування 8 біт
    for (int i = 0; i < 8; i++) {
        data <<= 1;
        if (digitalRead(DATA_PIN) == HIGH) {
            data |= 1;
        }
        
        // Тактовий імпульс
        digitalWrite(CLOCK_PIN, HIGH);
        digitalWrite(CLOCK_PIN, LOW);
    }
    
    return data;
}
