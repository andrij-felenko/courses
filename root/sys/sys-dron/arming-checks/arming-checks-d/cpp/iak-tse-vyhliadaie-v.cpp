static bool armed = false;   // за замовчуванням DISARMED — безпечно

// Найнижча ланка: розрахунок сигналу на кожен двигун.
// Хоч би що порахувала логіка керування — у disarmed виходить нуль.
void motors_output(uint16_t thr[NUM_MOTORS]) {
    if (!armed) {
        for (int i = 0; i < NUM_MOTORS; i++)
            esc_write(i, THROTTLE_MIN);   // мертвий вихід, крапка
        return;
    }
    for (int i = 0; i < NUM_MOTORS; i++)
        esc_write(i, thr[i]);             // сюди доходимо ЛИШЕ коли armed
}
