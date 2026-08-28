#include <stdbool.h>

// Двопозиційний регулятор із гістерезисом.
// Викликати з повільним темпом (напр., раз на секунду) з готовою температурою.
typedef struct {
    float setpoint;    // бажана температура, °C
    float hyst;        // півширина зони нечутливості (гістерезис), °C
    bool  heating;     // поточний стан: гріємо чи ні
} bangbang_t;

void bangbang_init(bangbang_t *b, float setpoint, float hyst) {
    b->setpoint = setpoint;
    b->hyst = hyst;
    b->heating = false;
}

void bangbang_update(bangbang_t *b, float temp) {
    if (b->heating) {
        // Гріємо — вимкнемо лише коли перевалили ВЕРХНІЙ поріг.
        if (temp > b->setpoint + b->hyst) b->heating = false;
    } else {
        // Не гріємо — увімкнемо лише коли впали під НИЖНІЙ поріг.
        if (temp < b->setpoint - b->hyst) b->heating = true;
    }
    thermostat_set_power(b->heating ? 1000 : 0);
}
