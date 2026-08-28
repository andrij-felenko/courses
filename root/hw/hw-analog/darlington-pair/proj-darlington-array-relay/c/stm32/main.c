#include "stm32f4xx_hal.h"

// Вісім входів масиву (IN1..IN8) на одному порту: PB0..PB7.
// Масив — стік: логічна 1 на INk відкриває канал і притягує OUTk до землі.
#define IN_PORT GPIOB
static const uint16_t IN_PIN[8] = {
    GPIO_PIN_0, GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3,
    GPIO_PIN_4, GPIO_PIN_5, GPIO_PIN_6, GPIO_PIN_7,
};

static void Relays_Init(void) {
    __HAL_RCC_GPIOB_CLK_ENABLE();

    GPIO_InitTypeDef gpio = {0};
    gpio.Mode  = GPIO_MODE_OUTPUT_PP;       // двотактний вихід: сам жене й 0, і 1
    gpio.Pull  = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;       // реле — повільне навантаження
    for (uint8_t ch = 0; ch < 8; ch++) {
        gpio.Pin = IN_PIN[ch];
        HAL_GPIO_Init(IN_PORT, &gpio);
        HAL_GPIO_WritePin(IN_PORT, IN_PIN[ch], GPIO_PIN_RESET);  // старт: усі закриті
    }
}

static void Relay_Set(uint8_t ch, uint8_t on) {
    HAL_GPIO_WritePin(IN_PORT, IN_PIN[ch], on ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

// Виставити одразу весь банк за бітовою маскою: біт k = 1 → реле k увімкнено.
static void Relay_Bank(uint8_t mask) {
    for (uint8_t ch = 0; ch < 8; ch++)
        Relay_Set(ch, (mask >> ch) & 1);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    Relays_Init();
    for (;;) {
        Relay_Set(0, 1);            // клацнули перше реле
        HAL_Delay(500);
        Relay_Set(0, 0);
        HAL_Delay(500);
        Relay_Bank(0b10101010);     // увімкнули реле 1, 3, 5, 7 воднораз
        HAL_Delay(500);
        Relay_Bank(0x00);           // усі відпустили
        HAL_Delay(500);
    }
}
