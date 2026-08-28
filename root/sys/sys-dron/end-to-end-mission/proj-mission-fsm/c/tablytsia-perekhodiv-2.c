static mission_state_t state = ST_BOOT;

// ЄДИНА функція, що змінює state. Іншого шляху немає — отже, обійти
// таблицю неможливо. Повертає true, якщо перехід відбувся.
static bool mission_transition(mission_state_t to) {
    if (to >= ST_COUNT)        return false;   // за межі enum — брак
    if (!allowed[state][to]) {                 // НЕЛЕГАЛЬНИЙ перехід —
        log_illegal(state, to);                //   не мовчки: лишаємо слід у лозі,
        return false;                          //   бо це майже завжди баг у логіці
    }
    on_state_exit(state);      // прибрати за старим станом (напр. згасити таймери)
    state = to;
    on_state_enter(to);        // ЄДИНЕ місце, де стан ставить свою ЦІЛЬ контуру
    return true;
}
