#include "usb/usb_host.h"
#include "usb/hid_host.h"

/* Callback при підключенні нового пристрою */
static void device_connected_cb(usb_device_handle_t dev_hdl,
                                 const usb_config_desc_t *config_desc)
{
    /* host-стек уже провів енумерацію: адресу призначено,
       дескриптори прочитано, конфігурацію встановлено */
    hid_host_device_handle_t hid_dev;
    hid_host_install_device(dev_hdl, &hid_dev);
}

/* Callback при отриманні HID-звіту (interrupt-IN) */
static void hid_report_cb(hid_host_device_handle_t hid_dev,
                          const hid_report_t *report)
{
    if (report->usage == HID_USAGE_KEYBOARD) {
        uint8_t keycode = report->keyboard.keycode[0];
        if (keycode != 0) {
            /* keycode — код клавіші зі стандарту HID Usage Tables */
            printf("Key pressed: 0x%02X\n", keycode);
        }
    }
}

void app_main(void)
{
    /* 1. Підняти USB Host */
    usb_host_config_t host_config = { .intr_flags = ESP_INTR_FLAG_LEVEL1 };
    usb_host_install(&host_config);

    /* 2. Встановити клас-драйвер HID */
    hid_host_config_t hid_config = {
        .create_background_task = true,
        .task_priority = 5,
        .stack_size    = 4096,
        .callback      = hid_report_cb,
    };
    hid_host_install(&hid_config);

    /* 3. Головний цикл: крутимо події USB Host Library */
    while (1) {
        uint32_t event_flags;
        usb_host_lib_handle_events(portMAX_DELAY, &event_flags);
        if (event_flags & USB_HOST_LIB_EVENT_FLAGS_NO_CLIENTS) {
            usb_host_device_free_all();
        }
    }
}
