void configureModule() {
    String resp;

    struct { const char *cmd; const char *what; } steps[] = {
        { "AT",                  "перевірка зв'язку" },
        { "AT+NAME=MyBT",        "ім'я модуля" },
        { "AT+PSWD=4726",        "новий PIN (замість 1234)" },
        { "AT+UART=9600,0,0",    "робоча швидкість 9600, 1 стоп-біт, без парності" },
        { "AT+ROLE=0",           "роль: ведений (slave) — чекає вхідне з'єднання [HC-05]" },
    };

    for (auto &s : steps) {
        bool ok = sendAT(s.cmd, resp);
        Serial.print(s.what);
        Serial.print("  →  ");
        Serial.print(resp);                    // повний текст відповіді модуля
        if (!ok) {
            Serial.println(">>> НЕ OK. Перевір: EN високо? швидкість 38400? \\r\\n?");
            return;                             // далі немає сенсу
        }
    }
    Serial.println("Налаштування завершено. Знеструм і подай живлення без EN.");
}
