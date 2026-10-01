#include "driver/usb_serial_jtag.h"
#include "esp_err.h"

esp_err_t init_usb_serial_jtag(void)
{
    // Налаштування розмірів кільцевих буферів прийому та передачі
    usb_serial_jtag_driver_config_t config = {
        .rx_buffer_size = 1024,
        .tx_buffer_size = 1024,
    };

    // Встановлення низькорівневого драйвера USB Serial/JTAG
    esp_err_t err = usb_serial_jtag_driver_install(&config);
    if (err != ESP_OK) {
        return err;
    }

    return ESP_OK;
}
