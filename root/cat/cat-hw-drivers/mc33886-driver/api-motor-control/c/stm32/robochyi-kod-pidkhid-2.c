// ── MC33886: ШІМ прямо на IN, EN ввімкнено. STM32 (HAL) ──
// ОБИДВІ ніжки напрямку — канали ОДНОГО таймера, тож частота спільна
// автоматично. Активний канал модулюється, «мовчазний» тримає CCR = 0.

#include "main.h"

extern TIM_HandleTypeDef htim3;   // CubeMX: TIM3_CH1 = IN1, TIM3_CH2 = IN2

#define DUTY_MAX  999             // = ARR
#define EN_PORT   GPIOB
#define EN_PIN    GPIO_PIN_2      // проста GPIO, тримаємо в «1»

static void motor_brake(void) {
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 0);
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, 0);   // 0 0 → тримаюче гальмо
}

static void motor_init(void) {
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);          // обидва канали — ШІМ
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);
  HAL_GPIO_WritePin(EN_PORT, EN_PIN, GPIO_PIN_SET);  // міст живий увесь час
  motor_brake();
}

static void motor_forward(uint16_t duty) {
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 0);      // стала «0»
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, duty);   // у паузах стан 0 0
}

static void motor_reverse(uint16_t duty) {
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, 0);
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, duty);
}

static void motor_coast(void) {
  HAL_GPIO_WritePin(EN_PORT, EN_PIN, GPIO_PIN_RESET);   // вибіг — лише через EN
  motor_brake();
}

int main(void) {
  HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM3_Init();
  motor_init();
  while (1) {
    HAL_GPIO_WritePin(EN_PORT, EN_PIN, GPIO_PIN_SET);
    motor_forward(700); HAL_Delay(1500);
    motor_reverse(470); HAL_Delay(1500);
    motor_brake();      HAL_Delay(800);
  }
}
