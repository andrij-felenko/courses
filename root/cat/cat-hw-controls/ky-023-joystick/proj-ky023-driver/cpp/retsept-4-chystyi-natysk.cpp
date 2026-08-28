struct Button {
    uint8_t  pin;
    bool     stable;        // останній сталий (гашений) рівень: true = відпущено
    bool     lastRead;      // останній миттєвий відлік — для лічби вікна
    uint32_t lastChange;    // коли миттєвий рівень востаннє змінився, мс
    bool     pressedEvent;  // виставляється на один цикл у мить натиску
};

const uint32_t DEBOUNCE_MS = 25;

void buttonSetup(Button &b, uint8_t pin) {
    b.pin = pin;
    pinMode(pin, INPUT_PULLUP);         // на модулі підтяжки немає!
    b.stable = b.lastRead = true;       // спокій = HIGH (відпущено)
    b.lastChange = millis();
    b.pressedEvent = false;
}

// Викликати щоцикл. Оновлює стан; pressedEvent — один імпульс на натиск.
void buttonUpdate(Button &b) {
    b.pressedEvent = false;
    bool now = digitalRead(b.pin);      // HIGH = відпущено, LOW = натиснуто

    if (now != b.lastRead) {            // рівень смикнувся — перезапустити вікно
        b.lastChange = millis();
        b.lastRead   = now;
    }

    // рівень протримався сталим досить довго — приймаємо його
    if (millis() - b.lastChange >= DEBOUNCE_MS && now != b.stable) {
        b.stable = now;
        if (b.stable == LOW)            // перехід HIGH→LOW = справжній натиск
            b.pressedEvent = true;
    }
}

bool buttonPressed(Button &b) { return b.pressedEvent; }         // один імпульс
bool buttonHeld(Button &b)    { return b.stable == LOW; }        // тримають зараз
