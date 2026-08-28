#include "nvs_flash.h"
#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_gap_bt_api.h"
#include "esp_spp_api.h"

static void spp_cb(esp_spp_cb_event_t ev, esp_spp_cb_param_t *p) {
  switch (ev) {
  case ESP_SPP_INIT_EVT:                              // стек піднявся — оголошуємо службу
    esp_bt_gap_set_device_name("ESP32-robot");        // ім'я в списку Bluetooth
    esp_bt_gap_set_scan_mode(ESP_BT_CONNECTABLE, ESP_BT_GENERAL_DISCOVERABLE);
    esp_spp_start_srv(ESP_SPP_SEC_NONE, ESP_SPP_ROLE_SLAVE, 0, "SPP_SERVER");
    break;
  case ESP_SPP_DATA_IND_EVT:                          // прийшли байти з телефона
    esp_spp_write(p->data_ind.handle, p->data_ind.len, p->data_ind.data);  // ехо назад
    break;
  default: break;
  }
}

void app_main(void) {
  ESP_ERROR_CHECK(nvs_flash_init());                  // ключі спарювання лежать у NVS
  esp_bt_controller_config_t cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
  ESP_ERROR_CHECK(esp_bt_controller_init(&cfg));
  ESP_ERROR_CHECK(esp_bt_controller_enable(ESP_BT_MODE_CLASSIC_BT));
  ESP_ERROR_CHECK(esp_bluedroid_init());
  ESP_ERROR_CHECK(esp_bluedroid_enable());
  ESP_ERROR_CHECK(esp_spp_register_callback(spp_cb));
  ESP_ERROR_CHECK(esp_spp_init(ESP_SPP_MODE_CB));     // події замість блокуючого читання
}
