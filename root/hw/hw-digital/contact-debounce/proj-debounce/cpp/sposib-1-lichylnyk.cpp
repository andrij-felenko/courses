// Викликати рівно раз на тік (напр. кожну 1 мс із таймера).
#define BTN_PIN 4
#define N       5            // скільки однакових відліків = «стабільно»

static uint8_t cnt = 0;      // лічильник однакових відліків
static int prev = HIGH;      // що читали минулого тіку
static int stable = HIGH;    // останній прийнятий стабільний рівень

void debounce_tick(void) {
    int s = digitalRead(BTN_PIN);
    cnt = (s == prev) ? (cnt + 1) : 0;   // той самий — рахуємо, інакше — скид
    prev = s;
    if (cnt >= N && s != stable) {       // рівень устояв і він НОВИЙ
        stable = s;
        if (s == LOW) on_press();        // фронт «відпущено → натиснуто»
    }
}
