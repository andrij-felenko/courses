// ── Неблокувальний стагер на STM32 (HAL). Той самий принцип. ──
// Розклад пусків + HAL_GetTick() (мілісекунди від старту); команди йдуть
// по черзі, головний цикл не спиняється жодним HAL_Delay.
#include "stm32f4xx_hal.h"

#define N 4
#define STAGGER_MS 90

static uint8_t  target[N];
static uint32_t dueAt[N];
static bool     pending[N];

// Задати нову «розкладку» цілей: серва рушать по черзі, а не разом.
void ScheduleMove(const uint8_t deg[N]) {
  uint32_t now = HAL_GetTick();
  for (uint8_t i = 0; i < N; i++) {
    target[i]  = deg[i];
    dueAt[i]   = now + (uint32_t)i * STAGGER_MS;   // i-те чекає i кроків
    pending[i] = true;
  }
}

// Викликати ЧАСТО (щооберту головного циклу).
void ServiceStagger(void) {
  uint32_t now = HAL_GetTick();
  for (uint8_t i = 0; i < N; i++) {
    if (pending[i] && (int32_t)(now - dueAt[i]) >= 0) {
      ServoMove(i, target[i]);                     // рушаємо ОДНЕ
      pending[i] = false;
    }
  }
}

int main(void) {
  HAL_Init();  SystemClock_Config();  MX_TIM3_Init();
  ServoInit();                          // усі серва — у центр
  uint32_t last = 0;
  for (;;) {
    if (HAL_GetTick() - last > 3000) {  // раз на 3 с нові кути — по черзі
      const uint8_t goal[N] = {30, 60, 120, 150};
      ScheduleMove(goal);
      last = HAL_GetTick();
    }
    ServiceStagger();      // піки рознесені; тут-таки радіо, вимір шини…
  }
}
