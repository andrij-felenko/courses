#include "main.h"

/* Мікросекунди HAL не дає: HAL_Delay рахує міліСЕКУНДИ. DS1302 точності не
   вимагає (шина до 2 МГц), тож вистачає грубого люфту на NOP-ах. */
static inline void ds_delay_us(uint32_t us) {
  uint32_t n = us * (SystemCoreClock / 1000000U) / 4U;   /* ~4 такти на виток */
  while (n--) __NOP();
}

/* Виставити один байт (біти 0..7, молодший уперед). DAT уже на ВИХІД. */
static void shift_out_byte(uint8_t v) {
  for (int i = 0; i < 8; i++) {
    HAL_GPIO_WritePin(DAT_PORT, DAT_PIN,
                      ((v >> i) & 1) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_SET);    /* ↑ мікросхема зчитала */
    ds_delay_us(1);
    HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_RESET);
    ds_delay_us(1);
  }
}

/* Забрати один байт. DAT уже на ВХІД. */
static uint8_t shift_in_byte(void) {
  uint8_t v = 0;
  for (int i = 0; i < 8; i++) {
    if (HAL_GPIO_ReadPin(DAT_PORT, DAT_PIN) == GPIO_PIN_SET) v |= (1u << i);
    HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_SET);
    ds_delay_us(1);
    HAL_GPIO_WritePin(CLK_PORT, CLK_PIN, GPIO_PIN_RESET);  /* ↓ новий біт на лінії */
    ds_delay_us(1);
  }
  return v;
}
