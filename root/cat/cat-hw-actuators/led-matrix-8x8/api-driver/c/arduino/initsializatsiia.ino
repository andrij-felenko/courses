void setup() {
    for (uint8_t i = 0; i < 8; i++) {
        pinMode(COL_PIN[i], OUTPUT);
        pinMode(ROW_PIN[i], OUTPUT);
        digitalWrite(COL_PIN[i], HIGH);   // стовпець «високий» → цятка темна
        digitalWrite(ROW_PIN[i], LOW);    // ключ закритий → рядок не живиться
    }
    drawSmiley();        // покладемо в буфер щось видиме
    setupScanTimer();    // запускаємо розгортку в перериванні
}
