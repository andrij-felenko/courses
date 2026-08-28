// вихід компаратора на PB0; підтяжку на платі ведемо до 3.3 В (вигода №1)
GPIO_InitTypeDef io = {0};
__HAL_RCC_GPIOB_CLK_ENABLE();
io.Pin  = GPIO_PIN_0;
io.Mode = GPIO_MODE_INPUT;
io.Pull = GPIO_NOPULL;                     // «1» дає зовнішній Rpull
HAL_GPIO_Init(GPIOB, &io);

if (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_0) == GPIO_PIN_SET) {  // перейдено поріг
    fan_on();                              // гаряче: вмикаємо вентилятор
} else {
    fan_off();                             // холодно
}
