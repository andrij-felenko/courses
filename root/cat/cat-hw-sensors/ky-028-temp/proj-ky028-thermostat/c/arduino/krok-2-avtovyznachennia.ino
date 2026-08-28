const uint8_t DO_PIN = 2;

int  restLevel = HIGH;     // рівень DO у спокої — визначимо на старті
bool wasHot    = false;    // попередній стан, щоб ловити саме ПЕРЕХІД

// Прочитати «спокій»: кілька замірів, повернути найчастіший рівень.
int readRestLevel() {
    int highs = 0;
    const int N = 15;
    for (int i = 0; i < N; i++) {
        if (digitalRead(DO_PIN) == HIGH) highs++;
        delay(5);
    }
    return (highs > N / 2) ? HIGH : LOW;   // більшість голосів
}

void setup() {
    pinMode(DO_PIN, INPUT);
    Serial.begin(9600);

    delay(300);                        // дати модулю усталитися після живлення
    restLevel = readRestLevel();       // ВАЖЛИВО: тут температура має бути в НОРМІ
    Serial.print("Спокій DO = ");
    Serial.println(restLevel == HIGH ? "HIGH (гаряче буде LOW)"
                                     : "LOW (гаряче буде HIGH)");
}

// «Гаряче» = стан, протилежний до виміряного спокою — полярність-незалежно.
bool isHot() {
    return digitalRead(DO_PIN) != restLevel;
}

void loop() {
    bool hot = isHot();
    if (hot != wasHot) {                               // друкуємо лише перехід
        Serial.println(hot ? ">> перетнуло поріг: ГАРЯЧЕ"
                           : "<< нижче порогу: норма");
        wasHot = hot;
    }
    delay(20);
}
