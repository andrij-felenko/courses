uint8_t hc165_read() {
    uint8_t result = 0;
    
    digitalWrite(PIN_SH_LD, LOW);
    digitalWrite(PIN_SH_LD, HIGH);
    
    for (int i = 0; i < 8; i++) {
        uint8_t bit = digitalRead(PIN_QH);
        result |= (bit << (7 - i));
        
        digitalWrite(PIN_CLK, HIGH);
        digitalWrite(PIN_CLK, LOW);
    }
    
    return result;
}
