// ── MC33886: керування мотором. STM32 (HAL, таймер у режимі PWM) ──
// EN сидить на каналі таймера: частота = f_тайм / ((PSC+1)·(ARR+1)).
// Швидкість — регістр порівняння CCR (0..ARR); напрямок — рівні GPIO.

#include "main.h"

extern TIM_HandleTypeDef htim3;  // CubeMX: TIM3_CH1 на PA6, ARR = 999 → 5 кГц

#define DUTY_MAX  999            // шкала 0..ARR, а не 0..255 і не 0..1023
#define IN1_PORT  GPIOB
#define IN1_PIN   GPIO_PIN_0     // напрямок, будь-яка GPIO-вихід
#define IN2_PORT  GPIOB
#define IN2_PIN   GPIO_PIN_1

static void motor_duty(uint16_t duty) {   // одна ручка швидкості
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, duty);
}

static void motor_coast(void) { motor_duty(0); }  // EN=0 → тристейт, вибіг

static void motor_init(void) {
  // Самі ніжки й таймер налаштовує згенерований CubeMX код (MX_GPIO_Init,
  // MX_TIM3_Init); нам лишається запустити ШІМ і стати в безпечний стан.
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
  motor_coast();                 // старт у безпечному стані: міст вимкнено
}

// duty: 0..DUTY_MAX — шпаруватість ШІМ (частка періоду, не вольти).
static void motor_forward(uint16_t duty) {
  HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_RESET);
  HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_SET);   // OUT1=−, OUT2=+
  motor_duty(duty);
}

static void motor_reverse(uint16_t duty) {
  HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_SET);
  HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_RESET); // OUT1=+, OUT2=−
  motor_duty(duty);
}

static void motor_brake(void) {
  HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_RESET);
  HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_RESET); // 0 0 → гальмо
  motor_duty(DUTY_MAX);          // міст має бути ВВІМКНЕНИЙ, щоб коротити
}

int main(void) {
  HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM3_Init();
  motor_init();
  while (1) {
    motor_forward(700); HAL_Delay(1500);   // ~70% від 999
    motor_coast();      HAL_Delay(800);
    motor_reverse(470); HAL_Delay(1500);
    motor_brake();      HAL_Delay(800);
  }
}
