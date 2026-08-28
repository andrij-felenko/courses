// Лічимо зриви FLT у ковзному вікні; якщо їх забагато — аварія стійка.
static int  fault_hits    = 0;
static bool prev_fault    = false;

// Кличемо, приміром, кожні 10 мс із таймера.
bool efuse_persistent_fault(void) {
    bool now = efuse_fault();
    if (now && !prev_fault) fault_hits++;   // рахуємо ФРОНТ у зрив, не рівень
    prev_fault = now;

    // за 3 с (300 викликів по 10 мс) більш ніж 5 зривів — стійка аварія
    static int window = 0;
    if (++window >= 300) {
        bool persistent = (fault_hits > 5);
        window = 0; fault_hits = 0;         // почати нове вікно
        return persistent;
    }
    return false;
}
