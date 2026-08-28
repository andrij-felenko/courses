const uint8_t SOUND = 3;        // DO давача — на цифровий вхід

int idleLevel;                  // рівень, який плата тримає в ТИШІ (визначаємо на старті)

void setup() {
    pinMode(SOUND, INPUT);
    Serial.begin(9600);
    delay(50);                  // дати входу усталитися
    idleLevel = digitalRead(SOUND);   // у тиші — це «спокій» цієї конкретної плати
    Serial.print("Рівень спокою DO = ");
    Serial.println(idleLevel == HIGH ? "HIGH (подія — падіння в LOW)"
                                     : "LOW (подія — зростання в HIGH)");
}

// true — коли DO відійшов від спокою, тобто звук ПЕРЕВИЩИВ поріг.
inline bool isLoud() {
    return digitalRead(SOUND) != idleLevel;
}

void loop() {
    Serial.println(isLoud() ? "гучно" : "тихо");
    delay(100);
}
