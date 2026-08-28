#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_rom_sys.h"                 // esp_rom_delay_us()
#include "esp_log.h"
#include <string.h>

#define PIN_SCK 18
#define PIN_MOSI 23
#define PIN_MISO 19
#define PIN_CSN  5                       // CSN веде сам SPI-драйвер
#define PIN_CE   4                       // CE — звичайний вихід, ним керуєте ви

static const char *TAG = "nrf24";
static spi_device_handle_t nrf;
static const uint8_t addr[5] = { 0xE7, 0xE7, 0xE7, 0xE7, 0xE7 };

// Одна SPI-транзакція. Перший байт відповіді чипа — ЗАВЖДИ регістр STATUS.
static uint8_t nrf_xfer(const uint8_t *tx, uint8_t *rx, size_t n) {
  uint8_t tmp[33];
  if (!rx) rx = tmp;
  spi_transaction_t t = { .length = n * 8, .tx_buffer = tx, .rx_buffer = rx };
  ESP_ERROR_CHECK(spi_device_polling_transmit(nrf, &t));
  return rx[0];
}
static void nrf_wr(uint8_t reg, const uint8_t *v, size_t n) {
  uint8_t tx[6] = { 0x20 | reg };        // 0x20 = W_REGISTER
  memcpy(tx + 1, v, n);
  nrf_xfer(tx, NULL, n + 1);
}
static void nrf_wr1(uint8_t reg, uint8_t v) { nrf_wr(reg, &v, 1); }

static void nrf_bus_init(void) {         // = SPI.begin() + перевірка звʼязку
  spi_bus_config_t bus = { .sclk_io_num = PIN_SCK, .mosi_io_num = PIN_MOSI,
                           .miso_io_num = PIN_MISO, .quadwp_io_num = -1, .quadhd_io_num = -1 };
  ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_DISABLED));
  spi_device_interface_config_t dev = { .mode = 0, .clock_speed_hz = 8 * 1000 * 1000,
                                        .spics_io_num = PIN_CSN, .queue_size = 1 };
  ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &dev, &nrf));
  gpio_set_direction(PIN_CE, GPIO_MODE_OUTPUT);
  gpio_set_level(PIN_CE, 0);
  vTaskDelay(pdMS_TO_TICKS(100));        // чипові треба ~100 мс після подачі живлення

  nrf_wr1(0x05, 76);                     // RF_CH — канал 76 (аналог setChannel)
  uint8_t back[2], q[2] = { 0x05, 0xFF };
  nrf_xfer(q, back, 2);                  // читаємо той самий регістр назад
  if (back[1] != 76) ESP_LOGE(TAG, "nRF24 не відповідає — живлення й розводка SPI");
}

static void nrf_tx_init(void) {
  nrf_wr1(0x06, 0x22);      // RF_SETUP: 250 кбіт/с + PA_LOW (= setDataRate + setPALevel)
  nrf_wr1(0x04, 0x5F);      // SETUP_RETR: 1500 мкс × 15 спроб авто-ACK
  nrf_wr(0x10, addr, 5);    // TX_ADDR    — куди пишемо      (= openWritingPipe)
  nrf_wr(0x0A, addr, 5);    // RX_ADDR_P0 — сюди прийде ACK  (труба 0 зайнята чипом)
  nrf_wr1(0x00, 0x0E);      // CONFIG: CRC 2 байти, PWR_UP, PRIM_RX=0 → передавач
  vTaskDelay(pdMS_TO_TICKS(5));         // 1.5 мс на вихід із power-down
}

// = radio.write(): віддати пакет і дочекатися вироку авто-ACK.
static bool nrf_send(const void *p, size_t n) {
  uint8_t tx[33] = { 0xA0 };            // 0xA0 = W_TX_PAYLOAD
  memcpy(tx + 1, p, n);
  nrf_xfer(tx, NULL, n + 1);
  gpio_set_level(PIN_CE, 1);            // імпульс CE — «відправляй»
  esp_rom_delay_us(15);
  gpio_set_level(PIN_CE, 0);

  uint8_t nop = 0xFF, st;
  do { st = nrf_xfer(&nop, NULL, 1); } while (!(st & 0x30));  // TX_DS або MAX_RT
  nrf_wr1(0x07, st & 0x30);             // скинути прапорці (записом ОДИНИЦЬ)
  return st & 0x20;                     // TX_DS → приймач підтвердив прийом
}

void app_main(void) {
  nrf_bus_init();
  nrf_tx_init();
  for (uint32_t counter = 0;; counter++) {
    char msg[32];
    int n = snprintf(msg, sizeof msg, "hello %u", (unsigned)counter);
    bool ok = nrf_send(msg, n + 1);     // + 1, щоб полетів і завершальний \0
    ESP_LOGI(TAG, "%s  %s", ok ? "ACK" : "нема ACK", msg);
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}
