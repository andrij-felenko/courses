// Два 74HC595 — це звичайний зсувний регістр, тож віддамо байти апаратному SPI,
// а латч лишиться простим виводом.
#include "main.h"                  // згенероване CubeMX: hspi1, *_GPIO_Port / *_Pin

extern SPI_HandleTypeDef hspi1;    // MSB first, CPOL = 0, CPHA = 0

// байти сегментів для цифр 0..9 (спільний анод: 0 = сегмент світиться)
static const uint8_t SEG[10] = { 0xC0,0xF9,0xA4,0xB0,0x99,0x92,0x82,0xF8,0x80,0x90 };
static const uint8_t SEL[4]  = { 0xF1,0xF2,0xF4,0xF8 };   // вибір розряду 1..4

// виставити один розряд: байт сегментів + байт вибору, клац латчем
static void latch_out(uint8_t seg, uint8_t sel) {
  uint8_t frame[2] = { seg, sel };           // спершу сегменти, потім вибір
  HAL_GPIO_WritePin(LATCH_GPIO_Port, LATCH_Pin, GPIO_PIN_RESET);
  HAL_SPI_Transmit(&hspi1, frame, 2, HAL_MAX_DELAY);
  HAL_GPIO_WritePin(LATCH_GPIO_Port, LATCH_Pin, GPIO_PIN_SET);
}

static void refresh(int value) {
  int v = value < 0 ? -value : value;        // модуль для показу
  uint8_t d[4] = { (uint8_t)(v/1000%10), (uint8_t)(v/100%10),
                   (uint8_t)(v/10%10),   (uint8_t)(v%10) };
  for (uint8_t pos = 0; pos < 4; pos++) {
    latch_out(SEG[d[pos]], SEL[pos]);
    delay_us(500);                           // трохи потримати розряд (DWT або TIMx)
    latch_out(0xFF, 0xFF);                   // погасити перед наступним
  }
}

int main(void) {
  HAL_Init();  SystemClock_Config();  MX_GPIO_Init();  MX_SPI1_Init();
  // кнопки S1/S2 — входи з підтяжкою до живлення (GPIO_PULLUP у CubeMX)

  int counter = 0;
  uint8_t s1was = 0, s2was = 0;              // попередній стан для фронту
  while (1) {
    uint8_t s1 = (HAL_GPIO_ReadPin(S1_GPIO_Port, S1_Pin) == GPIO_PIN_RESET);
    uint8_t s2 = (HAL_GPIO_ReadPin(S2_GPIO_Port, S2_Pin) == GPIO_PIN_RESET);
    if (s1 && !s1was) counter++;             // спрацювати раз на натиск
    if (s2 && !s2was) counter--;
    s1was = s1;  s2was = s2;
    refresh(counter);                        // перебрати розряди — раз за прохід
  }
}
