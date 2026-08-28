#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "esp_system.h"
#include "esp_sleep.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_rom_crc.h"

#define PIN_NUM_MISO  19
#define PIN_NUM_MOSI  23
#define PIN_NUM_CLK   18
#define PIN_NUM_CS    5

#define TEST_PACKET_SIZE  256
#define TEST_ITERATIONS   10000

typedef struct {
    uint32_t total_packets;
    uint32_t crc_errors;
    uint32_t timeout_errors;
} BusAuditStats;

static const char *TAG = "BUS_AUDIT";
static spi_device_handle_t spi_handle;

static void init_spi_test_bus(int clock_speed_hz) {
    spi_bus_config_t buscfg = {
        .miso_io_num = PIN_NUM_MISO,
        .mosi_io_num = PIN_NUM_MOSI,
        .sclk_io_num = PIN_NUM_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = TEST_PACKET_SIZE + 8
    };

    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = clock_speed_hz,
        .mode = 0,
        .spics_io_num = PIN_NUM_CS,
        .queue_size = 1,
        .flags = SPI_DEVICE_NO_DUMMY
    };

    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO));
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &devcfg, &spi_handle));
}

static BusAuditStats run_spi_integrity_test(void) {
    BusAuditStats stats = {0};
    uint8_t tx_buf[TEST_PACKET_SIZE];
    uint8_t rx_buf[TEST_PACKET_SIZE];

    for (uint32_t i = 0; i < TEST_ITERATIONS; i++) {
        for (size_t b = 0; b < TEST_PACKET_SIZE - 4; b++) {
            tx_buf[b] = (uint8_t)(i + b);
        }

        uint32_t crc = esp_rom_crc32_le(0, tx_buf, TEST_PACKET_SIZE - 4);
        memcpy(&tx_buf[TEST_PACKET_SIZE - 4], &crc, sizeof(crc));
        memset(rx_buf, 0, sizeof(rx_buf));

        spi_transaction_t t;
        memset(&t, 0, sizeof(t));
        t.length = TEST_PACKET_SIZE * 8;
        t.tx_buffer = tx_buf;
        t.rx_buffer = rx_buf;

        esp_err_t ret = spi_device_transmit(spi_handle, &t);
        stats.total_packets++;

        if (ret != ESP_OK) {
            stats.timeout_errors++;
            continue;
        }

        uint32_t rx_crc = esp_rom_crc32_le(0, rx_buf, TEST_PACKET_SIZE - 4);
        uint32_t expected_crc;
        memcpy(&expected_crc, &rx_buf[TEST_PACKET_SIZE - 4], sizeof(expected_crc));

        if (rx_crc != expected_crc || memcmp(tx_buf, rx_buf, TEST_PACKET_SIZE - 4) != 0) {
            stats.crc_errors++;
        }
    }

    return stats;
}

static void prepare_and_enter_deep_sleep(uint64_t sleep_duration_us) {
    spi_bus_remove_device(spi_handle);
    spi_bus_free(SPI2_HOST);

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_NUM_MISO) | (1ULL << PIN_NUM_MOSI) |
                        (1ULL << PIN_NUM_CLK)  | (1ULL << PIN_NUM_CS),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    ESP_LOGI(TAG, "Всі піни ізольовано в Hi-Z. Перехід у Deep Sleep на %llu с", sleep_duration_us / 1000000ULL);
    esp_sleep_enable_timer_wakeup(sleep_duration_us);
    esp_deep_sleep_start();
}

void app_main(void) {
    ESP_LOGI(TAG, "--- Старт тесту цілісності шини SPI (20 МГц) ---");
    init_spi_test_bus(20000000);

    BusAuditStats stats = run_spi_integrity_test();
    ESP_LOGI(TAG, "Всього пакетів: %lu | Помилок CRC: %lu | Таймаутів: %lu",
             stats.total_packets, stats.crc_errors, stats.timeout_errors);

    prepare_and_enter_deep_sleep(30 * 1000000ULL);
}
