#include "driver/uart.h"
#include "driver/usb_serial_jtag.h"

// Звичайний UART через зовнішній міст: живий з перших тактів, але ~11 КБ/с
const uart_config_t ucfg = { .baud_rate = 115200, .data_bits = UART_DATA_8_BITS,
                             .parity = UART_PARITY_DISABLE, .stop_bits = UART_STOP_BITS_1 };
uart_param_config(UART_NUM_0, &ucfg);
uart_write_bytes(UART_NUM_0, "link up\n", 8);   // повзе дротом ~0.7 мс на рядок

// Вбудований USB Serial/JTAG (ESP32-S3/C3): мегабайти/с, без моста на платі…
usb_serial_jtag_driver_config_t jcfg = USB_SERIAL_JTAG_DRIVER_CONFIG_DEFAULT();
usb_serial_jtag_driver_install(&jcfg);
usb_serial_jtag_write_bytes("link up\n", 8, portMAX_DELAY);
// …але впаде чіп — порт відвалиться; а з portMAX_DELAY і без відкритого
//   монітора цей виклик чекатиме, доки байти вичитають
