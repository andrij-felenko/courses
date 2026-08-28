#define BTN_PIN 4
#define T_MS    20UL                 // вікно тиші, мс

static int last_raw = HIGH;          // попередній СИРИЙ рівень
static int stable   = HIGH;          // прийнятий стабільний рівень
static unsigned long t_change = 0;   // коли сирий рівень смикнувся востаннє

void debounce_poll(void) {
    int s = digitalRead(BTN_PIN);
    if (s != last_raw) {             // рівень смикнувся — засікли час
        last_raw = s;
        t_change = millis();
    }
    // тиша протягом T і рівень НОВИЙ → це справжня подія
    if (millis() - t_change >= T_MS && s != stable) {
        stable = s;
        if (s == LOW) on_press();
    }
}
