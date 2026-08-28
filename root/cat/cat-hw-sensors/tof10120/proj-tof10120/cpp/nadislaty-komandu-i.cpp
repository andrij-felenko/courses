// Шле команду (напр. "s3-1#") і збирає відповідь модуля до '\n' або тайм-ауту.
// Повертає true, якщо у відповіді трапилось "ok"; текст відповіді кладе в resp.
bool tofCommand(const char *cmd, char *resp, size_t respSize,
                uint32_t timeoutMs = 200) {
    while (Serial1.available()) Serial1.read();   // прибрати недочитаний потік

    Serial1.print(cmd);                            // напр. "s3-1#"

    size_t n = 0;
    uint32_t t0 = millis();
    while (millis() - t0 < timeoutMs) {
        while (Serial1.available()) {
            char c = Serial1.read();
            if (c == '\n' || c == '\r') {          // кінець рядка відповіді
                resp[n] = '\0';
                if (n > 0) return (strstr(resp, "ok") != NULL);
            } else if (n < respSize - 1) {
                resp[n++] = c;
            }
        }
    }
    resp[n] = '\0';
    return false;                                  // модуль не відповів вчасно
}

void applySettings() {
    char resp[16];

    // сира миттєва відстань
    if (tofCommand("s3-1#", resp, sizeof(resp))) Serial.println("режим: сира — ok");
    else Serial.print("режим: збій, відповідь=") , Serial.println(resp);

    // пасивний режим: більше не базікає сам
    tofCommand("s5-1#", resp, sizeof(resp));

    // юстування нуля: якщо модуль стабільно завищує на 5 мм — компенсуємо
    tofCommand("s1-05#", resp, sizeof(resp));

    // тепер відстань беремо на запит
    if (tofCommand("r6#", resp, sizeof(resp)))
        Serial.print("на r6# прийшло: "), Serial.println(resp);  // напр. L=0748
}
