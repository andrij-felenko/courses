// N20 через DRV8833, канал A. STM32 + HAL (налаштування з CubeMX).
// TIM3 CH1 → AIN1, TIM3 CH2 → AIN2 (обидва в режимі PWM Generation).
// Такт таймера 84 МГц: Prescaler = 0, Period (ARR) = 4199 → 84e6/4200 = 20 кГц.
// nSLEEP — звичайний GPIO Output (тут PB0).
#include "main.h"

extern TIM_HandleTypeDef htim3;

#define PWM_MAX   4200                 // ARR+1: значення CCR ≥ PWM_MAX — постійна «1»
#define SLP_PORT  GPIOB
#define SLP_PIN   GPIO_PIN_0

static void motor_coast(void) {        // 0 0 → вибіг
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 0);
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, 0);
}

static void motor_brake(void) {        // 1 1 → гальмо
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, PWM_MAX);
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, PWM_MAX);
}

// «Фазна» схема: один канал у 0, на другий кладемо ШІМ-швидкість.
static void motor_drive(int speed) {
  if (speed >  100) speed =  100;
  if (speed < -100) speed = -100;
  uint32_t duty = (uint32_t)(speed < 0 ? -speed : speed) * PWM_MAX / 100;
  if (speed >= 0) {                    // ВПЕРЕД: CH2 у нулі, ШІМ на CH1
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, 0);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, duty);
  } else {                             // НАЗАД: навпаки
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 0);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_2, duty);
  }
}

static void motor_init(void) {
  HAL_GPIO_WritePin(SLP_PORT, SLP_PIN, GPIO_PIN_SET);   // будимо драйвер
  motor_coast();                                        // безпечний старт до пуску ШІМ
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_2);
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_TIM3_Init();
  motor_init();

  while (1) {
    for (int s = 0; s <= 100; s++) { motor_drive(s); HAL_Delay(20); }
    HAL_Delay(1000);
    motor_brake();
    HAL_Delay(500);
    for (int s = 0; s >= -100; s--) { motor_drive(s); HAL_Delay(20); }
    HAL_Delay(1000);
    motor_coast();
    HAL_Delay(1500);
  }
}
