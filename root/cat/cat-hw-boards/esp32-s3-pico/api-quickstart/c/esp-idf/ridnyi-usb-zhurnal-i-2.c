#include "tinyusb.h"
#include "class/hid/hid_device.h"

// дескриптор звіту — те, чим пристрій оголошує себе клавіатурою.
// В Arduino його ховає бібліотека; тут ми віддаємо його самі.
static const uint8_t kbd_desc[] = { TUD_HID_REPORT_DESC_KEYBOARD() };

const uint8_t *tud_hid_descriptor_report_cb(uint8_t instance) { return kbd_desc; }

void app_main(void) {
  const tinyusb_config_t tusb_cfg = { .external_phy = false };
  ESP_ERROR_CHECK(tinyusb_driver_install(&tusb_cfg));

  while (!tud_mounted()) vTaskDelay(pdMS_TO_TICKS(100));  // час хостові розпізнати пристрій

  uint8_t keys[6] = { HID_KEY_A };                  // натиснули «A»…
  tud_hid_keyboard_report(0, 0, keys);
  vTaskDelay(pdMS_TO_TICKS(20));
  tud_hid_keyboard_report(0, 0, NULL);              // …і відпустили
}
