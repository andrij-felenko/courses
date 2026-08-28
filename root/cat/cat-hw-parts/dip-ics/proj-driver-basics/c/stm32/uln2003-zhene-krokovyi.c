// 28BYJ-48 через ULN2003: напівкроковий режим, 8 станів.
// PA0..PA3 → IN1..IN4 (входи каналів 1..4), усі як GPIO_Output.
// Живлення мотора +5V; його спільний провід — на +5V; ULN2003 стягує фази в −.
// TIM6 у CubeMX налаштовано так, щоб один такт лічильника = 1 мкс.
extern TIM_HandleTypeDef htim6;

static const uint16_t PHASE_PIN[4] = {GPIO_PIN_0, GPIO_PIN_1, GPIO_PIN_2, GPIO_PIN_3};

// Вісім напівкрокових станів. Біт j рядка = рівень на IN(j+1).
static const uint8_t HALFSTEP[8][4] = {
  {1, 0, 0, 0},  {1, 1, 0, 0},  {0, 1, 0, 0},  {0, 1, 1, 0},
  {0, 0, 1, 0},  {0, 0, 1, 1},  {0, 0, 0, 1},  {1, 0, 0, 1},
};

static void ApplyState(int s) {
  for (int j = 0; j < 4; j++)
    HAL_GPIO_WritePin(GPIOA, PHASE_PIN[j],
                      HALFSTEP[s][j] ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

static void DelayUs(uint16_t us) {           // HAL_Delay має крок 1 мс — тут замало
  __HAL_TIM_SET_COUNTER(&htim6, 0);
  while (__HAL_TIM_GET_COUNTER(&htim6) < us) { }
}

int main(void) {
  HAL_Init();  SystemClock_Config();  MX_GPIO_Init();  MX_TIM6_Init();
  HAL_TIM_Base_Start(&htim6);

  while (1) {
    // один повний оберт «уперед»: женемо стани 0→7 багато разів
    for (int i = 0; i < 512; i++) {
      ApplyState(i & 7);      // i & 7 циклічно бере 0..7
      DelayUs(1500);          // пауза між кроками = швидкість
    }
  }
}
