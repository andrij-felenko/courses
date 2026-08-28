#include "driver/spi_master.h"
#include "esp_log.h"
#include "esp_rom_sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "rfid";
static spi_device_handle_t rc;      // читач — звичайний SPI-пристрій

// адресний байт MFRC522: (reg<<1)&0x7E; старший біт 1 — читання, 0 — запис
static void wr(uint8_t reg, uint8_t v) {
    uint8_t tx[2] = { (uint8_t)((reg << 1) & 0x7E), v };
    spi_transaction_t t = { .length = 16, .tx_buffer = tx };
    spi_device_polling_transmit(rc, &t);
}
static uint8_t rd(uint8_t reg) {
    uint8_t tx[2] = { (uint8_t)(0x80 | ((reg << 1) & 0x7E)), 0 }, rx[2] = { 0 };
    spi_transaction_t t = { .length = 16, .tx_buffer = tx, .rx_buffer = rx };
    spi_device_polling_transmit(rc, &t);
    return rx[1];
}

// один обмін із міткою: байти у FIFO → команда Transceive → відповідь із FIFO
static int transceive(const uint8_t *tx, int n, uint8_t lastbits, uint8_t *rx, int max) {
    wr(0x01, 0x00); wr(0x04, 0x7F); wr(0x0A, 0x80);  // Idle, скинути IRQ, чистити FIFO
    for (int i = 0; i < n; i++) wr(0x09, tx[i]);     // FIFODataReg
    wr(0x01, 0x0C);                                  // CommandReg = Transceive
    wr(0x0D, 0x80 | lastbits);                       // BitFramingReg: StartSend
    for (int i = 0; i < 40 && !(rd(0x04) & 0x30); i++) esp_rom_delay_us(500);
    wr(0x0D, 0x00);
    int len = rd(0x0A);                              // скільки байтів прийшло у FIFO
    if (len > max) len = max;
    for (int i = 0; i < len; i++) rx[i] = rd(0x09);
    return len;
}

static void pcd_init(void) {                         // те, що робить PCD_Init()
    wr(0x01, 0x0F); vTaskDelay(pdMS_TO_TICKS(50));   // SoftReset
    wr(0x2A, 0x8D); wr(0x2B, 0x3E); wr(0x2D, 30); wr(0x2C, 0);  // таймер ~25 мс
    wr(0x15, 0x40);                                  // TxASKReg: 100 % ASK
    wr(0x11, 0x3D);                                  // ModeReg: преднастройка CRC
    wr(0x14, rd(0x14) | 0x03);                       // TxControlReg: увімкнути антену
}

void app_main(void) {
    spi_bus_config_t bus = { .mosi_io_num = 23, .miso_io_num = 19, .sclk_io_num = 18,
                             .quadwp_io_num = -1, .quadhd_io_num = -1 };
    spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO);
    spi_device_interface_config_t dev = { .clock_speed_hz = 4 * 1000 * 1000,
                                          .mode = 0, .spics_io_num = 5, .queue_size = 1 };
    spi_bus_add_device(SPI2_HOST, &dev, &rc);
    pcd_init();

    while (1) {
        uint8_t reqa = 0x26, atqa[2], uid[5];
        if (transceive(&reqa, 1, 7, atqa, 2) == 2) {        // REQA — кадр завдовжки 7 біт
            uint8_t anti[2] = { 0x93, 0x20 };               // антиколізія, каскад 1
            if (transceive(anti, 2, 0, uid, 5) == 5)        // 4 байти UID + байт BCC
                ESP_LOGI(TAG, "UID: %02X %02X %02X %02X", uid[0], uid[1], uid[2], uid[3]);
        }
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}
