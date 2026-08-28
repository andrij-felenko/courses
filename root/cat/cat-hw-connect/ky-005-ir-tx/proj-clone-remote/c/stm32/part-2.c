/* TIM1_CH1 → нога KY-005: ШІМ 38 кГц зі шпаруватістю ≈1/3.
   «Імпульс» — це увімкнена несуча, «пауза» — вимкнена. delay_us() — свій
   лічильник (DWT->CYCCNT або вільний таймер), бо HAL_Delay() міряє мілісекунди. */
extern TIM_HandleTypeDef htim1;

static void mark(uint16_t us)  { HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1); delay_us(us); }
static void space(uint16_t us) { HAL_TIM_PWM_Stop(&htim1, TIM_CHANNEL_1);  delay_us(us); }

static void send_nec(uint8_t addr, uint8_t cmd) {
    uint32_t frame = addr | (uint32_t)(uint8_t)~addr << 8 |
                     (uint32_t)cmd << 16 | (uint32_t)(uint8_t)~cmd << 24;
    mark(9000); space(4500);                        // преамбула NEC
    for (int i = 0; i < 32; i++) {                  // молодшим бітом уперед
        mark(560);
        space(((frame >> i) & 1) ? 1690 : 560);     // довга пауза = «1»
    }
    mark(560);                                      // завершальний імпульс
    HAL_TIM_PWM_Stop(&htim1, TIM_CHANNEL_1);
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM1_Init();
    while (1) {
        // зняті адреса й команда — просто вставлені сюди:
        send_nec(0xF1, 0x76);   // «гучність +», зняте з рідного пульта
        HAL_Delay(2000);
        send_nec(0xF1, 0x77);   // «гучність −»
        HAL_Delay(2000);
    }
}
