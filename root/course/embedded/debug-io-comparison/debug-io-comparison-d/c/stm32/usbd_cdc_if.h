#include "usbd_cdc_if.h"            // CDC_Transmit_FS — із середника USB Device

extern UART_HandleTypeDef huart2;
static const char msg[] = "link up\n";

// Звичайний UART (у роз'єм ST-LINK VCP): живий з перших тактів, але ~11 КБ/с
HAL_UART_Transmit(&huart2, (uint8_t *)msg, sizeof(msg) - 1, HAL_MAX_DELAY);

// Вбудований USB CDC (F4/L4/H7 з USB-периферією): мегабайти/с, без моста…
CDC_Transmit_FS((uint8_t *)msg, sizeof(msg) - 1);
// …але впаде чіп — порт відвалиться; а поки хост не забрав попередній пакет,
//   виклик поверне USBD_BUSY і рядок просто зникне, якщо не повторити
