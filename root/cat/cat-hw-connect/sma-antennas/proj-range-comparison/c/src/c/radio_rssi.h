#ifndef RADIO_RSSI_H
#define RADIO_RSSI_H

#include <stdint.h>
#include <stdbool.h>

// Типи частотних діапазонів
typedef enum {
    FREQ_433_MHZ,
    FREQ_2400_MHZ
} radio_frequency_t;

// Структура для збереження стану радіомодуля
typedef struct {
    radio_frequency_t freq;
    bool initialized;
    int hardware_id;
} radio_module_t;

// Ініціалізація радіомодуля
bool radio_init(radio_module_t* radio, radio_frequency_t freq, int hw_id);

// Зчитування поточного RSSI (в дБм)
// Повертає 0 у разі успіху, інакше код помилки
int radio_read_rssi(const radio_module_t* radio, int8_t* rssi_out);

// Звільнення ресурсів радіомодуля
void radio_close(radio_module_t* radio);

#endif // RADIO_RSSI_H
