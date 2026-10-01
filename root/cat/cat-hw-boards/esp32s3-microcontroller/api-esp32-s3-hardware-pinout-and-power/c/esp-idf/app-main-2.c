#include <stdio.h>
#include "esp_efuse.h"
#include "driver/gpio.h"

void app_main(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_NUM_0),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    int gpio0_level = gpio_get_level(GPIO_NUM_0);

    bool is_vdd_spi_forced = esp_efuse_read_field_bit(ESP_EFUSE_VDD_SPI_FORCE);

    printf("Стан GPIO0 під час старту: %d\n", gpio0_level);
    printf("Статус примусової фіксації VDD_SPI в eFuse: %s\n", 
           is_vdd_spi_forced ? "Заблоковано" : "Автовизначення");
}
