const uint8_t PIN_LED = 8;
const uint8_t PIN_BTN = 3;

const unsigned long DEBOUNCE_MS = 30;  // поріг: скільки чекати, поки брязкіт уляжеться

bool     ledOn        = false;         // поточний стан світла (перемикач)
int      btnStable     = HIGH;         // останній «усталений» стан кнопки (відпущена = HIGH)
int      btnLastRead   = HIGH;         // що прочитали минулого разу (для лову зміни)
unsigned long lastEdge = 0;            // мить останнього дрижання на вході

void setup() {
    pinMode(PIN_LED, OUTPUT);
    pinMode(PIN_BTN, INPUT_PULLUP);
}

void loop() {
    int reading = digitalRead(PIN_BTN);

    // помітили будь-яку зміну на вході — це може бути і корисний натиск, і брязкіт.
    // Заводимо годинник наново: чекатимемо, поки вхід ПОСТОЇТЬ незмінним DEBOUNCE_MS.
    if (reading != btnLastRead) {
        lastEdge = millis();
    }

    // якщо від останнього дрижання минуло досить — вхід уже усталився, йому можна вірити
    if (millis() - lastEdge > DEBOUNCE_MS) {
        if (reading != btnStable) {          // усталений стан справді змінився
            btnStable = reading;
            if (btnStable == LOW) {          // саме натиснули (active-low) — момент перемикання
                ledOn = !ledOn;              // перевертаємо світло
                digitalWrite(PIN_LED, ledOn ? HIGH : LOW);
            }
        }
    }

    btnLastRead = reading; // запам'ятали для наступного кола
}
