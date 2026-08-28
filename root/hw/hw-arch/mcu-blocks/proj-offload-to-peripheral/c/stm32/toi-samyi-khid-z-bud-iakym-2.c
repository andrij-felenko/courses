volatile bool has_byte = false;
uint8_t rx;

// приймання запускають один раз: HAL_UART_Receive_IT(&huart1, &rx, 1);
// далі байт кладе в rx апаратура з обробником, а не наш цикл
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
  has_byte = true;
  HAL_UART_Receive_IT(huart, &rx, 1);   // одразу чекати наступний
}

while (1) {
  if (has_byte) {
    has_byte = false;
    // обробити отриманий символ rx
  }
  // тут же — будь-яка інша робота, бо ми не застрягли в очікуванні
}
