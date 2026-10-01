#include "usb_console.h"
#include <stdio.h>
#include <fcntl.h>
#include "esp_log.h"
#include "driver/usb_serial_jtag.h"
#include "esp_vfs_usb_serial_jtag.h"

static const char *TAG = "USB_CONSOLE";

esp_err_t usb_console_init(void)
{
    // Налаштування конфігурації за замовчуванням для драйвера USB Serial/JTAG
    usb_serial_jtag_driver_config_t usb_serial_jtag_config = USB_SERIAL_JTAG_DRIVER_CONFIG_DEFAULT();
    
    // Встановлення драйвера периферійного модуля USB Serial/JTAG
    esp_err_t ret = usb_serial_jtag_driver_install(&usb_serial_jtag_config);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося встановити драйвер USB Serial/JTAG: %s", esp_err_to_name(ret));
        return ret;
    }

    // Активація використання драйвера в системі VFS (Virtual File System)
    esp_vfs_usb_serial_jtag_use_driver();

    // Відключення буферизації стандартних потоків виведення/введення
    // для миттєвого відображення логів у USB-терміналі
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);

    ESP_LOGI(TAG, "Нативну консоль USB CDC/JTAG успішно ініціалізовано.");
    return ESP_OK;
}
