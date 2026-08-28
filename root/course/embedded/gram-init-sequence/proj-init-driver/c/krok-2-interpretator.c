// Низькорівневі примітиви платформи — ті самі, що й у статті.
void send_cmd(uint8_t c);                        // D/C = 0, вилити байт-команду
void send_data(const uint8_t *buf, uint32_t n);  // D/C = 1, вилити n байтів даних
void delay_ms(uint32_t ms);                      // блокувальна пауза

// Прокрутити таблицю згори вниз. n — кількість записів.
void run_init_table(const init_cmd_t *tab, uint32_t n) {
    for (uint32_t i = 0; i < n; i++) {
        send_cmd(tab[i].cmd);                     // 1) команда: D/C опускає примітив
        if (tab[i].n_args > 0) {                  // 2) аргументи, якщо є
            send_data(tab[i].args, tab[i].n_args);
        }
        if (tab[i].delay_ms > 0) {                // 3) пауза, якщо крок її вимагає
            delay_ms(tab[i].delay_ms);
        }
    }
}
