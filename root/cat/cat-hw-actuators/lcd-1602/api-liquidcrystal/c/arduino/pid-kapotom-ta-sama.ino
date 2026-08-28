void lcdInit() {
    // 0. Налаштувати ніжки на вихід
    pinMode(PIN_RS, OUTPUT); pinMode(PIN_E, OUTPUT);
    pinMode(PIN_D4, OUTPUT); pinMode(PIN_D5, OUTPUT);
    pinMode(PIN_D6, OUTPUT); pinMode(PIN_D7, OUTPUT);
    digitalWrite(PIN_E, LOW);

    delay(50);               // 1. Живлення встоялося: чекаємо ≥ 40 мс після подачі

    // 2. Тричі напівбайт 0011 — надійно завести у 8-бітний режим із будь-якого стану.
    //    Це ще НЕ повні байти: шлемо самі напівбайти, стробом кожен.
    digitalWrite(PIN_RS, LOW);
    putNibble(0x03); pulseE(); delay(5);      // перший раз: пауза > 4.1 мс
    putNibble(0x03); pulseE(); delayMicroseconds(150);  // другий: > 100 мкс
    putNibble(0x03); pulseE(); delayMicroseconds(150);  // третій

    // 3. Тепер напівбайт 0010 — перемкнути у 4-бітний режим.
    putNibble(0x02); pulseE(); delayMicroseconds(150);

    // 4. Звідси — вже ПОВНІ байти (sendByte ріже їх на два напівбайти).
    lcdCommand(0x28);        // Function Set: 4 біти, 2 рядки, шрифт 5×8
    lcdCommand(0x08);        // Display OFF
    lcdCommand(0x01); delay(2);   // Clear Display (довга — пауза ~1.52 мс)
    lcdCommand(0x06);        // Entry Mode: курсор рухається вправо, без зсуву екрана
    lcdCommand(0x0C);        // Display ON, курсор і блимання вимкнені
}
