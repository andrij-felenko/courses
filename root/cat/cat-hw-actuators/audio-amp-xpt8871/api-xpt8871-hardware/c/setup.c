// Керування живленням XPT8871 та генерація звуку без перехідних клацань
const uint8_t PIN_SHDN  = 4;  // Лінія SHDN підсилювача (HIGH = сон, LOW = робота)
const uint8_t PIN_AUDIO = 9;  // Лінія генерації звукового тону

void setup() {
    pinMode(PIN_SHDN, OUTPUT);
    digitalWrite(PIN_SHDN, HIGH); // Стартуємо в режимі сну зі споживанням < 1 мкА
    pinMode(PIN_AUDIO, OUTPUT);
    digitalWrite(PIN_AUDIO, LOW);
}

// Пробудження мікросхеми з паузою на стабілізацію віртуальної землі
void amplifier_wake() {
    digitalWrite(PIN_SHDN, LOW);  // Вмикаємо внутрішні джерела струму
    delay(50);                    // Чекаємо заряду конденсатора BYPASS
}

// Переведення мікросхеми в енергоощадний сон
void amplifier_sleep() {
    delay(10);                    // Чекаємо затухання коливань на виході
    digitalWrite(PIN_SHDN, HIGH); // Вимикаємо каскади підсилювача
}

// Безпечне відтворення сигналу сповіщення заданої частоти
void play_alert(unsigned int frequency_hz, unsigned long duration_ms) {
    amplifier_wake();                           // 1. Будимо підсилювач і чекаємо 50 мс
    tone(PIN_AUDIO, frequency_hz, duration_ms); // 2. Вмикаємо звук
    delay(duration_ms);                         // 3. Відтворюємо звук потрібний час
    noTone(PIN_AUDIO);                          // 4. Глушимо звукову хвилю
    amplifier_sleep();                          // 5. Витримуємо 10 мс і спимо
}

void loop() {
    play_alert(1000, 300); // Сигнал 1 кГц тривалістю 300 мс
    delay(5000);           // 5 секунд повної тиші в режимі мікроамперного сну
}
