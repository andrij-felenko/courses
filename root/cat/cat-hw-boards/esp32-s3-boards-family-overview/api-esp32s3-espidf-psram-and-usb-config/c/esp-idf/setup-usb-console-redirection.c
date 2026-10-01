#include "esp_vfs_dev.h"
#include "esp_vfs_usb_serial_jtag.h"
#include "driver/usb_serial_jtag.h"
#include <stdio.h>

void setup_usb_console_redirection(void)
{
    // Реєстрація драйвера USB Serial/JTAG у файловій системі VFS
    esp_vfs_usb_serial_jtag_use_driver();

    // Налаштування обробки символів переведення рядка для stdout та stdin
    esp_vfs_dev_usb_serial_jtag_set_rx_line_endings(ESP_LINE_ENDINGS_CRLF);
    esp_vfs_dev_usb_serial_jtag_set_tx_line_endings(ESP_LINE_ENDINGS_CRLF);

    // Перенаправлення стандартних потоків вводу та виводу
    freopen("/dev/usb_serial_jtag", "w", stdout);
    freopen("/dev/usb_serial_jtag", "r", stdin);
}
