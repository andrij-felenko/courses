// ESP32: Serial2 — апаратний UART. Виводи RX2=16, TX2=17 (типові).
// Модуль шле текст на 9600 8N1; його TX іде на RX2 плати.

char    buf[8];          // кільцевий накопичувач цифр (з запасом)
uint8_t len = 0;         // скільки цифр уже зібрано
int     lastDistance = -1;

void setup() {
    Serial.begin(115200);                        // порт у комп'ютер (монітор)
    Serial2.begin(9600, SERIAL_8N1, 16, 17);     // порт до давача: 9600!
}

void loop() {
    while (Serial2.available()) {
        char c = (char)Serial2.read();

        if (c >= '0' && c <= '9') {              // цифра — накопичуємо
            if (len < sizeof(buf) - 1)
                buf[len++] = c;
        }
        else if (c == '\n') {                    // кінець рядка — рядок готовий
            if (len > 0) {
                buf[len] = '\0';                 // завершуємо С-рядок
                lastDistance = atoi(buf);        // текст → число
                len = 0;                         // буфер під наступний рядок
                Serial.print(lastDistance);
                Serial.println(" mm");
            }
        }
        else {
            // 'm', '\r', пробіл, будь-що інше — ігноруємо; довжину не чіпаємо
        }
    }
}
