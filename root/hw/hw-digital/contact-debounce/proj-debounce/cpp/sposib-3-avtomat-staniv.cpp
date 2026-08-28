#define BTN_PIN 4
#define T_MS    20UL

enum { STABLE, SUSPECT };
static uint8_t st = STABLE;
static int stable = HIGH;            // підтверджений рівень
static unsigned long t0 = 0;         // коли увійшли в SUSPECT

void debounce_fsm(void) {
    int s = digitalRead(BTN_PIN);
    switch (st) {
    case STABLE:
        if (s != stable) {           // помітили зміну — під підозру
            st = SUSPECT;
            t0 = millis();
        }
        break;
    case SUSPECT:
        if (s == stable) {           // рівень повернувся → хибна тривога
            st = STABLE;
        } else if (millis() - t0 >= T_MS) {  // устояв усе вікно → подія
            stable = s;
            st = STABLE;
            if (s == LOW) on_press();
        }
        break;
    }
}
