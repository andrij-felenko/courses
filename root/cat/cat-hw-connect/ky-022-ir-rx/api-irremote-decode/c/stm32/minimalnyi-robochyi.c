#include "stm32f4xx_hal.h"       // захоплення таймера замість бібліотеки

extern TIM_HandleTypeDef htim2;  // TIM2: прескалер під 1 такт = 1 мкс,
extern UART_HandleTypeDef huart2;// канал 1 — захоплення на ОБИДВА фронти

#define IR_MAX 100
static uint16_t dur[IR_MAX];              // тривалості між фронтами, мкс
static uint16_t n_dur = 0;
static volatile uint8_t frame_ready = 0;  // аналог «decode() дав true»

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
    static uint32_t prev = 0;
    uint32_t now = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
    uint32_t d = (now - prev) & 0xFFFF;   // лічильник 16-бітний: переповнення лікується саме
    prev = now;
    if (d > 20000) n_dur = 0;             // довга тиша — початок нового кадру
    else if (n_dur < IR_MAX) dur[n_dur++] = (uint16_t)d;
    if (n_dur >= 67) frame_ready = 1;     // NEC: 67 інтервалів на повний кадр
}

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM2_Init(); MX_USART2_UART_Init();
    HAL_TIM_IC_Start_IT(&htim2, TIM_CHANNEL_1);      // старт приймача

    uint16_t addr, cmd;
    while (1) {
        if (frame_ready) {                           // прийшов цілий кадр?
            if (nec_decode(dur, n_dur, &addr, &cmd)) {
                char line[64];
                int k = snprintf(line, sizeof line,
                                 "протокол: NEC  адреса: 0x%X  команда: 0x%X\r\n", addr, cmd);
                HAL_UART_Transmit(&huart2, (uint8_t *)line, k, HAL_MAX_DELAY);
            }
            n_dur = 0; frame_ready = 0;              // звільнити буфер — роль resume()
        }
    }
}
