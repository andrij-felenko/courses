void setup() {
    Serial.begin(115200);
    Serial2.begin(9600, SERIAL_8N1, 16, 17);
    delay(30);
    Serial2.print("s5-1#");     // перемкнути модуль у пасивний режим
    delay(30);                  // дати час перетравити й відповісти "ok"
    while (Serial2.available()) Serial2.read();   // прибрати "ok" з буфера
}

// Запитати відстань один раз. Повертає мм або -1.
int tofQuery() {
    while (Serial2.available()) Serial2.read();   // чистимо старе
    Serial2.print("r6#");                         // «дай відстань зараз»

    // Відповідь виду "L=748\r\n" — беремо цифри після '='
    char buf[8]; uint8_t len = 0; bool seenEq = false;
    unsigned long t0 = millis();
    while (millis() - t0 < 100) {                 // ждемо відповідь до 100 мс
        if (!Serial2.available()) continue;
        char c = (char)Serial2.read();
        if (c == '=') { seenEq = true; continue; }
        if (seenEq && c >= '0' && c <= '9') {
            if (len < sizeof(buf) - 1) buf[len++] = c;
        } else if (seenEq && (c == '\r' || c == '\n')) {
            break;                                 // рядок скінчився
        }
    }
    if (len == 0) return -1;
    buf[len] = '\0';
    return atoi(buf);
}
