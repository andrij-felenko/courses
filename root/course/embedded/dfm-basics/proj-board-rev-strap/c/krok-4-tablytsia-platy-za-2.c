static board_config_t g_board;   // конфігурація ЦІЄЇ плати — на весь сеанс

// Визначити ревізію й обрати конфігурацію. Викликати рано на старті,
// але вже після HAL_Init (для HAL_Delay) — і до ініціалізації давачів.
void board_identify(void) {
    rev_straps_init();                       // піни-входи без підтяжки
    rev_straps_settle();                     // дати живленню встоятися

    uint8_t rev = read_board_revision();     // зчитати номер (0…7)

    if (rev >= BOARD_TABLE_LEN) {
        // Прочитали номер, якого в таблиці немає, — НЕ вгадуємо навмання.
        // Безпечно відкотитися до відомої ревізії й голосно про це сказати.
        // (Це, найімовірніше, ознака апаратної біди — див. пастки нижче.)
        rev = 1;
    }

    g_board = BOARD_TABLE[rev];              // взяли рядок своєї ревізії

    // Далі решта прошивки спирається на g_board, а не на #ifdef:
    baro_driver_select(g_board.baro);        // ставимо драйвер потрібного барометра
    servo_attach(g_board.servo_port, g_board.servo_pin);  // кермо на правильний пін
    // log_printf("board: %s\n", g_board.name);
}
