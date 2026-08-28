#define HOLD_MS   1000       // тримати ≈1 c, щоб перемкнути

// Викликається періодично (напр., кожні 10 мс) з відомим dt_ms.
void safety_button_poll(uint32_t dt_ms) {
    static uint32_t held_ms = 0;

    if (safety_button_pressed()) {       // кнопку зараз натиснуто?
        held_ms += dt_ms;
        if (held_ms >= HOLD_MS) {        // дотримали до порога —
            safety_on = !safety_on;      // перемкнути стан безпеки
            held_ms = 0;
            while (safety_button_pressed())   // дочекатись відпускання,
                ;                             // щоб не перемкнути знову
        }
    } else {
        held_ms = 0;                     // відпустили рано — лічильник з нуля
    }
}
