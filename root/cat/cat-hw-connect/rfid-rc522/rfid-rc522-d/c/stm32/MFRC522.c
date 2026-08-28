/* STM32 HAL + порт бібліотеки MFRC522 (MFRC522.c/.h у проєкті).
   SPI, CS і RST розводить CubeMX; порт бере їх із MFRC522_conf.h. */
#include "main.h"
#include "MFRC522.h"
#include <stdio.h>
#include <string.h>

extern SPI_HandleTypeDef  hspi1;     // апаратний SPI до модуля
extern UART_HandleTypeDef huart2;    // куди друкуємо UID

int main(void)
{
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_SPI1_Init();                    // SCK/MOSI/MISO
  MX_USART2_UART_Init();

  MFRC522_Init();                    // ініціалізуємо чип MFRC522

  uint8_t type[2], uid[5];
  char line[32];

  while (1) {
    // чи є нова мітка в полі? (REQA — «озвіться, хто в полі»)
    if (MFRC522_Request(PICC_REQIDL, type) != MI_OK) { HAL_Delay(50); continue; }
    // антиколізія: витягуємо UID однієї мітки
    if (MFRC522_Anticoll(uid) != MI_OK)              { HAL_Delay(50); continue; }

    int n = snprintf(line, sizeof line, "UID: %02X %02X %02X %02X\r\n",
                     uid[0], uid[1], uid[2], uid[3]);
    HAL_UART_Transmit(&huart2, (uint8_t *)line, n, HAL_MAX_DELAY);

    MFRC522_Halt();                  // відпускаємо мітку, щоб не читати без кінця
    HAL_Delay(500);
  }
}
