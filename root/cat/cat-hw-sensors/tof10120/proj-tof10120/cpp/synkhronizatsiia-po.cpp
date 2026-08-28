// Кладемо цифри в буфер; на кінці рядка віддаємо готове число.
// Повертає >=0, коли надійшло ЦІЛЕ нове число; -1, якщо рядок ще не завершено.
int tofPollUart() {
    static char buf[8];
    static uint8_t len = 0;

    while (Serial1.available()) {          // Serial1 — апаратний порт (див. нижче)
        char c = Serial1.read();

        if (c >= '0' && c <= '9') {        // цифра → накопичуємо
            if (len < sizeof(buf) - 1) buf[len++] = c;
        }
        else if (c == '\n') {              // кінець рядка → число готове
            buf[len] = '\0';
            int mm = (len > 0) ? atoi(buf) : -1;
            len = 0;                        // чистимо буфер під наступне число
            if (mm >= 0) return mm;
        }
        // усе інше ('m', '\r', пробіли, сміття) — просто пропускаємо
    }
    return -1;                              // цілого рядка ще нема
}

void setup() {
    Serial.begin(115200);                  // термінал у ПК
    Serial1.begin(9600);                   // TOF10120: 9600 8N1 (апаратний порт)
}

void loop() {
    int mm = tofPollUart();
    if (mm >= 0) { Serial.print(mm); Serial.println(" мм"); }
    // loop не блокується — тут може крутитися будь-яка інша робота
}
