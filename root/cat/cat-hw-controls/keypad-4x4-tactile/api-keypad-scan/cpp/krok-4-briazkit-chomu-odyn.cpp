#include <stdint.h>

#define DEBOUNCE_MS   30        // скільки чекати, поки стан устоявся (типово 20..50)

static uint16_t last_stable = 0;             // остання «устояна» карта натисків
static uint32_t last_change_ms[16] = {0};    // коли востаннє змінилася кожна клавіша

// Опитати клавіатуру з антибрязкотом. У key кладе символ нового натиску (0 = нема).
// Повертає true, якщо цього виклику з'явився свіжий натиск.
static bool keypad_read(char *key)
{
    uint16_t now_bits = keypad_scan_raw();   // сирий стан усіх 16 кнопок
    uint32_t t = millis();
    bool got = false;
    *key = 0;

    for (uint8_t i = 0; i < 16; i++) {
        uint16_t mask = (uint16_t)1 << i;
        bool now_down  = now_bits   & mask;      // зараз натиснута?
        bool was_down  = last_stable & mask;     // була натиснута в устояному стані?

        if (now_down != was_down) {              // стан клавіші змінився
            if (t - last_change_ms[i] >= DEBOUNCE_MS) {
                // зміна протрималась досить довго — вважаємо її СПРАВЖНЬОЮ
                last_change_ms[i] = t;
                if (now_down) {                  // саме натиснення (не відпускання)
                    *key = keypad_char(i / 4, i % 4);   // row = i/4, col = i%4
                    got = true;
                }
                // оновлюємо устояний біт цієї клавіші
                if (now_down) last_stable |=  mask;
                else          last_stable &= ~mask;
            }
            // якщо не витримало паузу — це брязкіт, ігноруємо (устояний стан не чіпаємо)
        }
    }
    return got;
}
