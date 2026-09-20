#ifndef RADIO_H
#define RADIO_H

#include <stdint.h>

// Оголошення структури радіомодуля
typedef struct {
    int spi_fd; // Файловий дескриптор для SPI
} RadioModule;

// Ініціалізація радіомодуля
int radio_init(RadioModule *radio, const char *spi_device);

// Зчитування рівня сигналу (RSSI)
int radio_get_rssi(RadioModule *radio, int8_t *rssi_out);

// Звільнення ресурсів
void radio_close(RadioModule *radio);

#endif // RADIO_H
