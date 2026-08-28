volatile char line[64];      // спільний сирий буфер (тому volatile)
volatile bool ready = false; // прапорець «рядок готовий»

void IRAM_ATTR onByte() {    // верхня половина — нічого «розумного»
    static uint8_t i = 0;
    char c = (char)readByte();       // лише читання регістра — реентерабельно
    if (c == '\n') {
        line[i] = 0;
        ready = true;                // сигнал нижній половині
        i = 0;
    } else if (i < sizeof(line) - 1) {
        line[i++] = c;               // складаємо байти по одному
    }
    // жодних strtok / malloc / printf — тільки складаємо байти
}

void loop() {                // нижня половина — тут можна ВСЕ
    if (ready) {
        ready = false;
        char tmp[64];
        noInterrupts();
        strncpy(tmp, (const char*)line, sizeof(tmp)); // атомарний знімок буфера
        interrupts();
        char *tok = strtok(tmp, ",");   // strtok — але лише в одному місці!
        Serial.println(tok);            // друк — у loop(), де безпечно
    }
}
