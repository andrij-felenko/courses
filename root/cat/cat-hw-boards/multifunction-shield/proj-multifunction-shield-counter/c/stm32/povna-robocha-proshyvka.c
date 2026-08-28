// Фон — переривання TIM3; події з нього забираємо через кільцевий буфер.
#include "main.h"                  // згенероване CubeMX: htim3, *_GPIO_Port / *_Pin

extern TIM_HandleTypeDef htim3;    // налаштований на 2 мс, Base_Start_IT

// драйвер шилда: перебір розрядів і відбивання кнопок — див. наступний розділ
void    shield_init(void);
void    shield_show(int value);
void    shield_refresh(void);
uint8_t shield_scan(void);
void    shield_beep(uint16_t ms);
void    shield_led(uint8_t n, uint8_t on);

static volatile uint8_t evq[8], head, tail;

// те саме, що MFS робить у своєму таймерному перериванні
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance != TIM3) return;
  shield_refresh();                              // освіжити наступний розряд
  uint8_t ev = shield_scan();                    // відбити кнопки
  if (ev) { evq[head] = ev; head = (head + 1) & 7; }   // подію — у кільце
}

int main(void) {
  int counter = 0;
  HAL_Init();  SystemClock_Config();  MX_GPIO_Init();  MX_TIM3_Init();
  shield_init();
  HAL_TIM_Base_Start_IT(&htim3);
  shield_show(counter);                          // одразу показати початкове значення

  while (1) {
    if (head == tail) continue;                  // черга порожня — нема чого робити
    uint8_t ev = evq[tail];  tail = (tail + 1) & 7;
    switch (ev) {
      case BTN1_SHORT_RELEASE: counter++; shield_beep(50);    break;  // S1 коротко: +1
      case BTN2_SHORT_RELEASE: counter--; shield_beep(50);    break;  // S2 коротко: −1
      case BTN1_LONG_PRESSED:  counter++;                     break;  // тримають: біжить угору
      case BTN2_LONG_PRESSED:  counter--;                     break;  // тримають: біжить униз
      case BTN3_LONG_RELEASE:  counter = 0; shield_beep(200); break;  // скинути в нуль
    }
    shield_show(counter);
    shield_led(1, counter < 0);                  // світлодіод, поки число від'ємне
  }
}
