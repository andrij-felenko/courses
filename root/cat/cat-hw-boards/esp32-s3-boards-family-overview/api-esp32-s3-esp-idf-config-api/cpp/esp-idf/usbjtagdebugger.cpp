#include "esp_log.h"
#include "driver/usb_serial_jtag.h"

class UsbJtagDebugger {
public:
    static bool is_host_connected() {
        return usb_serial_jtag_is_connected();
    }

    static void log_status() {
        if (is_host_connected()) {
            ESP_LOGI("USB_DBG", "Термінал OpenOCD/CDC активний");
        }
    }
};
