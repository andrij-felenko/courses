// ESP-IDF: готового драйвера nRF24 в SDK нема — говоримо по spi_master,
// а ті самі регістри пишемо самі. CE — звичайний вихід GPIO.
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_rom_sys.h"
#include <string.h>

#define PIN_CE   4              // «увімкнути радіо»
#define PIN_CSN  5              // вибір кристала — веде сам драйвер SPI
static spi_device_handle_t nrf;

static void nrf_wr(uint8_t reg, const uint8_t *v, size_t n) {   // W_REGISTER = 0x20|reg
    uint8_t tx[6] = { (uint8_t)(0x20 | reg) };
    memcpy(tx + 1, v, n);
    spi_transaction_t t = { .length = 8 * (n + 1), .tx_buffer = tx };
    ESP_ERROR_CHECK(spi_device_polling_transmit(nrf, &t));
}

void nrf_begin(void) {
    spi_bus_config_t bus = { .mosi_io_num = 23, .miso_io_num = 19, .sclk_io_num = 18,
                             .quadwp_io_num = -1, .quadhd_io_num = -1 };
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO));
    spi_device_interface_config_t dev = { .clock_speed_hz = 8 * 1000 * 1000, .mode = 0,
                                          .spics_io_num = PIN_CSN, .queue_size = 4 };
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &dev, &nrf));

    gpio_config_t ce = { .pin_bit_mask = 1ULL << PIN_CE, .mode = GPIO_MODE_OUTPUT };
    ESP_ERROR_CHECK(gpio_config(&ce));
    gpio_set_level(PIN_CE, 0);                       // радіо поки спить

    uint8_t ch = 76, rf = 0x22, cfg = 0x0A;          // канал 76 · 250 кбіт/с · потужність LOW
    const uint8_t addr[5] = { 'n','o','d','e','1' }; // 5-байтова адреса «труби»
    nrf_wr(0x05, &ch, 1);                            // RF_CH — має збігатися з іншим кінцем
    nrf_wr(0x06, &rf, 1);                            // RF_SETUP — швидкість і потужність
    nrf_wr(0x10, addr, 5);                           // TX_ADDR
    nrf_wr(0x0A, addr, 5);                           // RX_ADDR_P0 — інакше не приймемо авто-ACK
    nrf_wr(0x00, &cfg, 1);                           // CONFIG: PWR_UP + CRC, режим передавача
}

void nrf_send(const void *data, size_t n) {          // n ≤ 32
    uint8_t tx[33] = { 0xA0 };                       // W_TX_PAYLOAD
    memcpy(tx + 1, data, n);
    spi_transaction_t t = { .length = 8 * (n + 1), .tx_buffer = tx };
    ESP_ERROR_CHECK(spi_device_polling_transmit(nrf, &t));

    gpio_set_level(PIN_CE, 1);                       // імпульс CE — «жени в ефір»
    esp_rom_delay_us(15);                            // за даташитом треба ≥10 мкс
    gpio_set_level(PIN_CE, 0);
    // далі ESB сам шле й перепитує; підсумок — біти TX_DS / MAX_RT у регістрі STATUS
}
