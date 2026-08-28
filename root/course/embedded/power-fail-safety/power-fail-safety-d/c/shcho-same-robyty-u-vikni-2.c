// Старт після ввімкнення: чи можна довіряти збереженому стану?
void restore_state_on_boot(void)
{
    CriticalState s;
    fram_read(FRAM_STATE_ADDR, (uint8_t *)&s, sizeof s);

    uint16_t crc = crc16((const uint8_t *)&s, offsetof(CriticalState, crc));

    if (s.magic == STATE_MAGIC && crc == s.crc) {
        g_state = s;             // стан цілий — продовжуємо з нього
    } else {
        load_defaults(&g_state); // стан ушкоджений — безпечні значення
    }
}
