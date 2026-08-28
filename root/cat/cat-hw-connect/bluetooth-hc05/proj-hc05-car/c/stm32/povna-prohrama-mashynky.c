// USART1 (9600 8N1) → модуль, приймання по перериванню; STATE → PA0 (Input, Pull-down).
// Для "%.2f" у snprintf увімкніть підтримку float у printf: -u _printf_float.
#include "main.h"
#include <stdio.h>
#include <stdbool.h>

extern UART_HandleTypeDef huart1;

#define STATE_PORT  GPIOA
#define STATE_PIN   GPIO_PIN_0
#define RX_SIZE     64              // степінь двійки: індекс маскуємо, а не ділимо

static volatile uint8_t rxRing[RX_SIZE];
static volatile uint8_t rxHead = 0, rxTail = 0;
static uint8_t rxByte;

static int      speedLevel    = 5;
static bool     wasConnected  = false;
static uint32_t lastTelemetry = 0;

void  applyDrive(int leftDir, int rightDir);   // ваша реалізація моторів
float readBattery(void);                       // ваш давач напруги

// Байт із модуля лягає в кільце й одразу чекаємо наступний — головний цикл не спиняється.
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart->Instance == USART1) {
        rxRing[rxHead++ % RX_SIZE] = rxByte;
        HAL_UART_Receive_IT(huart, &rxByte, 1);
    }
}

static bool btAvailable(void) { return rxHead != rxTail; }
static char btRead(void)      { return (char)rxRing[rxTail++ % RX_SIZE]; }

static void handleCommand(char c) {
    switch (c) {
        case 'F': applyDrive(+1, +1); break;
        case 'B': applyDrive(-1, -1); break;
        case 'L': applyDrive(-1, +1); break;
        case 'R': applyDrive(+1, -1); break;
        case 'S': applyDrive( 0,  0); break;
        default:
            if (c >= '0' && c <= '9') speedLevel = c - '0';
            break;
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART1_UART_Init();

    HAL_UART_Receive_IT(&huart1, &rxByte, 1);   // запускаємо приймання
    applyDrive(0, 0);                           // старт зі стопу

    while (1) {
        // 1) команди від телефона → дії
        while (btAvailable()) handleCommand(btRead());

        // 2) сторож зв'язку: обрив → аварійний стоп
        bool connected = (HAL_GPIO_ReadPin(STATE_PORT, STATE_PIN) == GPIO_PIN_SET);
        if (wasConnected && !connected) applyDrive(0, 0);
        wasConnected = connected;

        // 3) телеметрія раз на секунду, без блокування
        uint32_t now = HAL_GetTick();           // мілісекунди від старту
        if (connected && now - lastTelemetry >= 1000) {
            lastTelemetry = now;
            char line[32];
            int len = snprintf(line, sizeof line, "BAT:%.2f SPD:%d\r\n",
                               readBattery(), speedLevel);
            HAL_UART_Transmit(&huart1, (uint8_t *)line, len, 100);
        }
    }
}
