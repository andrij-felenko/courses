// htim3 налаштовано в ir_begin(): TIM3_CH1 = 38 кГц, шпаруватість ≈ 1/3
static void mark(uint16_t us) {                  // пачка несучої
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    delay_us(us);                                // мікросекундна пауза (DWT або окремий TIM)
    HAL_TIM_PWM_Stop(&htim3, TIM_CHANNEL_1);
}
static void space(uint16_t us) { delay_us(us); } // тиша тієї ж довжини

static void send_nec(uint8_t addr, uint8_t cmd) {
    uint32_t w = addr | (uint32_t)(uint8_t)~addr << 8
               | (uint32_t)cmd << 16 | (uint32_t)(uint8_t)~cmd << 24;
    mark(9000); space(4500);                     // преамбула
    for (int i = 0; i < 32; i++, w >>= 1) { mark(560); space((w & 1) ? 1690 : 560); }
    mark(560);                                   // стоп-імпульс
}

int main(void) {
    HAL_Init();
    ir_begin();
    while (1) { send_nec(0x00, 0x34); HAL_Delay(1000); }
}
