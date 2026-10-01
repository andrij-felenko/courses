#ifndef USB_CONSOLE_H
#define USB_CONSOLE_H

#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Ініціалізує VFS драйвер USB Serial/JTAG для перенаправлення
 *        стандартного виведення (stdout/stderr) та введення (stdin)
 *        через апаратний USB-порт мікроконтролера ESP32-S3.
 *
 * @return esp_err_t ESP_OK у разі успіху або відповідний код помилки.
 */
esp_err_t usb_console_init(void);

#ifdef __cplusplus
}
#endif

#endif // USB_CONSOLE_H
