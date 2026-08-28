// Прийом NMEA на Arduino: збираємо рядок до '\n', потім розбираємо.
// Модуль BE-182 → Serial1 (TX модуля на RX1 плати), швидкість 38400.
char buf[100];
uint8_t len = 0;

void setup() {
    Serial.begin(115200);      // консоль у комп'ютер
    Serial1.begin(38400);      // BE-182 — саме 38400 за замовчуванням!
}

void loop() {
    while (Serial1.available()) {
        char c = Serial1.read();
        if (c == '\n') {                       // кінець рядка — розбираємо
            buf[len] = '\0';
            gga_t g;
            char copy[100];
            strncpy(copy, buf, sizeof copy);   // копія: parse_gga псує рядок
            if (parse_gga(copy, &g)) {
                Serial.print("lat="); Serial.print(g.lat, 6);
                Serial.print(" lon="); Serial.print(g.lon, 6);
                Serial.print(" sats="); Serial.println(g.sats);
            }
            len = 0;                           // почати новий рядок
        } else if (c != '\r' && len < sizeof(buf) - 1) {
            buf[len++] = c;                    // накопичувати (крім '\r')
        } else if (len >= sizeof(buf) - 1) {
            len = 0;                           // рядок задовгий — скинути буфер
        }
    }
}
