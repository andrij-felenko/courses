#include <cstdio>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "usb/usb_host.h"
#include "esp_log.h"

namespace {
    constexpr char TAG[] = "USB_HOST_CPP";

    void usbHostDaemonTask(void *param) {
        while (true) {
            uint32_t eventFlags = 0;
            usb_host_lib_handle_events(portMAX_DELAY, &eventFlags);
        }
    }

    void usbClientEventCallback(const usb_host_client_event_msg_t *eventMsg, void *arg) {
        if (eventMsg->event == USB_HOST_CLIENT_EVENT_NEW_DEV) {
            ESP_LOGI(TAG, "Пристрій підключено до шини, адреса: %d", eventMsg->new_dev.address);
        } else if (eventMsg->event == USB_HOST_CLIENT_EVENT_DEV_GONE) {
            ESP_LOGW(TAG, "Пристрій відключено від шини.");
        }
    }
}

extern "C" void app_main(void) {
    const usb_host_config_t hostConfig = {
        .skip_phy_setup = false,
        .intr_flags = ESP_INTR_FLAG_LEVEL1,
    };
    ESP_ERROR_CHECK(usb_host_install(&hostConfig));

    xTaskCreate(usbHostDaemonTask, "usb_daemon_cpp", 4096, nullptr, 5, nullptr);

    usb_host_client_config_t clientConfig = {
        .is_async = true,
        .max_num_event_msg = 5,
        .async = {
            .client_event_cb = usbClientEventCallback,
            .callback_arg = nullptr
        }
    };
    usb_host_client_handle_t clientHandle = nullptr;
    ESP_ERROR_CHECK(usb_host_client_register(&clientConfig, &clientHandle));

    ESP_LOGI(TAG, "Стек TinyUSB Host ініціалізовано у C++ середовищі.");
}
