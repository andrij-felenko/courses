// Перекласти вісім стовпців (colBuf) у вісім рядків (frame): транспозиція 8×8.
void columnsToRows() {
    for (uint8_t r = 0; r < 8; r++) {
        uint8_t rowBits = 0;
        for (uint8_t c = 0; c < 8; c++) {
            if (colBuf[c] & (1 << r))       // цятка (рядок r, стовпець c) горить?
                rowBits |= (1 << c);        // тоді ставимо біт c у рядку r
        }
        frame[r] = rowBits;
    }
}

void loop() {
    static uint16_t offset = 0;
    uint16_t total = strlen(message) * 8;   // повна довжина стрічки в стовпцях

    renderWindow(offset);     // порахувати вісім видимих стовпців
    columnsToRows();          // перекласти на рядки для виводу
    max7219show();            // показати (для прямого способу — нічого, крутить таймер)

    offset++;
    if (offset >= total) offset = 0;   // добіг кінця — почати спочатку

    delay(90);                // швидкість бігу: більше число — повільніше
}
