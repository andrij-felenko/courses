#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "usb/usb_host.h"
#include "esp_log.h"

static const char *TAG = "USB_HOST";

// Зворотний виклик для обробки подій периферійного пристрою
static void _usb_host_event_callback(const usb_host_client_event_msg_t *event_msg, void *arg) {
    if (event_msg->event == USB_HOST_CLIENT_EVENT_NEW_DEV) {
        ESP_LOGI(TAG, "Виявлено новий USB-пристрій, адреса: %d", event_msg->new_dev.address);
    } else if (event_msg->event == USB_HOST_CLIENT_EVENT_DEV_GONE) {
        ESP_LOGW(TAG, "Пристрій відключено, хендл: %p", event_msg->dev_gone.dev_hdl);
    }
}

// Фонова задача обробки подій стека TinyUSB
static void _usb_host_task(void *param) {
    while (1) {
        uint32_t event_flags;
        usb_host_lib_handle_events(portMAX_DELAY, &event_flags);
    }
}

void app_main(void) {
    // Конфігурація та встановлення драйвера USB Host
    const usb_host_config_t host_config = {
        .skip_phy_setup = false,
        .intr_flags = ESP_INTR_FLAG_LEVEL1,
    };
    ESP_ERROR_CHECK(usb_host_install(&host_config));

    // Створення фонової задачи обробки подій
    xTaskCreate(_usb_host_task, "usb_host_daemon", 4096, NULL, 5, NULL);

    // Реєстрація клієнта для отримання повідомлень про підключення
    usb_host_client_config_t client_config = {
        .is_async = true,
        .max_num_event_msg = 5,
        .async.client_event_cb = _usb_host_event_callback,
        .async.callback_arg = NULL,
    };
    usb_host_client_handle_t client_hdl;
    ESP_ERROR_CHECK(usb_host_client_register(&client_config, &client_hdl));

    ESP_LOGI(TAG, "Стек TinyUSB Host успішно ініціалізовано.");
}
