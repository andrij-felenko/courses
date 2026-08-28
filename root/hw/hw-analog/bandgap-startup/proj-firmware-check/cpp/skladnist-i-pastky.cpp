// Періодична переперевірка опори ВЖЕ під час роботи (напр., раз на секунду
// з основного циклу або таймера): brown-out міг убити опору непомітно.
void reference_watchdog_tick(void)
{
    uint16_t code = witness_average();
    if (!witness_in_window(code)) {
        // Опора впала вже в робочому режимі — реагуємо як на свіжу відмову.
        fault_latch(FAULT_VREF_DEAD);
        system_reset();        // або enter_degraded_mode() — за політикою приладу
    }
}
