// Те саме на HAL: захоплення таймера дало масив тривалостей у мікросекундах,
// декодер їх не впізнав — друкуємо як є, парні позиції це мітки.
if (!nec_decode(dur, n_dur, &addr, &cmd)) {
    char line[48];
    int k = snprintf(line, sizeof line, "протокол не впізнано, інтервалів: %u\r\n", n_dur);
    HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);
    for (uint16_t i = 0; i < n_dur; i++) {
        k = snprintf(line, sizeof line, "%s%u\r\n",
                     (i & 1) ? "  пробіл " : "  мітка  ", dur[i]);
        HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);
    }
}
