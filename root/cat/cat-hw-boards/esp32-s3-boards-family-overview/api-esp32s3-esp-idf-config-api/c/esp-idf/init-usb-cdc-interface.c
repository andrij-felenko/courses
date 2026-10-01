#include "tinyusb.h"
#include "tusb_cdc_acm.h"

void init_usb_cdc_interface(void) {
    const tinyusb_config_t tusb_cfg = {
        .device_descriptor = NULL,
        .string_descriptor = NULL,
        .external_phy = false,
        .configuration_descriptor = NULL,
    };

    ESP_ERROR_CHECK(tinyusb_driver_install(&tusb_cfg));
    
    tinyusb_config_cdcacm_t cdc_cfg = {
        .usb_dev = TINYUSB_USB_PERIPH_0,
        .cdc_port = TINYUSB_CDC_ACM_0,
        .rx_unread_bufsz = 64,
        .callback_rx = NULL,
        .callback_rx_wanted_char = NULL,
        .callback_line_state_changed = NULL,
        .callback_line_coding_changed = NULL
    };
    
    ESP_ERROR_CHECK(tusb_cdcacm_init(&cdc_cfg));
}
