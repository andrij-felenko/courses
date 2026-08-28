int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();                 /* CLK і RST — виходи; напрям DAT міняємо на льоту */
  MX_USART2_UART_Init();

  HAL_GPIO_WritePin(RST_PORT, RST_PIN, GPIO_PIN_RESET);  /* сеанс закритий */

  ds_write_protect_off();         /* пустити годинник, якщо стоїть */
  ds_clock_start();
  ds_write(REG_WP, 0x80);

  /* Виставити час ОДИН раз на свіжій мікросхемі — розкоментуйте, прошийте,
     тоді закоментуйте назад: інакше час скидатиметься при кожному старті.
     struct Clock init = { 30, 47, 10, 4, 7, 5, 26 };
     ds_set_time(&init); */

  char buf[48];
  while (1) {
    struct Clock now;
    ds_read_burst(&now);
    int n = snprintf(buf, sizeof(buf), "20%02u-%02u-%02u %02u:%02u:%02u  (дн.тижня %u)\r\n",
                     now.year, now.month, now.date, now.hour, now.min, now.sec, now.dow);
    HAL_UART_Transmit(&huart2, (uint8_t *)buf, n, HAL_MAX_DELAY);
    HAL_Delay(1000);
  }
}
