#include "main.h"

extern TIM_HandleTypeDef htim3;   // ШІМ 38 кГц, канал 1 — це вивід S
extern TIM_HandleTypeDef htim2;   // вільний лічильник на 1 МГц — мікросекунди

static void delay_us(uint16_t us) {
    __HAL_TIM_SET_COUNTER(&htim2, 0);
    while (__HAL_TIM_GET_COUNTER(&htim2) < us) { }
}

// «Пачка» — увімкнена несуча, «пауза» — вимкнена
static void mark(uint16_t us)  { HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1); delay_us(us); }
static void space(uint16_t us) { HAL_TIM_PWM_Stop(&htim3, TIM_CHANNEL_1);  delay_us(us); }

static void send_nec(uint32_t frame) {       // 32 біти, молодшим уперед
    mark(9000); space(4500);                 // преамбула NEC
    for (int i = 0; i < 32; i++) {
        mark(560);
        space(((frame >> i) & 1) ? 1690 : 560);  // «1» — довга пауза, «0» — коротка
    }
    mark(560);
    HAL_TIM_PWM_Stop(&htim3, TIM_CHANNEL_1); // завершальна пачка й тиша
}

void ir_loop(void) {              // виклик після MX_TIM2_Init()/MX_TIM3_Init()
    HAL_TIM_Base_Start(&htim2);
    while (1) {
        send_nec(0xCB34FF00);     // адреса 0x00, команда 0x34 з інверсіями
        HAL_Delay(1000);
    }
}
