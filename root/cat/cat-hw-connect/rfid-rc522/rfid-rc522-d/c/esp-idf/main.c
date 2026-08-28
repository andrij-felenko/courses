// Компонент rc522 з реєстру:  idf.py add-dependency "abobija/rc522"
// Опитування крутить сам драйвер у своїй задачі FreeRTOS і шле події.
#include "esp_log.h"
#include "rc522.h"
#include "driver/rc522_spi.h"

#define PIN_MISO 19
#define PIN_MOSI 23
#define PIN_SCLK 18
#define PIN_SDA   5            // «SDA» на платі — це chip-select
#define PIN_RST   4

static const char *TAG = "rc522";

static rc522_spi_config_t driver_config = {
    .host_id = SPI3_HOST,
    .bus_config = &(spi_bus_config_t){
        .miso_io_num = PIN_MISO,
        .mosi_io_num = PIN_MOSI,
        .sclk_io_num = PIN_SCLK,
    },
    .dev_config = { .spics_io_num = PIN_SDA },
    .rst_io_num = PIN_RST,
};

static rc522_driver_handle_t driver;
static rc522_handle_t scanner;

// подія від драйвера: мітка увійшла в поле й стала активною
static void on_picc(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    rc522_picc_state_changed_event_t *e = (rc522_picc_state_changed_event_t *)data;
    if (e->picc->state == RC522_PICC_STATE_ACTIVE) {
        rc522_picc_print(e->picc);          // друкує тип мітки та її UID
    }
}

void app_main(void)
{
    ESP_ERROR_CHECK(rc522_spi_create(&driver_config, &driver));
    ESP_ERROR_CHECK(rc522_driver_install(driver));

    rc522_config_t scanner_config = { .driver = driver };
    ESP_ERROR_CHECK(rc522_create(&scanner_config, &scanner));
    rc522_register_events(scanner, RC522_EVENT_PICC_STATE_CHANGED, on_picc, NULL);
    ESP_ERROR_CHECK(rc522_start(scanner));
    ESP_LOGI(TAG, "сканер запущено");
}
