// Те саме на STM32 HAL: затвор — HAL_GPIO_WritePin, вихід — вбудований АЦП.
HAL_GPIO_WritePin(SWITCH_EN_GPIO_Port, SWITCH_EN_Pin, GPIO_PIN_RESET);  // закрили канал
HAL_Delay(10);                                                          // ємності стекти

uint32_t raw = 0;
HAL_ADC_Start(&hadc1);
if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) raw = HAL_ADC_GetValue(&hadc1);
HAL_ADC_Stop(&hadc1);

uint32_t mv = raw * 3300u / 4095u;            // АЦП 12 біт, опора 3.3 В
if (mv > VOUT_OFF_THRESHOLD_MV) {
    // канал закрито, а напруга є → тече крізь body-діод (зворотне живлення)
    reverse_feed_detected = 1;                // прапорець для верхнього рівня
}
