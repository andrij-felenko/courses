#include "esp_vfs_dev_usb_serial_jtag.h"
#include "driver/usb_serial_jtag.h"
#include "esp_log.h"
#include <cstdio>

class UsbConsole {
public:
    static esp_err_t init() noexcept {
        std::setvbuf(stdout, nullptr, _IONBF, 0);
        esp_vfs_usb_serial_jtag_vfs_config_t vfs_config = ESP_VFS_USB_SERIAL_JTAG_VFS_CONFIG_DEFAULT();
        esp_err_t status = esp_vfs_dev_usb_serial_jtag_register(&vfs_config);
        if (status == ESP_OK) {
            esp_vfs_dev_usb_serial_jtag_use_nonblocking();
            esp_vfs_dev_usb_serial_jtag_use_driver();
        }
        return status;
    }
};
