#include "stm32f4xx_hal.h"
#include <stdio.h>
#include <string.h>

typedef enum { ERR, WARN, INFO, DEBUG, VERBOSE } Level;
static const char *NAME[] = { "ERR", "WRN", "INF", "DBG", "VRB" };

#define LOG_LEVEL  DEBUG          // поріг: усе, що нижче, компілятор викине

extern UART_HandleTypeDef huart2; // готує CubeMX: MX_USART2_UART_Init()

// ── Кільцевий буфер останніх рядків ──────────────────────────────────────
#define RING_N  32
static char ring[RING_N][80];     // фіксовані рядки — без купи, без фрагментації
static int  head = 0;

static void ring_push(const char *s) {
    strncpy(ring[head], s, sizeof(ring[0]) - 1);
    ring[head][sizeof(ring[0]) - 1] = '\0';
    head = (head + 1) % RING_N;   // по колу: новий затирає найстаріший
}

// ── Один лог-рядок: час · рівень · мітка · повідомлення ──────────────────
void log_line(Level lv, const char *tag, const char *msg) {
    char buf[80];
    snprintf(buf, sizeof(buf), "%lu [%s] %s: %s\r\n",
             (unsigned long)HAL_GetTick(), NAME[lv], tag, msg);   // тики SysTick — мс
    ring_push(buf);                                               // завжди — у кільце
    HAL_UART_Transmit(&huart2, (uint8_t *)buf, strlen(buf), 100); // і в порт
}

// Макрос ховає поріг: при level > LOG_LEVEL весь виклик зникне з прошивки
#define LOG(level, tag, msg)  do { if ((level) <= LOG_LEVEL) log_line((level), (tag), (msg)); } while (0)

// ── При аварії (напр. з HardFault_Handler) — висипати кільце ─────────────
void dump_ring(void) {
    for (int i = 0; i < RING_N; i++) {
        char *s = ring[(head + i) % RING_N];
        HAL_UART_Transmit(&huart2, (uint8_t *)s, strlen(s), 100);
    }
}
