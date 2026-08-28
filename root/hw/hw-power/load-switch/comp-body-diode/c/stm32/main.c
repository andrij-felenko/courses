// Те саме на STM32 HAL: затвор — HAL_GPIO_WritePin, вихід — вбудований АЦП.
HAL_GPIO_WritePin(LOAD_EN_GPIO_Port, LOAD_EN_Pin, GPIO_PIN_RESET);  // закрили канал
HAL_Delay(10);                                                      // ємності стекти

uint32_t raw = 0;
HAL_ADC_Start(&hadc1);
if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) raw = HAL_ADC_GetValue(&hadc1);
HAL_ADC_Stop(&hadc1);

uint32_t mv = raw * 3300u / 4095u;           // АЦП 12 біт, опора 3.3 В
if (mv > VOUT_OFF_THRESHOLD_MV) {
    // канал закритий, а напруга лишилась → тече крізь body-діод (зворотне живлення)
    // повне відключення тут потребує ключа з reverse current blocking
    reverse_feed_detected = 1;               // прапорець для верхнього рівня
}
