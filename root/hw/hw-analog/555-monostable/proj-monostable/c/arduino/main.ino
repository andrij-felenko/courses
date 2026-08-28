#define BTN_PIN 2
#define OUT_PIN 3

oneshot_t btn;

void setup(void) {
    pinMode(BTN_PIN, INPUT_PULLUP);   // кнопка замикає вхід на землю
    pinMode(OUT_PIN, OUTPUT);         // сюди виходить чистий імпульс
    oneshot_init(&btn, 30);           // T = 30 мс, трохи довше за брязкіт
}

void loop(void) {
    static bool prev = true;               // рівень входу з попереднього кола
    bool level   = digitalRead(BTN_PIN);   // LOW = натиснуто
    bool falling = prev && !level;         // спад = момент натискання
    prev = level;

    // рівно один імпульс 30 мс на натискання: перший спад запускає ACTIVE,
    // а всі дальші стрибки контакту в ці 30 мс потрапляють у «глуху» зону
    digitalWrite(OUT_PIN, oneshot_poll(&btn, falling, millis()));
}
