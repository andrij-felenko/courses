#include "main.h"                        // CubeMX: SPI1 = PA5/PA6/PA7, PA4 і PB0 — виходи
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

extern SPI_HandleTypeDef hspi1;

#define CSN(v) HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, (v) ? GPIO_PIN_SET : GPIO_PIN_RESET)
#define CE(v)  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, (v) ? GPIO_PIN_SET : GPIO_PIN_RESET)

static const uint8_t addr[5] = { 0xE7, 0xE7, 0xE7, 0xE7, 0xE7 };

// Перший байт відповіді чипа — завжди STATUS, хоч би яку команду ви послали.
static uint8_t nrf_xfer(const uint8_t *tx, uint8_t *rx, uint16_t n) {
  uint8_t tmp[33];
  if (!rx) rx = tmp;
  CSN(0);
  HAL_SPI_TransmitReceive(&hspi1, (uint8_t *)tx, rx, n, HAL_MAX_DELAY);
  CSN(1);
  return rx[0];
}
static void nrf_wr(uint8_t reg, const uint8_t *v, uint16_t n) {
  uint8_t tx[6] = { 0x20 | reg };        // 0x20 = W_REGISTER
  memcpy(tx + 1, v, n);
  nrf_xfer(tx, NULL, n + 1);
}
static void nrf_wr1(uint8_t reg, uint8_t v) { nrf_wr(reg, &v, 1); }

static bool nrf_bus_init(void) {         // = radio.begin(): підняти шину й перевірити чип
  CE(0);
  CSN(1);
  HAL_Delay(100);                        // чипові треба ~100 мс після подачі живлення
  nrf_wr1(0x05, 76);                     // RF_CH — канал 76
  uint8_t back[2], q[2] = { 0x05, 0xFF };
  nrf_xfer(q, back, 2);                  // прочитати той самий регістр назад
  return back[1] == 76;                  // не збіглося — чип не піднявся по SPI
}

static void nrf_tx_init(void) {
  nrf_wr1(0x06, 0x22);      // RF_SETUP: 250 кбіт/с + PA_LOW
  nrf_wr1(0x04, 0x5F);      // SETUP_RETR: 1500 мкс × 15 спроб авто-ACK
  nrf_wr(0x10, addr, 5);    // TX_ADDR    — куди пишемо
  nrf_wr(0x0A, addr, 5);    // RX_ADDR_P0 — на цю трубу чип чекає ACK
  nrf_wr1(0x00, 0x0E);      // CONFIG: CRC 2 байти, PWR_UP, PRIM_RX = 0
  HAL_Delay(5);
}

static bool nrf_send(const void *p, uint16_t n) {
  uint8_t tx[33] = { 0xA0 }, nop = 0xFF, st;   // 0xA0 = W_TX_PAYLOAD
  memcpy(tx + 1, p, n);
  nrf_xfer(tx, NULL, n + 1);
  CE(1);
  for (volatile int i = 0; i < 300; i++) {}    // імпульс >10 мкс (точніше — таймером)
  CE(0);
  do { st = nrf_xfer(&nop, NULL, 1); } while (!(st & 0x30));  // TX_DS або MAX_RT
  nrf_wr1(0x07, st & 0x30);                    // скинути прапорці
  return st & 0x20;                            // TX_DS → приймач підтвердив
}

int main(void) {
  HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_SPI1_Init();
  if (!nrf_bus_init()) { printf("nRF24 не відповідає\n"); while (1) {} }
  nrf_tx_init();
  for (uint32_t counter = 0;; counter++) {
    char msg[32];
    int n = snprintf(msg, sizeof msg, "hello %lu", (unsigned long)counter);
    bool ok = nrf_send(msg, n + 1);            // + 1 — завершальний \0
    printf("%s  %s\n", ok ? "ACK" : "нема ACK", msg);   // UART або ITM
    HAL_Delay(1000);
  }
}
