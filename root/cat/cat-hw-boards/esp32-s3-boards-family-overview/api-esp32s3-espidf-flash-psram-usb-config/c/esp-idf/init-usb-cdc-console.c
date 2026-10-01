#include <stdio.h>
#include "driver/usb_serial_jtag.h"
#include "esp_log.h"

void init_usb_cdc_console(void) {
    // Конфігурація драйвера USB Serial/JTAG
    usb_serial_jtag_driver_config_t cfg = {
        .rx_buffer_size = 1024,
        .tx_buffer_size = 1024
    };

    // Встановлення драйвера
    esp_err_t ret = usb_serial_jtag_driver_install(&cfg);
    if (ret == ESP_OK) {
        printf("Драйвер USB CDC/JTAG успішно ініціалізовано.\n");
    }
}
