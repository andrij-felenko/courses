#include "stm32f1xx.h"

// --- Лінія DQ на PB6. Керуємо через регістри конфігурації й даних порту B. ---
#define OW_PIN        6
#define OW_PORT       GPIOB

// Перемкнути PB6 у режим "вихід open-drain" (потрібно на час притискання).
static inline void ow_dir_output(void) {
  // У STM32F1 режим піна задають 4 біти в CRL (для пінів 0..7).
  OW_PORT->CRL &= ~(0xF << (OW_PIN * 4));           // очистити поле піна
  OW_PORT->CRL |=  (0x5 << (OW_PIN * 4));           // 0b0101: вихід 10 МГц, open-drain
}

// Перемкнути PB6 у режим "вхід" (відпустити лінію — тягне зовнішня підтяжка).
static inline void ow_dir_input(void) {
  OW_PORT->CRL &= ~(0xF << (OW_PIN * 4));
  OW_PORT->CRL |=  (0x4 << (OW_PIN * 4));           // 0b0100: плаваючий вхід
}

// Притиснути лінію до нуля (у режимі open-drain "0" тягне лінію вниз).
static inline void ow_low(void) {
  ow_dir_output();
  OW_PORT->BSRR = (1 << (OW_PIN + 16));             // BR6: скинути PB6 у 0
}

// Відпустити лінію: перевести в режим входу, підтяжка підніме її сама.
static inline void ow_release(void) {
  ow_dir_input();
}

// Прочитати рівень лінії (0 або 1) з регістра входів.
static inline uint8_t ow_read(void) {
  return (OW_PORT->IDR & (1 << OW_PIN)) ? 1 : 0;
}

// Точна затримка в мікросекундах через лічильник тактів DWT.
// (увімкнути один раз у старті: CoreDebug->DEMCR |= TRCENA; DWT->CTRL |= 1;)
static inline void delay_us(uint32_t us) {
  uint32_t start = DWT->CYCCNT;
  uint32_t ticks = us * (SystemCoreClock / 1000000UL);   // тактів на 1 мкс × us
  while ((DWT->CYCCNT - start) < ticks) { /* крутимось */ }
}
