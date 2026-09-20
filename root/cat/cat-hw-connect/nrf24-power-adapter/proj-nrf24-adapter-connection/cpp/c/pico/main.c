#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/spi.h"

#define NRF_CSN_PIN 17
#define NRF_CE_PIN  16

void nrf24_init() {
    spi_init(spi0, 1000 * 1000); // SPI 1 MHz
    gpio_set_function(PICO_DEFAULT_SPI_RX_PIN, GPIO_FUNC_SPI);
    gpio_set_function(PICO_DEFAULT_SPI_SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(PICO_DEFAULT_SPI_TX_PIN, GPIO_FUNC_SPI);
    
    gpio_init(NRF_CSN_PIN);
    gpio_set_dir(NRF_CSN_PIN, GPIO_OUT);
    gpio_put(NRF_CSN_PIN, 1);
    
    gpio_init(NRF_CE_PIN);
    gpio_set_dir(NRF_CE_PIN, GPIO_OUT);
    gpio_put(NRF_CE_PIN, 0);
}

uint8_t nrf24_read_status() {
    uint8_t cmd = 0xFF; // NOP
    uint8_t status = 0;
    
    gpio_put(NRF_CSN_PIN, 0);
    spi_write_read_blocking(spi0, &cmd, &status, 1);
    gpio_put(NRF_CSN_PIN, 1);
    
    return status;
}

int main() {
    stdio_init_all();
    nrf24_init();
    
    while (true) {
        uint8_t status = nrf24_read_status();
        printf("nRF24L01 STATUS: 0x%02X\n", status);
        
        if (status == 0x0E) {
            printf("Живлення стабільне, зв'язок SPI встановлено.\n");
        } else if (status == 0x00 || status == 0xFF) {
            printf("Помилка зв'язку.\n");
        }
        
        sleep_ms(2000);
    }
}
