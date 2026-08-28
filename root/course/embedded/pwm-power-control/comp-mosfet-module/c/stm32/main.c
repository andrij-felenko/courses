// TIM3_CH1 у режимі ШІМ на ніжці затвора (CubeMX: PSC = 0, ARR = 3999,
// такт таймера 80 МГц → 80 МГц / 4000 = 20 кГц).
extern TIM_HandleTypeDef htim3;

#define GATE_TIM  (&htim3)
#define GATE_CH   TIM_CHANNEL_1
#define GATE_ARR  3999U

static void gate_set(uint8_t duty8) {         // та сама шкала 0…255
    __HAL_TIM_SET_COMPARE(GATE_TIM, GATE_CH, (GATE_ARR + 1U) * duty8 / 256U);
}

void gate_start(void) {
    gate_set(0);                              // старт із закритого ключа
    HAL_TIM_PWM_Start(GATE_TIM, GATE_CH);
}

void gate_ramp(void) {
    for (int d = 0; d <= 255; d++) {          // плавний пуск: 0→100%
        gate_set((uint8_t)d);
        HAL_Delay(4);
    }
    HAL_Delay(500);
}
