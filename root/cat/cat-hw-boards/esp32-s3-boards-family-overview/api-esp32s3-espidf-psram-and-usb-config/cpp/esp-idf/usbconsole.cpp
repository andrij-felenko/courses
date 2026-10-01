#include "esp_vfs_dev.h"
#include "esp_vfs_usb_serial_jtag.h"
#include "driver/usb_serial_jtag.h"
#include <iostream>

class UsbConsole {
public:
    static void redirect_stdio() {
        esp_vfs_usb_serial_jtag_use_driver();
        esp_vfs_dev_usb_serial_jtag_set_rx_line_endings(ESP_LINE_ENDINGS_CRLF);
        esp_vfs_dev_usb_serial_jtag_set_tx_line_endings(ESP_LINE_ENDINGS_CRLF);

        // Прив'язка системного VFS до стандартних дескрипторів C/C++
        freopen("/dev/usb_serial_jtag", "w", stdout);
        freopen("/dev/usb_serial_jtag", "r", stdin);
    }
};
