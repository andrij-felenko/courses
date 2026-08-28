/* CubeMX: PA0 — GPIO_Input без підтяжки (DO має свою на платі),
           PA5 — GPIO_Output (світлодіод LD2 на Nucleo-64).
   ky038_poll() викликається з нескінченного циклу в main(). */
#define SOUND_PORT  GPIOA
#define SOUND_PIN   GPIO_PIN_0
#define LED_PORT    GPIOA
#define LED_PIN     GPIO_PIN_5

static uint32_t last_evt = 0;   // HAL_GetTick() останньої зарахованої події
static uint32_t count    = 0;   // лічильник гучних подій

void ky038_poll(void) {
    GPIO_PinState loud = HAL_GPIO_ReadPin(SOUND_PORT, SOUND_PIN);  // SET = звук понад поріг
    HAL_GPIO_WritePin(LED_PORT, LED_PIN, loud);                    // світимо, поки чуємо гучне

    // рахуємо подію не частіше ніж раз на 300 мс; HAL_GetTick() лічить мілісекунди
    uint32_t now = HAL_GetTick();
    if (loud == GPIO_PIN_SET && now - last_evt > 300) {
        last_evt = now;
        printf("гучно #%lu\r\n", (unsigned long)++count);   // printf перенаправлено на UART
    }
    HAL_Delay(2);   // щільний цикл, щоб не проґавити короткий сплеск звуку
}
