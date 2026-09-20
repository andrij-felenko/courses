#include "cc1101.h"
#include "spi_hal.h"
#include <stdio.h>

// Заглушки апаратного рівня (HAL) для демонстрації
void spi_hal_init(void) {}
uint8_t spi_hal_transfer(uint8_t data) { return 0; }
void spi_hal_cs_low(void) {}
void spi_hal_cs_high(void) {}
bool spi_hal_is_miso_low(void) { return true; }
bool spi_hal_get_gdo0(void) { return false; }

int main(void) {
    cc1101_t radio;
    cc1101_init(&radio);
    
    uint8_t packet[] = {0xDE, 0xAD, 0xBE, 0xEF};
    if (cc1101_send(&radio, packet, sizeof(packet))) {
        printf("Packet queued for transmission.\n");
    }
    
    // Неблокуючий суперцикл
    while (1) {
        // Оновлення стану трансивера
        cc1101_update(&radio);
        
        // Читання при наявності даних
        uint8_t rx_data[64];
        uint8_t rx_len;
        if (cc1101_receive(&radio, rx_data, &rx_len)) {
            printf("Received %d bytes.\n", rx_len);
        }
        
        // Інші завдання можуть виконуватися без затримок
        break; // У прикладі виходимо з циклу відразу
    }
    
    return 0;
}
