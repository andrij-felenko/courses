// 28BYJ-48 через ULN2003, напівкроковий режим із розгоном. Крок робить
// переривання TIM2, а період (ARR) переписуємо після кожного кроку — це
// місцевий відповідник run(). TIM2 у CubeMX: PSC такий, щоб такт був 1 МГц.
#include "main.h"

extern TIM_HandleTypeDef htim2;

#define STEPS_PER_REV  4076

typedef struct { GPIO_TypeDef *port; uint16_t pin; } out_t;
static const out_t IN[4] = {
    { GPIOB, GPIO_PIN_0 }, { GPIOB, GPIO_PIN_1 },
    { GPIOB, GPIO_PIN_2 }, { GPIOB, GPIO_PIN_3 },
};

// Напівкрокова послідовність (8 тактів) у ФІЗИЧНОМУ порядку IN1..IN4.
static const uint8_t HALF_STEP[8][4] = {
    {1,0,0,0}, {1,1,0,0}, {0,1,0,0}, {0,1,1,0},
    {0,0,1,0}, {0,0,1,1}, {0,0,0,1}, {1,0,0,1},
};

static const float MAX_SPEED = 600.0f; // кроків/с
static const float ACCEL     = 500.0f; // кроків/с²
static const float MIN_SPEED =  20.0f; // з ним ARR ≤ 49999 — влазить і в 16 біт

static volatile long position = 0, target = 0;
static float speed = MIN_SPEED;
static int phase = 0;

static void apply_phase(int p) {
  for (int i = 0; i < 4; i++)
    HAL_GPIO_WritePin(IN[i].port, IN[i].pin,
                      HALF_STEP[p][i] ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance != TIM2) return;             // таймер бази часу — не наш клопіт
  long togo = target - position;
  if (togo == 0) { HAL_TIM_Base_Stop_IT(&htim2); speed = MIN_SPEED; return; }
  int dir = (togo > 0) ? 1 : -1;
  phase = (phase + dir + 8) & 7;
  apply_phase(phase);
  position += dir;

  // Гальмівний шлях із поточної швидкості — v²/(2a).
  float left = (float)(togo * dir - 1);
  float dt = 1.0f / speed;
  if (left <= speed * speed / (2.0f * ACCEL)) speed -= ACCEL * dt;
  else if (speed < MAX_SPEED)                 speed += ACCEL * dt;
  if (speed < MIN_SPEED) speed = MIN_SPEED;
  __HAL_TIM_SET_AUTORELOAD(&htim2, (uint32_t)(1000000.0f / speed) - 1);
}

static void move_to(long p) {                     // абсолютна ціль у кроках
  target = p;
  if (position != p) HAL_TIM_Base_Start_IT(&htim2);
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_TIM2_Init();

  move_to(STEPS_PER_REV);                         // ціль: один оберт уперед
  while (1) {                                     // цикл вільний: тут кнопка, дисплей…
    if (position == target) move_to(-position);   // доїхали — розвертаємось
    HAL_Delay(50);
  }
}
