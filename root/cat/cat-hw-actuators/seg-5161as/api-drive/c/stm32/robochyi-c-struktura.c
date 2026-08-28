#include "main.h"        // згенерований CubeMX: порти, ноги, MX_GPIO_Init()
#include <stdbool.h>

// Вивід тут — пара «порт + пін», у тому самому порядку a,b,c,d,e,f,g,DP.
typedef struct { GPIO_TypeDef *port; uint16_t pin; } SegPin;

static const SegPin SEG[8] = {
  {GPIOA, GPIO_PIN_0}, {GPIOA, GPIO_PIN_1}, {GPIOA, GPIO_PIN_2}, {GPIOA, GPIO_PIN_3},
  {GPIOA, GPIO_PIN_4}, {GPIOA, GPIO_PIN_5}, {GPIOA, GPIO_PIN_6}, {GPIOA, GPIO_PIN_7},
};
static const bool COMMON_ANODE = false;   // 5161AS — спільний катод

// Окремого begin() немає: усі вісім ніг позначені GPIO_Output у CubeMX,
// і режим виходу виставляє згенерований MX_GPIO_Init().
static void seg_show_mask(uint8_t mask) {
  for (int i = 0; i < 8; i++) {
    bool on = (mask >> i) & 1;
    if (COMMON_ANODE) on = !on;
    HAL_GPIO_WritePin(SEG[i].port, SEG[i].pin, on ? GPIO_PIN_SET : GPIO_PIN_RESET);
  }
}

static void seg_show_hex(uint8_t v, bool dot) {
  uint8_t m = FONT[v & 0x0F];
  if (dot) m |= SDP;
  seg_show_mask(m);
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  while (1) {
    for (uint8_t v = 0; v < 16; v++) {
      seg_show_hex(v, v == 10);
      HAL_Delay(500);
    }
  }
}
