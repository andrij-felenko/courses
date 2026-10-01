#include "tinyusb.h"
#include "tusb_cdc_acm.h"
#include "esp_log.h"

class NativeUsbController {
private:
    static constexpr const char *TAG = "UsbController";

public:
    static esp_err_t initCdcMode() {
        const tinyusb_config_t tusb_cfg = {
            .device_descriptor = nullptr,
            .string_descriptor = nullptr,
            .external_phy = false,
            .configuration_descriptor = nullptr,
        };

        esp_err_t err = tinyusb_driver_install(&tusb_cfg);
        if (err != ESP_OK) return err;

        tinyusb_config_cdcacm_t cdc_cfg = {
            .usb_dev = TINYUSB_USBDEV_0,
            .cdc_port = TINYUSB_CDC_ACM_0,
            .rx_unread_buf_sz = 64,
            .callback_rx = nullptr,
            .callback_rx_wanted_char = nullptr,
            .callback_line_state_changed = nullptr,
            .callback_line_coding_changed = nullptr
        };

        return tusb_cdc_acm_init(&cdc_cfg);
    }
};
