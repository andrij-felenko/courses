// НЕ РОБІТЬ ТАК — усе нереентерабельне в обробнику
// HAL кличе цей callback із контексту переривання USART
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    char buf[32];
    size_t n = read_line(buf);           // умовно: читаємо рядок
    char *tok = strtok(buf, ",");        // статичний стан! — зітре позицію main()
    int *vals = malloc(n * sizeof(int)); // замок купи newlib! — псує її структури
    printf("got %s\r\n", tok);           // буфер виводу + malloc! — подвійний удар
    // ... три способи тихо зламати систему в одному обробнику
}
