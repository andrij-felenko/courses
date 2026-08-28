// Шина й помічники nrf_xfer()/nrf_wr()/nrf_wr1() — ті самі, що в передавачі.
static const uint8_t addr[5] = { 0xE7, 0xE7, 0xE7, 0xE7, 0xE7 };  // ТА САМА адреса

static void nrf_rx_init(void) {
  nrf_wr1(0x06, 0x22);        // RF_SETUP: ті самі 250 кбіт/с + PA_LOW
  nrf_wr1(0x05, 76);          // RF_CH: той самий канал 76
  nrf_wr(0x0B, addr, 5);      // RX_ADDR_P1 — слухаємо цю адресу на трубі №1
  nrf_wr1(0x02, 0x02);        // EN_RXADDR: увімкнена лише труба 1
  nrf_wr1(0x12, 32);          // RX_PW_P1: скільки байтів у пакеті труби 1
  nrf_wr1(0x00, 0x0F);        // CONFIG: те саме, але PRIM_RX = 1 → приймач
  vTaskDelay(pdMS_TO_TICKS(5));
  gpio_set_level(PIN_CE, 1);  // піднятий CE і є «слухати» (= startListening)
}

void app_main(void) {
  nrf_bus_init();
  nrf_rx_init();
  while (1) {
    uint8_t nop = 0xFF;
    if (nrf_xfer(&nop, NULL, 1) & 0x40) {          // STATUS.RX_DR — у буфері є пакет
      uint8_t tx[33] = { 0x61 }, rx[33] = {0};     // 0x61 = R_RX_PAYLOAD
      nrf_xfer(tx, rx, 33);                        // rx[0] — це STATUS, дані з rx[1]
      nrf_wr1(0x07, 0x40);                         // зняти прапорець RX_DR
      ESP_LOGI(TAG, "прийшло: %s", (char *)&rx[1]);
    }
    vTaskDelay(pdMS_TO_TICKS(2));
  }
}
