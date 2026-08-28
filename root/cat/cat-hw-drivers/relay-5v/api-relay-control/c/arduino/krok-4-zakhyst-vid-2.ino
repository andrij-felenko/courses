unsigned long lastSwitch = 0;              // мить минулого РЕАЛЬНОГО перемикання реле
const unsigned long MIN_INTERVAL_MS = 500; // реле не клацає частіше ніж раз на 0.5 с

// Безпечне перемикання: пропустить, лише якщо минув мінімальний інтервал.
// Повертає true, якщо перемикання відбулося.
bool relaySwitch(bool on) {
    if (on == relayState) return false;               // уже в цьому стані — нічого не робимо
    if ((millis() - lastSwitch) < MIN_INTERVAL_MS)    // ще рано перемикати
        return false;
    relayState = on;
    relayWrite(on);
    lastSwitch = millis();
    return true;
}
