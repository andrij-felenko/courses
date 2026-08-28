// Шина й помічники — з попередніх прикладів. Тут у регістрах видно те саме
// правило: труба 1 має РЕГІСТР НА П'ЯТЬ байтів, труби 2–5 — на ОДИН.
static const uint8_t addr1[5] = { 0xC2, 0xC2, 0xC2, 0xC2, 0xC2 };  // повна
static const uint8_t last2 = 0xC3;      // труба 2: лише свій останній байт
static const uint8_t last4 = 0xC5;      // труба 4: лише свій останній байт

static void nrf_rx3_init(void) {
  nrf_wr1(0x06, 0x22);                  // RF_SETUP: 250 кбіт/с + PA_LOW
  nrf_wr1(0x05, 76);                    // RF_CH: канал 76
  nrf_wr(0x0B, addr1, 5);               // RX_ADDR_P1 — задає спільні старші 4 байти
  nrf_wr(0x0C, &last2, 1);              // RX_ADDR_P2 — регістр ОДНОБАЙТОВИЙ
  nrf_wr(0x0E, &last4, 1);              // RX_ADDR_P4 — теж один байт
  nrf_wr1(0x02, 0x02 | 0x04 | 0x10);    // EN_RXADDR: труби 1, 2 і 4
  nrf_wr1(0x12, 32); nrf_wr1(0x13, 32); nrf_wr1(0x15, 32);  // RX_PW_P1/P2/P4
  nrf_wr1(0x00, 0x0F);                  // CONFIG: PRIM_RX = 1 → приймач
  vTaskDelay(pdMS_TO_TICKS(5));
  gpio_set_level(PIN_CE, 1);
}

void app_main(void) {
  nrf_bus_init();
  nrf_rx3_init();
  while (1) {
    uint8_t nop = 0xFF, st = nrf_xfer(&nop, NULL, 1);
    if (st & 0x40) {                              // RX_DR — щось прийшло
      uint8_t pipe = (st >> 1) & 0x07;            // номер труби живе в самому STATUS
      uint8_t tx[33] = { 0x61 }, rx[33] = {0};
      nrf_xfer(tx, rx, 33);
      nrf_wr1(0x07, 0x40);
      ESP_LOGI(TAG, "труба %u: %s", pipe, (char *)&rx[1]);
    }
    vTaskDelay(pdMS_TO_TICKS(2));
  }
}
