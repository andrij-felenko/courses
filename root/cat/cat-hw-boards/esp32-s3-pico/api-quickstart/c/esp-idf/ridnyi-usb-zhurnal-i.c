#include "tinyusb.h"
#include "tusb_cdc_acm.h"
#include "esp_timer.h"

void app_main(void) {
  const tinyusb_config_t tusb_cfg = { .external_phy = false };
  ESP_ERROR_CHECK(tinyusb_driver_install(&tusb_cfg));

  const tinyusb_config_cdcacm_t acm_cfg = {
    .usb_dev = TINYUSB_USBDEV_0, .cdc_port = TINYUSB_CDC_ACM_0,
  };
  ESP_ERROR_CHECK(tusb_cdc_acm_init(&acm_cfg));

  // трохи чекаємо, поки хост відкриє порт
  for (int i = 0; i < 30 && !tud_cdc_connected(); i++) vTaskDelay(pdMS_TO_TICKS(100));

  while (1) {
    char line[48];
    int n = snprintf(line, sizeof line, "uptime: %lld c\n",
                     esp_timer_get_time() / 1000000);
    tinyusb_cdcacm_write_queue(TINYUSB_CDC_ACM_0, (uint8_t *)line, n);
    tinyusb_cdcacm_write_flush(TINYUSB_CDC_ACM_0, 0);
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}
