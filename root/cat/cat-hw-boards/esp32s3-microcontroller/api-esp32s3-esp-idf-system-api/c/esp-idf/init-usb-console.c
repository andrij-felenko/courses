#include "esp_vfs_dev_usb_serial_jtag.h"
#include "driver/usb_serial_jtag.h"
#include "esp_log.h"
#include <stdio.h>

void init_usb_console(void) {
    // Вимикаємо буферизацію stdout для миттєвого виведення логів
    setvbuf(stdout, NULL, _IONBF, 0);

    // Налаштування VFS драйвера USB Serial/JTAG
    esp_vfs_usb_serial_jtag_vfs_config_t vfs_config = ESP_VFS_USB_SERIAL_JTAG_VFS_CONFIG_DEFAULT();
    esp_err_t err = esp_vfs_dev_usb_serial_jtag_register(&vfs_config);
    if (err == ESP_OK) {
        // Перенаправляємо системний вивід і вмикаємо неблокувальний режим
        esp_vfs_dev_usb_serial_jtag_use_nonblocking();
        esp_vfs_dev_usb_serial_jtag_use_driver();
    }
}
