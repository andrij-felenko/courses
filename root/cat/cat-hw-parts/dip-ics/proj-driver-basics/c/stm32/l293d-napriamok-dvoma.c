// L293D, перший міст: мотор між OUT1 (вивід 3) і OUT2 (вивід 6).
// EN1 (вивід 1) → PA6 = TIM3_CH1 (ШІМ); IN1 → PB0, IN2 → PB1 (GPIO_Output).
// Vss (вивід 16) = 5V логіки; Vs (вивід 8) = живлення мотора; GND (4,5,12,13) спільна з МК.
// TIM3 у CubeMX: PWM Generation CH1, період (ARR) = 255 → глибина так само 0..255.
extern TIM_HandleTypeDef htim3;

#define IN1_PORT GPIOB
#define IN1_PIN  GPIO_PIN_0
#define IN2_PORT GPIOB
#define IN2_PIN  GPIO_PIN_1

static void SetSpeed(uint8_t speed) {            // speed 0..255 — глибина ШІМ
  __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, speed);
}

static void Forward(uint8_t speed) {
  HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_SET);
  HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_RESET);
  SetSpeed(speed);                               // ШІМ на enable = оберти
}

static void Backward(uint8_t speed) {
  HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_RESET);
  HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_SET);
  SetSpeed(speed);
}

static void Brake(void) {                        // динамічне гальмо: enable є, входи однакові
  HAL_GPIO_WritePin(IN1_PORT, IN1_PIN, GPIO_PIN_SET);
  HAL_GPIO_WritePin(IN2_PORT, IN2_PIN, GPIO_PIN_SET);
  SetSpeed(255);                                 // міст увімкнено на повну, обмотка закорочена
}

static void Coast(void) { SetSpeed(0); }         // вільний хід: enable знято

int main(void) {
  HAL_Init();  SystemClock_Config();  MX_GPIO_Init();  MX_TIM3_Init();
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);      // з цієї миті нога EN1 під ШІМ

  while (1) {
    Forward(180);   HAL_Delay(1500);   // вперед на ~70% обертів
    Coast();        HAL_Delay(500);    // відпустили — котиться
    Backward(120);  HAL_Delay(1500);   // назад повільніше
    Brake();        HAL_Delay(500);    // різко спинили
  }
}
