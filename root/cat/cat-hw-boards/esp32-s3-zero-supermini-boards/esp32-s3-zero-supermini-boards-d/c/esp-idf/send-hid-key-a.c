#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "tinyusb.h"
#include "class/hid/hid_device.h"

// Звіт HID для клавіатури (натискання клавіші 'A')
static void send_hid_key_a(void)
{
    if (tud_mounted()) {
        uint8_t keycode[6] = { HID_KEY_A, 0, 0, 0, 0, 0 };
        // Відправка натискання клавіші
        tud_hid_keyboard_report(1, 0, keycode);
        vTaskDelay(pdMS_TO_TICKS(50));
        // Відпускання клавіші
        tud_hid_keyboard_report(1, 0, NULL);
    }
}

void app_main(void)
{
    // Налаштування конфігурації TinyUSB
    const tinyusb_config_t tos_cfg = {
        .device_descriptor = NULL,
        .string_descriptor = NULL,
        .external_phy = false,
    };
    
    ESP_ERROR_CHECK(tinyusb_driver_install(&tos_cfg));
    
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(5000));
        send_hid_key_a();
    }
}
